from elasticsearch import AsyncElasticsearch

from src.backend.search.infrastructure.elasticsearch.indexes.base import BaseIndex

_ANALYSIS = {
    "analyzer": {
        "multilingual": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": [
                "lowercase",
                "russian_stop",
                "russian_stemmer",
                "english_stop",
                "english_stemmer",
            ],
        },
        "autocomplete_index": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": ["lowercase", "edge_ngram_filter"],
        },
        "autocomplete_search": {
            "type": "custom",
            "tokenizer": "standard",
            "filter": ["lowercase"],
        },
    },
    "normalizer": {
        "lowercase_normalizer": {
            "type": "custom",
            "filter": ["lowercase"],
        }
    },
    "filter": {
        "russian_stop": {"type": "stop", "stopwords": "_russian_"},
        "russian_stemmer": {"type": "stemmer", "language": "russian"},
        "english_stop": {"type": "stop", "stopwords": "_english_"},
        "english_stemmer": {"type": "stemmer", "language": "english"},
        "edge_ngram_filter": {
            "type": "edge_ngram",
            "min_gram": 2,
            "max_gram": 20,
        },
    },
}

_MAPPINGS = {
    "properties": {
        "id": {"type": "keyword"},
        "title": {
            "type": "text",
            "analyzer": "multilingual",
            "fields": {
                "keyword": {
                    "type": "keyword",
                    "normalizer": "lowercase_normalizer",
                },
                "autocomplete": {
                    "type": "text",
                    "analyzer": "autocomplete_index",
                    "search_analyzer": "autocomplete_search",
                },
            },
        },
        "short_description": {
            "type": "text",
            "analyzer": "multilingual",
        },
        "description": {
            "type": "text",
            "analyzer": "multilingual",
        },
        "category_id": {"type": "keyword"},
        "category_name": {
            "type": "keyword",
            "normalizer": "lowercase_normalizer",
            "fields": {
                "text": {"type": "text", "analyzer": "multilingual"}
            },
        },
        "tags": {
            "type": "keyword",
            "normalizer": "lowercase_normalizer",
            "fields": {
                "text": {"type": "text", "analyzer": "multilingual"}
            },
        },
        "tag_names": {
            "type": "text",
            "analyzer": "multilingual",
        },
        "rating_avg": {"type": "float"},
        "view_count": {"type": "integer"},
        "is_published": {"type": "boolean"},
        "created_at": {"type": "date"},
        "updated_at": {"type": "date"},
        "characteristics": {
            "type": "nested",
            "properties": {
                "name": {"type": "text", "analyzer": "multilingual"},
                "value": {"type": "text", "analyzer": "multilingual"},
                "group": {"type": "keyword"},
            },
        },
        "popularity_score": {"type": "float"},
        "preview_image_key": {"type": "keyword", "index": False},
        "marketplace_links": {"type": "object", "enabled": False},
    }
}


class ItemIndex(BaseIndex):

    def __init__(self, es: AsyncElasticsearch, prefix: str) -> None:
        super().__init__(es, prefix)

    @property
    def index_name(self) -> str:
        return f"{self.prefix}_items"

    @property
    def index_config(self) -> dict:
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": _ANALYSIS,
            },
            "mappings": _MAPPINGS,
        }
