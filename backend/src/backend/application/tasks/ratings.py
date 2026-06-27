import asyncio
import logging
import time

from celery import Task

from src.backend.celery_app import celery_app

logger = logging.getLogger("coremarket.tasks.ratings")


async def _recalculate_async(item_id: str) -> dict:
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from src.backend.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(
                text(
                    "SELECT AVG(score) AS avg_score, COUNT(*) AS total "
                    "FROM ratings WHERE item_id = :iid"
                ),
                {"iid": item_id},
            )
            row = result.fetchone()
            avg = round(float(row.avg_score), 2) if row.avg_score else 0.0
            total = row.total or 0

            # Update cached avg_rating on item if column exists.
            # Safe no-op if the column is not present (ignores error via try/except).
            try:
                await session.execute(
                    text(
                        "UPDATE items SET avg_rating = :avg WHERE id = :iid"
                    ),
                    {"avg": avg, "iid": item_id},
                )
                await session.commit()
            except Exception:
                await session.rollback()

            return {"avg_score": avg, "count": total}
    finally:
        await engine.dispose()


@celery_app.task(
    name="coremarket.tasks.recalculate_item_rating",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
)
def recalculate_item_rating(self: Task, item_id: str) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info(
        "task_started",
        extra={"task_id": task_id, "task_name": self.name, "item_id": item_id},
    )

    try:
        result = asyncio.run(_recalculate_async(item_id))
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "item_id": item_id,
                "avg_score": result["avg_score"],
                "count": result["count"],
                "status": "success",
                "duration_ms": duration_ms,
            },
        )
        return result

    except Exception as exc:
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.error(
            "task_failed",
            exc_info=exc,
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "item_id": item_id,
                "duration_ms": duration_ms,
                "retry": self.request.retries,
            },
        )
        raise self.retry(exc=exc, countdown=5 * (2 ** self.request.retries))
