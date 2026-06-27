"""
Homepage snapshot precomputation task.

Runs every 5 minutes via Celery Beat.  Queries the DB for:
  - top 20 items by view_count   (featured)
  - top 10 items by avg_rating   (top_rated)
  - all categories               (navigation)
  - 6 latest published blog posts

Stores the result as JSON in Redis under HOMEPAGE_SNAPSHOT_KEY.
The /api/v1/homepage endpoint reads this key and serves the snapshot in <5 ms
with zero DB queries on the hot path.

Fallback: if Redis is unavailable the task logs a warning and the API
endpoint falls back to an inline DB query.
"""

import asyncio
import json
import logging
import time

from celery import Task

from src.backend.celery_app import celery_app

logger = logging.getLogger("coremarket.tasks.homepage")


async def _build_snapshot() -> dict:
    import redis.asyncio as aioredis
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from src.backend.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            # Top items by view_count
            featured_rows = (await session.execute(
                text("""
                    SELECT id, title, short_description, category_id,
                           view_count, avg_rating, preview_image, created_at
                    FROM items
                    WHERE is_published = TRUE
                    ORDER BY view_count DESC
                    LIMIT 20
                """)
            )).fetchall()

            # Top rated items (need at least one rating)
            top_rated_rows = (await session.execute(
                text("""
                    SELECT id, title, short_description, category_id,
                           view_count, avg_rating, preview_image, created_at
                    FROM items
                    WHERE is_published = TRUE AND avg_rating IS NOT NULL
                    ORDER BY avg_rating DESC, view_count DESC
                    LIMIT 10
                """)
            )).fetchall()

            # All categories with item counts
            category_rows = (await session.execute(
                text("""
                    SELECT c.id, c.name, c.slug, COUNT(i.id) AS item_count
                    FROM categories c
                    LEFT JOIN items i ON i.category_id = c.id AND i.is_published = TRUE
                    GROUP BY c.id, c.name, c.slug
                    ORDER BY item_count DESC
                """)
            )).fetchall()

            # Recent blog posts
            blog_rows = (await session.execute(
                text("""
                    SELECT id, title, slug, cover_image_url, created_at,
                           seo_description
                    FROM blog_posts
                    WHERE status = 'published'
                    ORDER BY created_at DESC
                    LIMIT 6
                """)
            )).fetchall()

            # Aggregate stats
            stats_row = (await session.execute(
                text("""
                    SELECT
                        (SELECT COUNT(*) FROM items WHERE is_published = TRUE) AS items,
                        (SELECT COUNT(*) FROM categories) AS categories,
                        (SELECT COUNT(*) FROM blog_posts WHERE status = 'published') AS posts
                """)
            )).fetchone()

    finally:
        await engine.dispose()

    def _row(r: object) -> dict:
        return dict(r._mapping)

    snapshot = {
        "computed_at": time.time(),
        "featured_items": [_row(r) for r in featured_rows],
        "top_rated_items": [_row(r) for r in top_rated_rows],
        "categories": [_row(r) for r in category_rows],
        "recent_posts": [_row(r) for r in blog_rows],
        "stats": {
            "total_items": stats_row.items if stats_row else 0,
            "total_categories": stats_row.categories if stats_row else 0,
            "total_posts": stats_row.posts if stats_row else 0,
        },
    }

    # Store in Redis
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        await redis_client.set(
            settings.HOMEPAGE_SNAPSHOT_KEY,
            json.dumps(snapshot, default=str),
            ex=settings.HOMEPAGE_SNAPSHOT_TTL,
        )
    finally:
        await redis_client.aclose()

    return snapshot


@celery_app.task(
    name="coremarket.tasks.compute_homepage_snapshot",
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    queue="homepage",
)
def compute_homepage_snapshot(self: Task) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info("task_started", extra={"task_id": task_id, "task_name": self.name})

    try:
        snapshot = asyncio.run(_build_snapshot())
        duration_ms = int((time.monotonic() - start) * 1000)

        # Update Prometheus gauge so Grafana can show snapshot freshness
        try:
            from src.backend.metrics import homepage_snapshot_age_seconds
            homepage_snapshot_age_seconds.set(0)
        except Exception:
            pass

        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "status": "success",
                "duration_ms": duration_ms,
                "featured_items": len(snapshot.get("featured_items", [])),
                "categories": len(snapshot.get("categories", [])),
            },
        )
        return {"status": "ok", "duration_ms": duration_ms}

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
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
