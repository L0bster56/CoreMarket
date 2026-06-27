from src.backend.search.domain.models import SearchResponse
from src.backend.search.domain.repositories import SearchRepositoryProtocol
from src.backend.search.domain.value_objects import ItemSearchParams


class SearchItemsUseCase:
    def __init__(self, repository: SearchRepositoryProtocol) -> None:
        self._repo = repository

    async def execute(self, params: ItemSearchParams) -> SearchResponse:
        return await self._repo.search(params)
