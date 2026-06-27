from __future__ import annotations

from unittest.mock import patch
from uuid import uuid4

import pytest
from elasticsearch import TransportError

from src.backend.search.domain.models import SearchResponse

BASE = "/api/v1/search/items"


async def test_search_items_200(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=laptop")

    assert response.status_code == 200
    data = response.json()
    assert "hits" in data
    assert "total" in data
    assert data["total"] == 2


async def test_search_items_503_when_disabled(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = False
        response = await anon_client.get(f"{BASE}?q=laptop")

    assert response.status_code == 503


async def test_search_items_passes_query(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?q=laptop")

    params = mock_search_uc.execute.call_args[0][0]
    assert params.search == "laptop"


async def test_search_items_passes_category_filter(anon_client, mock_search_uc):
    cat_id = uuid4()
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?category_id={cat_id}")

    params = mock_search_uc.execute.call_args[0][0]
    assert params.category_id == cat_id


async def test_search_items_passes_tag_filter(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?tag=python")

    params = mock_search_uc.execute.call_args[0][0]
    assert "python" in params.tags


async def test_search_items_passes_min_rating(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?min_rating=3.5")

    params = mock_search_uc.execute.call_args[0][0]
    assert params.min_rating == 3.5


async def test_search_items_pagination(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?limit=5&offset=10")

    params = mock_search_uc.execute.call_args[0][0]
    assert params.limit == 5
    assert params.offset == 10


async def test_search_items_sort_by_rating(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?sort_by=rating")

    params = mock_search_uc.execute.call_args[0][0]
    assert params.sort_by == "rating"


async def test_search_items_invalid_sort_by_422(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?sort_by=invalid_sort")

    assert response.status_code == 422


async def test_search_items_empty_results(anon_client, mock_search_uc):
    mock_search_uc.execute.return_value = SearchResponse(
        hits=[], total=0, took_ms=1, query=None, page=1, page_size=20
    )
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=xyz")

    assert response.status_code == 200
    data = response.json()
    assert data["hits"] == []
    assert data["total"] == 0


async def test_search_items_503_on_es_exception(anon_client, mock_search_uc):
    mock_search_uc.execute.side_effect = TransportError("es unavailable")
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=laptop")
    assert response.status_code == 503


@pytest.mark.parametrize("sort_by", ["relevance", "rating", "views", "newest", "popularity"])
async def test_valid_sort_options_accepted(anon_client, mock_search_uc, sort_by):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?sort_by={sort_by}")
    assert response.status_code == 200
    assert mock_search_uc.execute.call_args[0][0].sort_by == sort_by


async def test_is_published_always_true(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(BASE)
    assert mock_search_uc.execute.call_args[0][0].is_published is True


async def test_response_hit_has_required_fields(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=test")
    hit = response.json()["hits"][0]
    for field in ("id", "title", "short_description", "category_id", "rating_avg", "score"):
        assert field in hit, f"Field '{field}' missing from hit"


async def test_response_has_metadata_fields(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(BASE)
    data = response.json()
    for field in ("total", "took_ms", "page", "page_size"):
        assert field in data, f"Metadata field '{field}' missing"


async def test_no_tag_param_produces_empty_tags(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(BASE)
    assert mock_search_uc.execute.call_args[0][0].tags == []


async def test_min_rating_below_1_returns_422(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?min_rating=0.5")
    assert response.status_code == 422


async def test_limit_above_100_returns_422(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?limit=101")
    assert response.status_code == 422


async def test_negative_offset_returns_422(anon_client, mock_search_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?offset=-1")
    assert response.status_code == 422
