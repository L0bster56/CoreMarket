from uuid import uuid4

import pytest

from src.backend.search.domain.value_objects import ItemSearchParams
from src.backend.search.infrastructure.elasticsearch.queries.items import (
    build_autocomplete_query,
    build_item_search_query,
)


class TestBuildItemSearchQueryNoSearch:
    def test_no_params_returns_match_all(self):
        params = ItemSearchParams(is_published=None)
        query = build_item_search_query(params)
        assert "match_all" in query["query"]

    def test_with_filters_returns_bool_filter(self):
        params = ItemSearchParams(is_published=True)
        query = build_item_search_query(params)
        assert "bool" in query["query"]
        assert "filter" in query["query"]["bool"]

    def test_includes_pagination(self):
        params = ItemSearchParams(offset=20, limit=10)
        query = build_item_search_query(params)
        assert query["from"] == 20
        assert query["size"] == 10


class TestBuildItemSearchQueryWithSearch:
    def test_text_search_uses_function_score(self):
        params = ItemSearchParams(search="laptop")
        query = build_item_search_query(params)
        assert "function_score" in query["query"]

    def test_text_search_uses_multi_match(self):
        params = ItemSearchParams(search="laptop")
        query = build_item_search_query(params)
        fn_score = query["query"]["function_score"]
        must = fn_score["query"]["bool"]["must"]
        assert any("multi_match" in clause for clause in must)

    def test_function_score_boosts_rating_and_views(self):
        params = ItemSearchParams(search="laptop")
        query = build_item_search_query(params)
        fn_score = query["query"]["function_score"]
        fields = [f["field_value_factor"]["field"] for f in fn_score["functions"]]
        assert "rating_avg" in fields
        assert "view_count" in fields

    def test_fuzziness_is_auto(self):
        params = ItemSearchParams(search="lptop")
        query = build_item_search_query(params)
        fn_score = query["query"]["function_score"]
        multi_match = fn_score["query"]["bool"]["must"][0]["multi_match"]
        assert multi_match["fuzziness"] == "AUTO"

    def test_title_field_has_highest_boost(self):
        params = ItemSearchParams(search="laptop")
        query = build_item_search_query(params)
        fn_score = query["query"]["function_score"]
        multi_match = fn_score["query"]["bool"]["must"][0]["multi_match"]
        boosted = [f for f in multi_match["fields"] if f.startswith("title^")]
        assert boosted, "title field must have boost"
        boost = float(boosted[0].split("^")[1])
        assert boost >= 4


class TestBuildItemSearchQueryFilters:
    def test_category_filter_applied(self):
        cat_id = uuid4()
        params = ItemSearchParams(category_id=cat_id)
        query = build_item_search_query(params)
        filters = query["query"]["bool"]["filter"]
        cat_filters = [f for f in filters if "category_id" in str(f)]
        assert cat_filters

    def test_tag_filter_applied(self):
        params = ItemSearchParams(tags=["python", "django"])
        query = build_item_search_query(params)
        filters = query["query"]["bool"]["filter"]
        tag_filters = [f for f in filters if "terms" in f and "tags" in f["terms"]]
        assert tag_filters
        assert "python" in tag_filters[0]["terms"]["tags"]

    def test_min_rating_filter_applied(self):
        params = ItemSearchParams(min_rating=3.5)
        query = build_item_search_query(params)
        filters = query["query"]["bool"]["filter"]
        rating_filters = [f for f in filters if "range" in f]
        assert rating_filters
        assert rating_filters[0]["range"]["rating_avg"]["gte"] == 3.5

    def test_is_published_filter_applied(self):
        params = ItemSearchParams(is_published=True)
        query = build_item_search_query(params)
        filters = query["query"]["bool"]["filter"]
        pub_filters = [f for f in filters if "term" in f and "is_published" in f["term"]]
        assert pub_filters
        assert pub_filters[0]["term"]["is_published"] is True

    def test_no_filters_when_all_none(self):
        params = ItemSearchParams(is_published=None)
        query = build_item_search_query(params)
        assert "match_all" in query["query"]


class TestBuildItemSearchQuerySorting:
    def test_sort_by_relevance_with_search(self):
        params = ItemSearchParams(search="laptop", sort_by="relevance")
        query = build_item_search_query(params)
        sort_fields = [list(s.keys())[0] for s in query["sort"]]
        assert "_score" in sort_fields

    def test_sort_by_rating(self):
        params = ItemSearchParams(sort_by="rating")
        query = build_item_search_query(params)
        sort_fields = [list(s.keys())[0] for s in query["sort"]]
        assert "rating_avg" in sort_fields

    def test_sort_by_views(self):
        params = ItemSearchParams(sort_by="views")
        query = build_item_search_query(params)
        sort_fields = [list(s.keys())[0] for s in query["sort"]]
        assert "view_count" in sort_fields

    def test_sort_by_newest(self):
        params = ItemSearchParams(sort_by="newest")
        query = build_item_search_query(params)
        sort_fields = [list(s.keys())[0] for s in query["sort"]]
        assert "created_at" in sort_fields

    def test_sort_by_relevance_without_search_uses_popularity(self):
        params = ItemSearchParams(sort_by="relevance")
        query = build_item_search_query(params)
        sort_fields = [list(s.keys())[0] for s in query["sort"]]
        assert "popularity_score" in sort_fields


class TestBuildAutocompleteQuery:
    def test_returns_dict_with_query_and_size(self):
        q = build_autocomplete_query("laptop", limit=5)
        assert "query" in q
        assert q["size"] == 5

    def test_uses_bool_must_multi_match(self):
        q = build_autocomplete_query("lap")
        must = q["query"]["bool"]["must"]
        assert any("multi_match" in clause for clause in must)

    def test_filters_by_is_published(self):
        q = build_autocomplete_query("lap")
        filters = q["query"]["bool"]["filter"]
        assert any("is_published" in str(f) for f in filters)

    def test_source_restricted_to_id_and_title(self):
        q = build_autocomplete_query("lap")
        assert "_source" in q
        assert "id" in q["_source"]
        assert "title" in q["_source"]

    def test_default_limit_is_8(self):
        q = build_autocomplete_query("lap")
        assert q["size"] == 8

    def test_autocomplete_field_in_search_fields(self):
        q = build_autocomplete_query("lap")
        must = q["query"]["bool"]["must"]
        mm = must[0]["multi_match"]
        autocomplete_fields = [f for f in mm["fields"] if "autocomplete" in f]
        assert autocomplete_fields


class TestFunctionScoreDetails:
    def _fn_score(self) -> dict:
        return build_item_search_query(ItemSearchParams(search="test"))["query"]["function_score"]

    def test_boost_mode_is_sum(self):
        assert self._fn_score()["boost_mode"] == "sum"

    def test_score_mode_is_sum(self):
        assert self._fn_score()["score_mode"] == "sum"

    def test_rating_factor_value(self):
        fns = self._fn_score()["functions"]
        fn = next(f for f in fns if f["field_value_factor"]["field"] == "rating_avg")
        assert fn["field_value_factor"]["factor"] == 0.15

    def test_views_factor_value(self):
        fns = self._fn_score()["functions"]
        fn = next(f for f in fns if f["field_value_factor"]["field"] == "view_count")
        assert fn["field_value_factor"]["factor"] == 0.001

    def test_rating_modifier_is_sqrt(self):
        fns = self._fn_score()["functions"]
        fn = next(f for f in fns if f["field_value_factor"]["field"] == "rating_avg")
        assert fn["field_value_factor"]["modifier"] == "sqrt"

    def test_views_modifier_is_log1p(self):
        fns = self._fn_score()["functions"]
        fn = next(f for f in fns if f["field_value_factor"]["field"] == "view_count")
        assert fn["field_value_factor"]["modifier"] == "log1p"

    def test_prefix_length_is_1(self):
        mm = self._fn_score()["query"]["bool"]["must"][0]["multi_match"]
        assert mm["prefix_length"] == 1

    def test_minimum_should_match_75_percent(self):
        mm = self._fn_score()["query"]["bool"]["must"][0]["multi_match"]
        assert mm["minimum_should_match"] == "75%"

    def test_missing_for_rating_is_0(self):
        fns = self._fn_score()["functions"]
        fn = next(f for f in fns if f["field_value_factor"]["field"] == "rating_avg")
        assert fn["field_value_factor"]["missing"] == 0

    def test_missing_for_views_is_0(self):
        fns = self._fn_score()["functions"]
        fn = next(f for f in fns if f["field_value_factor"]["field"] == "view_count")
        assert fn["field_value_factor"]["missing"] == 0

    def test_exactly_two_boost_functions(self):
        assert len(self._fn_score()["functions"]) == 2

    def test_tag_names_field_in_multi_match(self):
        mm = self._fn_score()["query"]["bool"]["must"][0]["multi_match"]
        assert any("tag_names" in f for f in mm["fields"])

    def test_characteristics_name_and_value_in_fields(self):
        mm = self._fn_score()["query"]["bool"]["must"][0]["multi_match"]
        fields_str = " ".join(mm["fields"])
        assert "characteristics.name" in fields_str
        assert "characteristics.value" in fields_str


class TestCombinedFilters:
    def test_category_and_min_rating_produce_two_filters(self):
        params = ItemSearchParams(category_id=uuid4(), min_rating=3.0, is_published=None)
        q = build_item_search_query(params)
        assert len(q["query"]["bool"]["filter"]) == 2

    def test_all_four_filters_combined(self):
        params = ItemSearchParams(
            is_published=True, category_id=uuid4(), tags=["tech"], min_rating=4.0
        )
        q = build_item_search_query(params)
        assert len(q["query"]["bool"]["filter"]) == 4

    def test_multiple_tags_in_terms_filter(self):
        params = ItemSearchParams(tags=["a", "b", "c"], is_published=None)
        q = build_item_search_query(params)
        tag_filter = next(f for f in q["query"]["bool"]["filter"] if "terms" in f)
        assert tag_filter["terms"]["tags"] == ["a", "b", "c"]

    def test_empty_tags_produces_match_all(self):
        params = ItemSearchParams(tags=[], is_published=None)
        q = build_item_search_query(params)
        assert "match_all" in q["query"]

    def test_category_id_cast_to_str(self):
        cat_id = uuid4()
        params = ItemSearchParams(category_id=cat_id, is_published=None)
        q = build_item_search_query(params)
        cat_filter = next(
            f for f in q["query"]["bool"]["filter"]
            if "term" in f and "category_id" in f["term"]
        )
        assert cat_filter["term"]["category_id"] == str(cat_id)

    def test_is_published_false_filter(self):
        params = ItemSearchParams(is_published=False)
        q = build_item_search_query(params)
        assert {"term": {"is_published": False}} in q["query"]["bool"]["filter"]

    def test_search_with_category_filter_uses_function_score(self):
        params = ItemSearchParams(search="laptop", category_id=uuid4())
        q = build_item_search_query(params)
        assert "function_score" in q["query"]
        fn_score = q["query"]["function_score"]
        assert "filter" in fn_score["query"]["bool"]


@pytest.mark.parametrize("sort_by,expected_first_key", [
    ("rating", "rating_avg"),
    ("views", "view_count"),
    ("newest", "created_at"),
    ("popularity", "popularity_score"),
])
def test_sort_option_parametrized(sort_by: str, expected_first_key: str) -> None:
    params = ItemSearchParams(sort_by=sort_by)
    q = build_item_search_query(params)
    assert list(q["sort"][0].keys())[0] == expected_first_key


def test_sort_relevance_with_search_has_score_first() -> None:
    q = build_item_search_query(ItemSearchParams(search="test", sort_by="relevance"))
    assert list(q["sort"][0].keys())[0] == "_score"


def test_sort_relevance_with_search_popularity_as_secondary() -> None:
    q = build_item_search_query(ItemSearchParams(search="test", sort_by="relevance"))
    assert list(q["sort"][1].keys())[0] == "popularity_score"


def test_sort_rating_includes_view_count_as_secondary() -> None:
    q = build_item_search_query(ItemSearchParams(sort_by="rating"))
    sort_keys = [list(s.keys())[0] for s in q["sort"]]
    assert "view_count" in sort_keys


def test_sort_views_is_descending() -> None:
    q = build_item_search_query(ItemSearchParams(sort_by="views"))
    assert q["sort"][0]["view_count"]["order"] == "desc"


def test_sort_newest_is_descending() -> None:
    q = build_item_search_query(ItemSearchParams(sort_by="newest"))
    assert q["sort"][0]["created_at"]["order"] == "desc"


def test_default_pagination_from_is_0() -> None:
    q = build_item_search_query(ItemSearchParams())
    assert q["from"] == 0


def test_default_pagination_size_is_20() -> None:
    q = build_item_search_query(ItemSearchParams())
    assert q["size"] == 20
