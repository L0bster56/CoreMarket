# Moved to search/infrastructure/elasticsearch/sync/item_sync.py
from src.backend.search.infrastructure.elasticsearch.sync.item_sync import (  # noqa: F401
    _popularity_score,
    build_item_document,
    bulk_reindex,
    delete_item_from_index,
    index_item,
)
