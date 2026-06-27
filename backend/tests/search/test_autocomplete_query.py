"""Tests for build_autocomplete_query covering structure, size, fields, and filters."""
import pytest

from src.backend.search.infrastructure.elasticsearch.queries.items import build_autocomplete_query


# ---------------------------------------------------------------------------
# Top-level structure
# ---------------------------------------------------------------------------

class TestAutocompleteQueryTopLevel:
    def test_has_query_key(self):
        assert "query" in build_autocomplete_query("test")

    def test_has_size_key(self):
        assert "size" in build_autocomplete_query("test")

    def test_has_source_key(self):
        assert "_source" in build_autocomplete_query("test")

    def test_exactly_three_top_level_keys(self):
        keys = set(build_autocomplete_query("test").keys())
        assert keys == {"query", "size", "_source"}


# ---------------------------------------------------------------------------
# _source field list
# ---------------------------------------------------------------------------

class TestAutocompleteQuerySource:
    def test_source_contains_id(self):
        assert "id" in build_autocomplete_query("x")["_source"]

    def test_source_contains_title(self):
        assert "title" in build_autocomplete_query("x")["_source"]

    def test_source_has_exactly_two_fields(self):
        assert len(build_autocomplete_query("x")["_source"]) == 2


# ---------------------------------------------------------------------------
# Size / limit
# ---------------------------------------------------------------------------

class TestAutocompleteQuerySize:
    def test_default_size_8(self):
        assert build_autocomplete_query("test")["size"] == 8

    def test_custom_limit_1(self):
        assert build_autocomplete_query("test", limit=1)["size"] == 1

    def test_custom_limit_5(self):
        assert build_autocomplete_query("abc", limit=5)["size"] == 5

    def test_custom_limit_20(self):
        assert build_autocomplete_query("x", limit=20)["size"] == 20


# ---------------------------------------------------------------------------
# Query structure (bool → must + filter)
# ---------------------------------------------------------------------------

class TestAutocompleteQueryBoolStructure:
    def _bool(self, q: str = "test") -> dict:
        return build_autocomplete_query(q)["query"]["bool"]

    def test_bool_has_must(self):
        assert "must" in self._bool()

    def test_bool_has_filter(self):
        assert "filter" in self._bool()

    def test_must_is_list_with_one_item(self):
        assert len(self._bool()["must"]) == 1

    def test_filter_is_list(self):
        assert isinstance(self._bool()["filter"], list)


# ---------------------------------------------------------------------------
# multi_match inside bool.must
# ---------------------------------------------------------------------------

class TestAutocompleteQueryMultiMatch:
    def _mm(self, q: str = "test") -> dict:
        return build_autocomplete_query(q)["query"]["bool"]["must"][0]["multi_match"]

    def test_type_best_fields(self):
        assert self._mm()["type"] == "best_fields"

    def test_query_text_is_forwarded(self):
        assert self._mm("телефон")["query"] == "телефон"

    def test_title_autocomplete_boost_3(self):
        assert "title.autocomplete^3" in self._mm()["fields"]

    def test_title_boost_4(self):
        assert "title^4" in self._mm()["fields"]

    def test_exactly_two_fields(self):
        assert len(self._mm()["fields"]) == 2

    def test_single_char_query(self):
        assert self._mm("a")["query"] == "a"

    def test_long_query_text(self):
        long_q = "samsung galaxy s24 ultra pro max"
        assert self._mm(long_q)["query"] == long_q

    def test_cyrillic_query(self):
        assert self._mm("ноутбук")["query"] == "ноутбук"


# ---------------------------------------------------------------------------
# Filter (is_published)
# ---------------------------------------------------------------------------

class TestAutocompleteQueryFilter:
    def _filters(self) -> list:
        return build_autocomplete_query("x")["query"]["bool"]["filter"]

    def test_is_published_true_filter_present(self):
        assert {"term": {"is_published": True}} in self._filters()

    def test_only_one_filter(self):
        assert len(self._filters()) == 1

    def test_filter_is_not_false(self):
        filters = self._filters()
        assert {"term": {"is_published": False}} not in filters
