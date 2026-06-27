from typing import Protocol

from src.backend.search.domain.models import SearchResponse, SuggestionsResponse
from src.backend.search.domain.value_objects import ItemSearchParams


class SearchRepositoryProtocol(Protocol):
    async def search(self, params: ItemSearchParams) -> SearchResponse: ...
    async def get_by_id(self, item_id: str) -> dict | None: ...


class AutocompleteRepositoryProtocol(Protocol):
    async def suggest(self, query: str, limit: int) -> SuggestionsResponse: ...
