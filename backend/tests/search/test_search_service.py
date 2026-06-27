from unittest.mock import AsyncMock

import pytest

from src.backend.search.domain.models import SearchHit, SearchResponse, SuggestionItem, SuggestionsResponse
from src.backend.search.domain.value_objects import ItemSearchParams
from src.backend.search.infrastructure.elasticsearch.repositories.item_search import (
    ESItemSearchRepository,
    _hit_to_model,
)


def _make_es_search_response(hits: list[dict], total: int = None, took: int = 5) -> dict:
    total = total if total is not None else len(hits)
    return {
        "took": took,
        "hits": {
            "total": {"value": total},
            "hits": hits,
        },
    }


def _make_hit(item_id: str, title: str, score: float = 1.0, **extra) -> dict:
    source = {
        "id": item_id,
        "title": title,
        "short_description": "desc",
        "category_id": "cat-1",
        "tags": [],
        "rating_avg": 4.5,
        "view_count": 100,
        "is_published": True,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "preview_image_key": None,
        **extra,
    }
    return {"_id": item_id, "_score": score, "_source": source}


class TestHitToModel:
    def test_basic_fields(self):
        hit = _make_hit("abc", "Test Product", score=2.5)
        result = _hit_to_model(hit)
        assert result.id == "abc"
        assert result.title == "Test Product"
        assert result.score == 2.5

    def test_missing_score_defaults_zero(self):
        hit = _make_hit("x", "Y", score=None)
        hit["_score"] = None
        result = _hit_to_model(hit)
        assert result.score == 0.0

    def test_tags_preserved(self):
        hit = _make_hit("id1", "T", tags=["a", "b"])
        result = _hit_to_model(hit)
        assert result.tags == ["a", "b"]

    def test_preview_image_key_none(self):
        hit = _make_hit("id2", "Title")
        result = _hit_to_model(hit)
        assert result.preview_image_key is None


class TestESItemSearchRepository:
    def _make_repo(self) -> tuple[ESItemSearchRepository, AsyncMock]:
        mock_es = AsyncMock()
        repo = ESItemSearchRepository(es=mock_es, index_name="coremarket_items")
        return repo, mock_es

    async def test_search_returns_search_response(self):
        repo, mock_es = self._make_repo()
        mock_es.search.return_value = _make_es_search_response(
            hits=[_make_hit("1", "Телефон Samsung")],
            total=1,
        )

        result = await repo.search(ItemSearchParams(search="samsung"))

        assert isinstance(result, SearchResponse)
        assert result.total == 1
        assert len(result.hits) == 1
        assert result.hits[0].title == "Телефон Samsung"
        assert result.took_ms == 5
        assert result.query == "samsung"

    async def test_search_no_query_returns_results(self):
        repo, mock_es = self._make_repo()
        mock_es.search.return_value = _make_es_search_response(
            hits=[_make_hit("2", "Laptop")],
            total=1,
        )

        result = await repo.search(ItemSearchParams())
        assert result.total == 1

    async def test_pagination_page_calculation(self):
        repo, mock_es = self._make_repo()
        mock_es.search.return_value = _make_es_search_response(hits=[], total=100)

        result = await repo.search(ItemSearchParams(limit=20, offset=40))
        assert result.page == 3
        assert result.page_size == 20

    async def test_suggest_returns_suggestions(self):
        repo, mock_es = self._make_repo()
        mock_es.search.return_value = {
            "hits": {
                "total": {"value": 2},
                "hits": [
                    {"_id": "1", "_score": 3.0, "_source": {"id": "1", "title": "Телефон"}},
                    {"_id": "2", "_score": 2.0, "_source": {"id": "2", "title": "Теле-визор"}},
                ],
            }
        }

        result = await repo.suggest("теле", limit=5)

        assert isinstance(result, SuggestionsResponse)
        assert len(result.suggestions) == 2
        assert result.query == "теле"
        assert result.suggestions[0].title == "Телефон"

    async def test_search_calls_es_with_correct_index(self):
        repo, mock_es = self._make_repo()
        mock_es.search.return_value = _make_es_search_response(hits=[], total=0)

        await repo.search(ItemSearchParams(search="test"))

        mock_es.search.assert_called_once()
        call_kwargs = mock_es.search.call_args.kwargs
        assert call_kwargs["index"] == "coremarket_items"

    async def test_get_by_id_returns_source(self):
        repo, mock_es = self._make_repo()
        mock_es.get.return_value = {"_source": {"id": "abc", "title": "Test"}}

        result = await repo.get_by_id("abc")
        assert result == {"id": "abc", "title": "Test"}

    async def test_get_by_id_returns_none_on_error(self):
        repo, mock_es = self._make_repo()
        mock_es.get.side_effect = Exception("not found")

        result = await repo.get_by_id("missing")
        assert result is None
