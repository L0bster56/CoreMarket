import asyncio
import logging
import time
from uuid import UUID

from celery import Task

from src.backend.celery_app import celery_app

logger = logging.getLogger("coremarket.tasks.search_sync")


async def _index_item_async(item_id: str) -> dict:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from src.backend.config import get_settings
    from src.backend.search.infrastructure.elasticsearch.client import get_es_client
    from src.backend.search.infrastructure.elasticsearch.indexes.items import ItemIndex
    from src.backend.search.infrastructure.elasticsearch.sync.item_sync import index_item

    settings = get_settings()
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    try:
        es = get_es_client()
        item_index = ItemIndex(es, settings.ELASTICSEARCH_INDEX_PREFIX)
        async with AsyncSession(engine) as session:
            indexed = await index_item(
                item_id=UUID(item_id),
                session=session,
                es=es,
                index_name=item_index.index_name,
            )
        return {"item_id": item_id, "indexed": indexed}
    finally:
        await engine.dispose()


async def _delete_item_async(item_id: str) -> dict:
    from src.backend.config import get_settings
    from src.backend.search.infrastructure.elasticsearch.client import get_es_client
    from src.backend.search.infrastructure.elasticsearch.indexes.items import ItemIndex
    from src.backend.search.infrastructure.elasticsearch.sync.item_sync import delete_item_from_index

    settings = get_settings()
    es = get_es_client()
    item_index = ItemIndex(es, settings.ELASTICSEARCH_INDEX_PREFIX)
    await delete_item_from_index(item_id=item_id, es=es, index_name=item_index.index_name)
    return {"item_id": item_id, "deleted": True}


@celery_app.task(
    name="coremarket.tasks.index_item",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def index_item_task(self: Task, item_id: str) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info(
        "task_started",
        extra={"task_id": task_id, "task_name": self.name, "item_id": item_id},
    )

    try:
        from src.backend.config import get_settings

        if not get_settings().SEARCH_ENABLED:
            return {"skipped": True, "reason": "search_disabled"}

        result = asyncio.run(_index_item_async(item_id))
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "item_id": item_id,
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
                "item_id": item_id,
                "duration_ms": duration_ms,
                "retry": self.request.retries,
            },
        )
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))


@celery_app.task(
    name="coremarket.tasks.delete_item_from_index",
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
)
def delete_item_task(self: Task, item_id: str) -> dict:
    start = time.monotonic()
    task_id = self.request.id

    logger.info(
        "task_started",
        extra={"task_id": task_id, "task_name": self.name, "item_id": item_id},
    )

    try:
        from src.backend.config import get_settings

        if not get_settings().SEARCH_ENABLED:
            return {"skipped": True, "reason": "search_disabled"}

        result = asyncio.run(_delete_item_async(item_id))
        duration_ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "task_completed",
            extra={
                "task_id": task_id,
                "task_name": self.name,
                "item_id": item_id,
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
        raise self.retry(exc=exc, countdown=10 * (2 ** self.request.retries))
