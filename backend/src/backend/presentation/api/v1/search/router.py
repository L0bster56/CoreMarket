import logging
from uuid import UUID

from elasticsearch import TransportError as ElasticsearchException
from fastapi import APIRouter, HTTPException, Query, status

from src.backend.config import get_settings
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.core.dependencies import UoWDep
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.search.dependencies import AutocompleteUseCaseDep, SearchUseCaseDep
from src.backend.presentation.api.v1.search.schemas import (
    ReindexResponse,
    SearchItemHit,
    SearchItemsResponse,
    SuggestionItemSchema,
    SuggestionsResponse,
)
from src.backend.search.domain.value_objects import ItemSearchParams

logger = logging.getLogger("coremarket.search.router")

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={503: {"model": ExceptionSchema}},
)


def _require_search_enabled() -> None:
    if not get_settings().SEARCH_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service is disabled",
        )


@router.get("/items", response_model=SearchItemsResponse)
async def search_items(
    use_case: SearchUseCaseDep,
    q: str | None = Query(default=None, description="Full-text search query"),
    category_id: UUID | None = Query(default=None),
    tag: str | None = Query(default=None, description="Tag slug filter"),
    min_rating: float | None = Query(default=None, ge=1, le=5),
    sort_by: str = Query(default="relevance", pattern="^(relevance|rating|views|newest|popularity)$"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> SearchItemsResponse:
    _require_search_enabled()

    params = ItemSearchParams(
        search=q,
        category_id=category_id,
        tags=[tag] if tag else [],
        min_rating=min_rating,
        is_published=True,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )

    try:
        result = await use_case.execute(params)
    except ElasticsearchException as exc:
        logger.error("search_elasticsearch_error", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service temporarily unavailable",
        )

    return SearchItemsResponse(
        hits=[
            SearchItemHit(
                id=h.id,
                title=h.title,
                short_description=h.short_description,
                category_id=h.category_id,
                tags=h.tags,
                rating_avg=h.rating_avg,
                view_count=h.view_count,
                is_published=h.is_published,
                created_at=h.created_at,
                updated_at=h.updated_at,
                preview_image_key=h.preview_image_key,
                score=h.score,
            )
            for h in result.hits
        ],
        total=result.total,
        took_ms=result.took_ms,
        query=result.query,
        page=result.page,
        page_size=result.page_size,
    )


@router.get("/suggestions", response_model=SuggestionsResponse)
async def search_suggestions(
    use_case: AutocompleteUseCaseDep,
    q: str = Query(min_length=1, max_length=100, description="Autocomplete query"),
    limit: int = Query(default=8, ge=1, le=20),
) -> SuggestionsResponse:
    _require_search_enabled()

    try:
        result = await use_case.execute(query=q, limit=limit)
    except ElasticsearchException as exc:
        logger.error("autocomplete_elasticsearch_error", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Search service temporarily unavailable",
        )

    return SuggestionsResponse(
        suggestions=[
            SuggestionItemSchema(id=s.id, title=s.title, score=s.score)
            for s in result.suggestions
        ],
        query=result.query,
    )


@router.post("/reindex", response_model=ReindexResponse, status_code=status.HTTP_200_OK)
async def trigger_reindex(
    uow: UoWDep,
    _: AdminUserDep,
) -> ReindexResponse:
    _require_search_enabled()

    from src.backend.config import get_settings as _gs
    from src.backend.infrastructure.db.sqlalchemy.core.session import async_session
    from src.backend.search.infrastructure.elasticsearch.client import get_es_client
    from src.backend.search.infrastructure.elasticsearch.indexes.items import ItemIndex
    from src.backend.search.infrastructure.elasticsearch.sync.item_sync import bulk_reindex

    settings = _gs()
    es = get_es_client()

    try:
        index = ItemIndex(es, settings.ELASTICSEARCH_INDEX_PREFIX)
        await index.recreate_index()

        async with async_session() as session:
            indexed = await bulk_reindex(
                session=session,
                es=es,
                index_name=index.index_name,
            )

        logger.info("reindex_completed", extra={"indexed": indexed})
        return ReindexResponse(indexed=indexed, message=f"Successfully reindexed {indexed} items")

    except ElasticsearchException as exc:
        logger.error("reindex_elasticsearch_error", exc_info=exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Reindex failed — Elasticsearch unavailable",
        )
