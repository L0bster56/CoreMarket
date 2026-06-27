import logging

from elasticsearch import AsyncElasticsearch

from src.backend.config import get_settings

logger = logging.getLogger("coremarket.search.client")

_client: AsyncElasticsearch | None = None


def get_es_client() -> AsyncElasticsearch:
    global _client
    if _client is None:
        settings = get_settings()
        _client = AsyncElasticsearch(
            hosts=[settings.ELASTICSEARCH_URL],
            retry_on_timeout=True,
            max_retries=3,
            request_timeout=10,
        )
        logger.info("elasticsearch_client_created", extra={"url": settings.ELASTICSEARCH_URL})
    return _client


async def close_es_client() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
        logger.info("elasticsearch_client_closed")


async def ping_es() -> bool:
    try:
        client = get_es_client()
        return await client.ping()
    except Exception:
        return False
