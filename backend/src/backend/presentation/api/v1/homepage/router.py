"""
Homepage endpoint — serves precomputed Redis snapshot with DB fallback.

GET /api/v1/homepage
  - Primary path (< 5 ms): read snapshot from Redis, return immediately
  - Fallback path (slow): inline DB query if snapshot is missing / Redis down
  - On cache miss also triggers async snapshot refresh via Celery

The response includes a `source` field so front-end and monitoring can
distinguish cache hits from DB queries.
"""

import json
import logging
import time
from typing import Any

import redis.asyncio as aioredis
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.backend.config import get_settings
from src.backend.metrics import homepage_requests_total, homepage_snapshot_age_seconds

logger = logging.getLogger("coremarket.homepage")
router = APIRouter(prefix="/homepage", tags=["homepage"])


def _get_redis() -> aioredis.Redis:
    settings = get_settings()
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def _inline_query() -> dict[str, Any]:
    """Fallback: query DB directly when Redis snapshot is unavailable."""
    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    try:
        async with AsyncSession(engine) as session:
            featured = (await session.execute(
                text("""
                    SELECT id, title, short_description, category_id,
                           view_count, avg_rating, preview_image, created_at
                    FROM items WHERE is_published = TRUE
                    ORDER BY view_count DESC LIMIT 20
                """)
            )).fetchall()

            top_rated = (await session.execute(
                text("""
                    SELECT id, title, short_description, category_id,
                           view_count, avg_rating, preview_image, created_at
                    FROM items
                    WHERE is_published = TRUE AND avg_rating IS NOT NULL
                    ORDER BY avg_rating DESC LIMIT 10
                """)
            )).fetchall()

            categories = (await session.execute(
                text("""
                    SELECT c.id, c.name, c.slug, COUNT(i.id) AS item_count
                    FROM categories c
                    LEFT JOIN items i ON i.category_id = c.id AND i.is_published = TRUE
                    GROUP BY c.id, c.name, c.slug
                    ORDER BY item_count DESC
                """)
            )).fetchall()

            posts = (await session.execute(
                text("""
                    SELECT id, title, slug, cover_image_url, created_at, seo_description
                    FROM blog_posts WHERE status = 'published'
                    ORDER BY created_at DESC LIMIT 6
                """)
            )).fetchall()

            stats = (await session.execute(
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

    return {
        "computed_at": time.time(),
        "featured_items": [_row(r) for r in featured],
        "top_rated_items": [_row(r) for r in top_rated],
        "categories": [_row(r) for r in categories],
        "recent_posts": [_row(r) for r in posts],
        "stats": {
            "total_items": stats.items if stats else 0,
            "total_categories": stats.categories if stats else 0,
            "total_posts": stats.posts if stats else 0,
        },
    }


def _trigger_snapshot_refresh() -> None:
    """Fire-and-forget: ask Celery to rebuild the snapshot asap."""
    try:
        from src.backend.application.tasks.homepage import compute_homepage_snapshot
        compute_homepage_snapshot.apply_async(countdown=0)
    except Exception:
        pass


@router.get("")
async def homepage() -> JSONResponse:
    """
    Return precomputed homepage payload.

    Response fields:
    - source         : "cache" | "db_fallback"
    - computed_at    : Unix timestamp of when the snapshot was built
    - featured_items : top 20 items by view_count
    - top_rated_items: top 10 items by avg_rating
    - categories     : all categories with item counts
    - recent_posts   : 6 latest published blog posts
    - stats          : aggregate counts
    """
    settings = get_settings()
    redis_client = _get_redis()
    snapshot: dict[str, Any] | None = None

    try:
        raw = await redis_client.get(settings.HOMEPAGE_SNAPSHOT_KEY)
        if raw:
            snapshot = json.loads(raw)
            computed_at = snapshot.get("computed_at", 0)
            age = time.time() - computed_at
            homepage_snapshot_age_seconds.set(age)
            homepage_requests_total.labels(source="cache_hit").inc()
            snapshot["source"] = "cache"
            return JSONResponse(content=snapshot)
    except Exception as exc:
        logger.warning("homepage_redis_error", exc_info=exc)
    finally:
        try:
            await redis_client.aclose()
        except Exception:
            pass

    # Snapshot missing — trigger async rebuild and serve from DB
    homepage_requests_total.labels(source="cache_miss").inc()
    _trigger_snapshot_refresh()

    try:
        snapshot = await _inline_query()
        homepage_requests_total.labels(source="fallback").inc()
        snapshot["source"] = "db_fallback"
        return JSONResponse(content=snapshot)
    except Exception as exc:
        logger.error("homepage_inline_query_failed", exc_info=exc)
        return JSONResponse(
            status_code=503,
            content={"detail": "Homepage data temporarily unavailable"},
        )
