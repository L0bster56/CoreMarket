from uuid import UUID

import pytest

from src.backend.search.domain.value_objects import ItemSearchParams
from src.backend.search.infrastructure.elasticsearch.queries.items import (
    build_autocomplete_query,
    build_item_search_query,
)


class TestBuildItemSearchQuery:
    def test_no_search_with_default_params_returns_bool_filter(self):
        # Default is_published=True produces a bool filter, not match_all
        params = ItemSearchParams()
        query = build_item_search_query(params)
        assert "bool" in query["query"]
        assert {"term": {"is_published": True}} in query["query"]["bool"]["filter"]

    def test_no_search_no_filters_returns_match_all(self):
        params = ItemSearchParams(is_published=None)
        query = build_item_search_query(params)
        assert query["query"] == {"match_all": {}}

    def test_search_text_uses_function_score(self):
        params = ItemSearchParams(search="телефон")
        query = build_item_search_query(params)
        assert "function_score" in query["query"]

    def test_search_multi_match_has_fuzziness(self):
        params = ItemSearchParams(search="ноутбук")
        query = build_item_search_query(params)
        multi_match = query["query"]["function_score"]["query"]["bool"]["must"][0]["multi_match"]
        assert multi_match["fuzziness"] == "AUTO"
        assert "title^4" in multi_match["fields"]

    def test_category_filter_applied(self):
        cat_id = UUID("12345678-1234-5678-1234-567812345678")
        params = ItemSearchParams(category_id=cat_id)
        query = build_item_search_query(params)
        assert "bool" in query["query"]
        filters = query["query"]["bool"]["filter"]
        assert {"term": {"category_id": str(cat_id)}} in filters

    def test_min_rating_filter(self):
        params = ItemSearchParams(min_rating=4.0)
        query = build_item_search_query(params)
        filters = query["query"]["bool"]["filter"]
        assert {"range": {"rating_avg": {"gte": 4.0}}} in filters

    def test_tags_filter(self):
        params = ItemSearchParams(tags=["smartphones", "android"])
        query = build_item_search_query(params)
        filters = query["query"]["bool"]["filter"]
        assert {"terms": {"tags": ["smartphones", "android"]}} in filters

    def test_pagination(self):
        params = ItemSearchParams(limit=10, offset=30)
        query = build_item_search_query(params)
        assert query["from"] == 30
        assert query["size"] == 10

    def test_sort_newest(self):
        params = ItemSearchParams(sort_by="newest")
        query = build_item_search_query(params)
        assert query["sort"] == [{"created_at": {"order": "desc"}}]

    def test_sort_rating(self):
        params = ItemSearchParams(sort_by="rating")
        query = build_item_search_query(params)
        assert query["sort"][0] == {"rating_avg": {"order": "desc"}}

    def test_sort_relevance_with_search(self):
        params = ItemSearchParams(search="query", sort_by="relevance")
        query = build_item_search_query(params)
        assert query["sort"][0] == {"_score": {"order": "desc"}}

    def test_function_score_has_popularity_functions(self):
        params = ItemSearchParams(search="test")
        query = build_item_search_query(params)
        functions = query["query"]["function_score"]["functions"]
        fields = [f["field_value_factor"]["field"] for f in functions]
        assert "rating_avg" in fields
        assert "view_count" in fields

    def test_is_published_filter_default_true(self):
        params = ItemSearchParams()
        query = build_item_search_query(params)
        filters = query["query"]["match_all"] if "match_all" in query["query"] else []
        # Default is_published=True — when no other filters, it generates match_all
        # but with is_published filter it becomes a bool query
        params_with_published = ItemSearchParams(is_published=True)
        q2 = build_item_search_query(params_with_published)
        assert {"term": {"is_published": True}} in q2["query"]["bool"]["filter"]

    def test_no_is_published_filter_when_none(self):
        params = ItemSearchParams(is_published=None)
        query = build_item_search_query(params)
        # When no filters at all, should be match_all
        assert query["query"] == {"match_all": {}}


class TestBuildAutocompleteQuery:
    def test_has_is_published_filter(self):
        query = build_autocomplete_query("теле")
        filter_terms = query["query"]["bool"]["filter"]
        assert {"term": {"is_published": True}} in filter_terms

    def test_uses_autocomplete_fields(self):
        query = build_autocomplete_query("nout")
        fields = query["query"]["bool"]["must"][0]["multi_match"]["fields"]
        assert any("autocomplete" in f for f in fields)

    def test_respects_limit(self):
        query = build_autocomplete_query("test", limit=5)
        assert query["size"] == 5

    def test_source_limited(self):
        query = build_autocomplete_query("x")
        assert "_source" in query
        assert "id" in query["_source"]
        assert "title" in query["_source"]
