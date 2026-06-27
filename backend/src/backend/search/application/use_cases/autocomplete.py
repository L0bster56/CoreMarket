from src.backend.search.domain.models import SuggestionsResponse
from src.backend.search.domain.repositories import AutocompleteRepositoryProtocol


class AutocompleteUseCase:
    def __init__(self, repository: AutocompleteRepositoryProtocol) -> None:
        self._repo = repository

    async def execute(self, query: str, limit: int) -> SuggestionsResponse:
        return await self._repo.suggest(query, limit)
