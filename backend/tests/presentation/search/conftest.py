from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.backend.main import app
from src.backend.presentation.api.v1.search.dependencies import (
    get_autocomplete_use_case,
    get_search_use_case,
)
from src.backend.search.domain.models import (
    SearchHit,
    SearchResponse,
    SuggestionItem,
    SuggestionsResponse,
)


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


def _make_suggestions_response() -> SuggestionsResponse:
    return SuggestionsResponse(
        suggestions=[
            SuggestionItem(id=str(uuid4()), title="Laptop Pro", score=1.2),
            SuggestionItem(id=str(uuid4()), title="Laptop Air", score=1.0),
        ],
        query="lap",
    )


@pytest.fixture
def mock_search_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_search_response()
    app.dependency_overrides[get_search_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_search_use_case, None)


@pytest.fixture
def mock_autocomplete_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_suggestions_response()
    app.dependency_overrides[get_autocomplete_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_autocomplete_use_case, None)
