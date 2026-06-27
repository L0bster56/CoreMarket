import logging
from abc import ABC, abstractmethod

from elasticsearch import AsyncElasticsearch

logger = logging.getLogger("coremarket.search.indexes")


class BaseIndex(ABC):
    def __init__(self, es: AsyncElasticsearch, prefix: str) -> None:
        self.es = es
        self.prefix = prefix

    @property
    @abstractmethod
    def index_name(self) -> str: ...

    @property
    @abstractmethod
    def index_config(self) -> dict: ...

    async def ensure_index(self) -> None:
        exists = await self.es.indices.exists(index=self.index_name)
        if not exists:
            await self.es.indices.create(
                index=self.index_name,
                settings=self.index_config["settings"],
                mappings=self.index_config["mappings"],
            )
            logger.info("search_index_created", extra={"index": self.index_name})
        else:
            logger.debug("search_index_exists", extra={"index": self.index_name})

    async def delete_index(self) -> None:
        exists = await self.es.indices.exists(index=self.index_name)
        if exists:
            await self.es.indices.delete(index=self.index_name)
            logger.info("search_index_deleted", extra={"index": self.index_name})

    async def recreate_index(self) -> None:
        await self.delete_index()
        await self.ensure_index()
        logger.info("search_index_recreated", extra={"index": self.index_name})
