"""
Full Elasticsearch reindex CLI.

Usage (inside Docker backend container):
    python -m src.backend.scripts.reindex
    python -m src.backend.scripts.reindex --drop   # recreate index before indexing
"""
import argparse
import asyncio
import logging
import sys
import time

logger = logging.getLogger("coremarket.scripts.reindex")


async def run(drop: bool = False) -> int:
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

    from src.backend.config import get_settings
    from src.backend.logging_setup import setup_logging
    from src.backend.search.infrastructure.elasticsearch.client import get_es_client
    from src.backend.search.infrastructure.elasticsearch.indexes.items import ItemIndex
    from src.backend.search.infrastructure.elasticsearch.sync.item_sync import bulk_reindex

    settings = get_settings()
    setup_logging(level=settings.LOG_LEVEL, fmt=settings.LOG_FORMAT)

    if not settings.SEARCH_ENABLED:
        logger.error("reindex_aborted: SEARCH_ENABLED=false")
        return 1

    es = get_es_client()
    item_index = ItemIndex(es, settings.ELASTICSEARCH_INDEX_PREFIX)

    logger.info(
        "reindex_start",
        extra={"index": item_index.index_name, "drop": drop, "es_url": settings.ELASTICSEARCH_URL},
    )

    if drop:
        logger.info("reindex_dropping_index", extra={"index": item_index.index_name})
        await item_index.recreate_index()
    else:
        await item_index.ensure_index()

    engine = create_async_engine(settings.ASYNC_DATABASE_URL, pool_pre_ping=True)
    start = time.monotonic()
    try:
        async with AsyncSession(engine) as session:
            indexed = await bulk_reindex(
                session=session,
                es=es,
                index_name=item_index.index_name,
            )
    finally:
        await engine.dispose()
        await es.close()

    duration_s = round(time.monotonic() - start, 2)
    logger.info(
        "reindex_complete",
        extra={"indexed": indexed, "duration_s": duration_s, "index": item_index.index_name},
    )
    print(f"[reindex] Done: {indexed} items indexed in {duration_s}s → {item_index.index_name}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Reindex all items to Elasticsearch")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop and recreate the index before reindexing",
    )
    args = parser.parse_args()
    exit_code = asyncio.run(run(drop=args.drop))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
