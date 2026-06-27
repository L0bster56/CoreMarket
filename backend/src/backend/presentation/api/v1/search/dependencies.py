from typing import Annotated

from fastapi import Depends

from src.backend.config import get_settings
from src.backend.search.application.use_cases.autocomplete import AutocompleteUseCase
from src.backend.search.application.use_cases.search_items import SearchItemsUseCase
from src.backend.search.infrastructure.elasticsearch.client import get_es_client
from src.backend.search.infrastructure.elasticsearch.indexes.items import ItemIndex
from src.backend.search.infrastructure.elasticsearch.repositories.item_search import ESItemSearchRepository


def _get_es_repository() -> ESItemSearchRepository:
    settings = get_settings()
    es = get_es_client()
    index = ItemIndex(es, settings.ELASTICSEARCH_INDEX_PREFIX)
    return ESItemSearchRepository(es=es, index_name=index.index_name)


def get_search_use_case() -> SearchItemsUseCase:
    return SearchItemsUseCase(_get_es_repository())


def get_autocomplete_use_case() -> AutocompleteUseCase:
    return AutocompleteUseCase(_get_es_repository())


SearchUseCaseDep = Annotated[SearchItemsUseCase, Depends(get_search_use_case)]
AutocompleteUseCaseDep = Annotated[AutocompleteUseCase, Depends(get_autocomplete_use_case)]
