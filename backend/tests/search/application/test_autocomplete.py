from unittest.mock import AsyncMock

import pytest

from src.backend.search.application.use_cases.autocomplete import AutocompleteUseCase
from src.backend.search.domain.models import SuggestionItem, SuggestionsResponse


def _make_suggestions(query: str = "lap", count: int = 3) -> SuggestionsResponse:
    return SuggestionsResponse(
        suggestions=[
            SuggestionItem(id=f"id-{i}", title=f"Laptop {i}", score=1.0 - i * 0.1)
            for i in range(count)
        ],
        query=query,
    )


class TestAutocompleteUseCase:
    async def test_delegates_to_repository(self):
        repo = AsyncMock()
        repo.suggest.return_value = _make_suggestions()
        uc = AutocompleteUseCase(repo)

        result = await uc.execute(query="lap", limit=5)

        repo.suggest.assert_called_once_with("lap", 5)
        assert len(result.suggestions) == 3

    async def test_returns_empty_suggestions(self):
        repo = AsyncMock()
        repo.suggest.return_value = SuggestionsResponse(suggestions=[], query="xyz")
        uc = AutocompleteUseCase(repo)

        result = await uc.execute(query="xyz", limit=8)

        assert result.suggestions == []

    async def test_passes_limit_to_repository(self):
        repo = AsyncMock()
        repo.suggest.return_value = _make_suggestions(count=0)
        uc = AutocompleteUseCase(repo)

        await uc.execute(query="test", limit=3)

        _, limit = repo.suggest.call_args[0]
        assert limit == 3

    async def test_returns_repository_response_unchanged(self):
        repo = AsyncMock()
        expected = _make_suggestions("laptop", 5)
        repo.suggest.return_value = expected
        uc = AutocompleteUseCase(repo)

        result = await uc.execute(query="laptop", limit=8)

        assert result is expected


async def test_query_preserved_in_response() -> None:
    repo = AsyncMock()
    repo.suggest.return_value = SuggestionsResponse(suggestions=[], query="test-q")
    uc = AutocompleteUseCase(repo)
    result = await uc.execute(query="test-q", limit=8)
    assert result.query == "test-q"


async def test_suggestion_fields_preserved() -> None:
    repo = AsyncMock()
    s = SuggestionItem(id="99", title="Galaxy Pro", score=3.14)
    repo.suggest.return_value = SuggestionsResponse(suggestions=[s], query="gal")
    uc = AutocompleteUseCase(repo)
    result = await uc.execute(query="gal", limit=8)
    hit = result.suggestions[0]
    assert hit.id == "99"
    assert hit.title == "Galaxy Pro"
    assert hit.score == 3.14


async def test_suggestions_order_preserved() -> None:
    repo = AsyncMock()
    suggestions = [
        SuggestionItem(id="1", title="First", score=5.0),
        SuggestionItem(id="2", title="Second", score=3.0),
        SuggestionItem(id="3", title="Third", score=1.0),
    ]
    repo.suggest.return_value = SuggestionsResponse(suggestions=suggestions, query="fi")
    uc = AutocompleteUseCase(repo)
    result = await uc.execute(query="fi", limit=8)
    assert [s.id for s in result.suggestions] == ["1", "2", "3"]


async def test_single_char_query_forwarded() -> None:
    repo = AsyncMock()
    repo.suggest.return_value = SuggestionsResponse(suggestions=[], query="a")
    uc = AutocompleteUseCase(repo)
    await uc.execute(query="a", limit=5)
    repo.suggest.assert_called_once_with("a", 5)


@pytest.mark.parametrize("limit", [1, 3, 8, 20])
async def test_various_limits_forwarded(limit: int) -> None:
    repo = AsyncMock()
    repo.suggest.return_value = SuggestionsResponse(suggestions=[], query="x")
    uc = AutocompleteUseCase(repo)
    await uc.execute(query="x", limit=limit)
    _, passed_limit = repo.suggest.call_args[0]
    assert passed_limit == limit


async def test_cyrillic_query_forwarded() -> None:
    repo = AsyncMock()
    repo.suggest.return_value = SuggestionsResponse(suggestions=[], query="ноутбук")
    uc = AutocompleteUseCase(repo)
    await uc.execute(query="ноутбук", limit=8)
    called_query, _ = repo.suggest.call_args[0]
    assert called_query == "ноутбук"
