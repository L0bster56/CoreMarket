import asyncio
import logging
import time

from celery import Task

from src.backend.celery_app import celery_app

logger = logging.getLogger("coremarket.tasks.cleanup")


async def _cleanup_async() -> dict:
    """
    Placeholder for session/token cleanup logic.
    Extend here when refresh token table or session store is introduced.
    """
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from src.backend.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            # Cleanup soft-deleted comments older than 90 days as an example
            result = await session.execute(
                text(
                    "DELETE FROM comments "
                    "WHERE is_deleted = TRUE "
                    "AND updated_at < NOW() - INTERVAL '90 days'"
                )
            )
            await session.commit()
            return {"deleted_comments": result.rowcount}
    finally:
        await engine.dispose()


@celery_app.task(
    name="coremarket.tasks.cleanup_expired_sessions",
    bind=True,
    max_retries=2,
    default_retry_delay=300,
    acks_late=True,
)
def cleanup_expired_sessions(self: Task) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info(
        "task_started",
        extra={"task_id": task_id, "task_name": self.name},
    )

    try:
        result = asyncio.run(_cleanup_async())
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "status": "success",
                "duration_ms": duration_ms,
                **result,
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
                "duration_ms": duration_ms,
                "retry": self.request.retries,
            },
        )
        raise self.retry(exc=exc, countdown=300)
