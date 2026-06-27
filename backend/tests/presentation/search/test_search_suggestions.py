from __future__ import annotations

from unittest.mock import patch

import pytest
from elasticsearch import TransportError

from src.backend.search.domain.models import SuggestionsResponse

BASE = "/api/v1/search/suggestions"


async def test_suggestions_200(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap")

    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert "query" in data
    assert len(data["suggestions"]) == 2


async def test_suggestions_503_when_disabled(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = False
        response = await anon_client.get(f"{BASE}?q=lap")

    assert response.status_code == 503


async def test_suggestions_passes_query(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?q=laptop&limit=5")

    call_kwargs = mock_autocomplete_uc.execute.call_args[1]
    assert call_kwargs["query"] == "laptop"
    assert call_kwargs["limit"] == 5


async def test_suggestions_empty_results(anon_client, mock_autocomplete_uc):
    mock_autocomplete_uc.execute.return_value = SuggestionsResponse(
        suggestions=[], query="xyz"
    )
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=xyz")

    assert response.status_code == 200
    data = response.json()
    assert data["suggestions"] == []


async def test_suggestions_422_missing_query(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(BASE)

    assert response.status_code == 422


async def test_suggestions_default_limit(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?q=lap")

    call_kwargs = mock_autocomplete_uc.execute.call_args[1]
    assert call_kwargs["limit"] == 8


async def test_suggestions_503_on_es_exception(anon_client, mock_autocomplete_uc):
    mock_autocomplete_uc.execute.side_effect = TransportError("es unavailable")
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap")
    assert response.status_code == 503


async def test_suggestions_limit_above_20_returns_422(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap&limit=21")
    assert response.status_code == 422


async def test_suggestions_limit_1_is_valid(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap&limit=1")
    assert response.status_code == 200


async def test_suggestion_has_id_title_score(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap")
    suggestion = response.json()["suggestions"][0]
    assert "id" in suggestion
    assert "title" in suggestion
    assert "score" in suggestion


async def test_suggestions_query_echoed_in_response(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap")
    assert response.json()["query"] == "lap"


async def test_suggestions_limit_20_is_valid(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        response = await anon_client.get(f"{BASE}?q=lap&limit=20")
    assert response.status_code == 200
    call_kwargs = mock_autocomplete_uc.execute.call_args[1]
    assert call_kwargs["limit"] == 20


async def test_suggestions_passes_query_string(anon_client, mock_autocomplete_uc):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = True
        await anon_client.get(f"{BASE}?q=ноутбук")
    call_kwargs = mock_autocomplete_uc.execute.call_args[1]
    assert call_kwargs["query"] == "ноутбук"
