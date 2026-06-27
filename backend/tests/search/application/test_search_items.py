from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.backend.search.application.use_cases.search_items import SearchItemsUseCase
from src.backend.search.domain.models import SearchHit, SearchResponse
from src.backend.search.domain.value_objects import ItemSearchParams


def _make_search_response(num_hits: int = 2) -> SearchResponse:
    hits = [
        SearchHit(
            id=str(uuid4()),
            title=f"Item {i}",
            short_description=f"Desc {i}",
            category_id=str(uuid4()),
            tags=["python"],
            rating_avg=4.0,
            view_count=100,
            is_published=True,
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-01T00:00:00",
            preview_image_key=None,
            score=1.0,
        )
        for i in range(num_hits)
    ]
    return SearchResponse(hits=hits, total=num_hits, took_ms=5, query=None, page=1, page_size=20)


class TestSearchItemsUseCase:
    async def test_delegates_to_repository(self):
        repo = AsyncMock()
        repo.search.return_value = _make_search_response()
        uc = SearchItemsUseCase(repo)
        params = ItemSearchParams(search="laptop")

        result = await uc.execute(params)

        repo.search.assert_called_once_with(params)
        assert len(result.hits) == 2

    async def test_returns_empty_results(self):
        repo = AsyncMock()
        repo.search.return_value = SearchResponse(
            hits=[], total=0, took_ms=1, query=None, page=1, page_size=20
        )
        uc = SearchItemsUseCase(repo)

        result = await uc.execute(ItemSearchParams())

        assert result.total == 0
        assert result.hits == []

    async def test_passes_all_filter_params(self):
        repo = AsyncMock()
        repo.search.return_value = _make_search_response(0)
        uc = SearchItemsUseCase(repo)
        cat_id = uuid4()
        params = ItemSearchParams(
            search="query",
            category_id=cat_id,
            tags=["python"],
            min_rating=3.5,
            is_published=True,
            sort_by="rating",
            limit=10,
            offset=5,
        )

        await uc.execute(params)

        called_params = repo.search.call_args[0][0]
        assert called_params.search == "query"
        assert called_params.category_id == cat_id
        assert called_params.tags == ["python"]
        assert called_params.min_rating == 3.5
        assert called_params.limit == 10
        assert called_params.offset == 5

    async def test_returns_repository_response_unchanged(self):
        repo = AsyncMock()
        expected = _make_search_response(3)
        repo.search.return_value = expected
        uc = SearchItemsUseCase(repo)

        result = await uc.execute(ItemSearchParams())

        assert result is expected


@pytest.mark.parametrize("sort_by", ["relevance", "rating", "views", "newest", "popularity"])
async def test_sort_option_forwarded(sort_by: str) -> None:
    repo = AsyncMock()
    repo.search.return_value = _make_search_response(0)
    uc = SearchItemsUseCase(repo)
    await uc.execute(ItemSearchParams(sort_by=sort_by))
    assert repo.search.call_args[0][0].sort_by == sort_by


async def test_response_metadata_preserved() -> None:
    repo = AsyncMock()
    response = SearchResponse(
        hits=[], total=99, took_ms=42, query="gpu", page=5, page_size=10
    )
    repo.search.return_value = response
    uc = SearchItemsUseCase(repo)
    result = await uc.execute(ItemSearchParams(search="gpu", limit=10, offset=40))
    assert result.total == 99
    assert result.took_ms == 42
    assert result.page == 5
    assert result.page_size == 10


async def test_default_is_published_true() -> None:
    repo = AsyncMock()
    repo.search.return_value = _make_search_response(0)
    uc = SearchItemsUseCase(repo)
    await uc.execute(ItemSearchParams())
    assert repo.search.call_args[0][0].is_published is True


async def test_none_search_forwarded() -> None:
    repo = AsyncMock()
    repo.search.return_value = _make_search_response(0)
    uc = SearchItemsUseCase(repo)
    await uc.execute(ItemSearchParams(search=None))
    assert repo.search.call_args[0][0].search is None


async def test_large_offset_preserved() -> None:
    repo = AsyncMock()
    repo.search.return_value = _make_search_response(0)
    uc = SearchItemsUseCase(repo)
    await uc.execute(ItemSearchParams(limit=5, offset=500))
    p = repo.search.call_args[0][0]
    assert p.offset == 500
    assert p.limit == 5


async def test_multiple_tags_forwarded() -> None:
    repo = AsyncMock()
    repo.search.return_value = _make_search_response(0)
    uc = SearchItemsUseCase(repo)
    await uc.execute(ItemSearchParams(tags=["python", "django", "fastapi"]))
    assert repo.search.call_args[0][0].tags == ["python", "django", "fastapi"]


async def test_empty_tags_forwarded() -> None:
    repo = AsyncMock()
    repo.search.return_value = _make_search_response(0)
    uc = SearchItemsUseCase(repo)
    await uc.execute(ItemSearchParams(tags=[]))
    assert repo.search.call_args[0][0].tags == []
