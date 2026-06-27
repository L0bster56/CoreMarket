# Moved to search/infrastructure/elasticsearch/repositories/item_search.py
# ESItemSearchRepository replaces ItemSearchService
from src.backend.search.infrastructure.elasticsearch.repositories.item_search import (  # noqa: F401
    ESItemSearchRepository as ItemSearchService,
    _hit_to_model as _hit_to_schema,
)
