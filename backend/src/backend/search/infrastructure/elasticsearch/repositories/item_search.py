import logging

from elasticsearch import AsyncElasticsearch

from src.backend.search.domain.models import SearchHit, SearchResponse, SuggestionItem, SuggestionsResponse
from src.backend.search.domain.value_objects import ItemSearchParams
from src.backend.search.infrastructure.elasticsearch.queries.items import (
    build_autocomplete_query,
    build_item_search_query,
)

logger = logging.getLogger("coremarket.search.repository")


class ESItemSearchRepository:
    """Elasticsearch implementation of SearchRepositoryProtocol and AutocompleteRepositoryProtocol."""

    def __init__(self, es: AsyncElasticsearch, index_name: str) -> None:
        self._es = es
        self._index = index_name

    async def search(self, params: ItemSearchParams) -> SearchResponse:
        body = build_item_search_query(params)

        logger.debug(
            "search_query",
            extra={
                "query": params.search,
                "category_id": str(params.category_id) if params.category_id else None,
                "tags": params.tags,
                "sort_by": params.sort_by,
            },
        )

        response = await self._es.search(
            index=self._index,
            query=body["query"],
            sort=body["sort"],
            from_=body["from"],
            size=body["size"],
            source_excludes=["description"],
        )

        took_ms: int = response.get("took", 0)
        total: int = response["hits"]["total"]["value"]
        raw_hits = response["hits"]["hits"]

        hits = [_hit_to_model(h) for h in raw_hits]

        page_size = params.limit
        page = (params.offset // page_size) + 1 if page_size > 0 else 1

        logger.info(
            "search_completed",
            extra={
                "query": params.search,
                "total": total,
                "returned": len(hits),
                "took_ms": took_ms,
            },
        )

        return SearchResponse(
            hits=hits,
            total=total,
            took_ms=took_ms,
            query=params.search,
            page=page,
            page_size=page_size,
        )

    async def suggest(self, query: str, limit: int = 8) -> SuggestionsResponse:
        body = build_autocomplete_query(query, limit)

        response = await self._es.search(
            index=self._index,
            query=body["query"],
            size=body["size"],
            source=body["_source"],
        )

        suggestions = [
            SuggestionItem(
                id=hit["_source"]["id"],
                title=hit["_source"]["title"],
                score=round(hit["_score"], 4),
            )
            for hit in response["hits"]["hits"]
        ]

        return SuggestionsResponse(suggestions=suggestions, query=query)

    async def get_by_id(self, item_id: str) -> dict | None:
        try:
            response = await self._es.get(index=self._index, id=item_id)
            return response["_source"]
        except Exception:
            return None


def _hit_to_model(hit: dict) -> SearchHit:
    src = hit.get("_source", {})
    return SearchHit(
        id=src.get("id", hit["_id"]),
        title=src.get("title", ""),
        short_description=src.get("short_description", ""),
        category_id=src.get("category_id", ""),
        tags=src.get("tags", []),
        rating_avg=float(src.get("rating_avg", 0.0)),
        view_count=int(src.get("view_count", 0)),
        is_published=bool(src.get("is_published", True)),
        created_at=src.get("created_at"),
        updated_at=src.get("updated_at"),
        preview_image_key=src.get("preview_image_key"),
        score=round(float(hit.get("_score") or 0.0), 4),
    )
