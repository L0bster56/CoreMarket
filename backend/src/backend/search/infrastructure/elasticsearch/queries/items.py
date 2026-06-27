from src.backend.search.domain.value_objects import ItemSearchParams


def build_item_search_query(params: ItemSearchParams) -> dict:
    filters = _build_filters(params)

    if params.search:
        query: dict = {
            "function_score": {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": params.search,
                                    "fields": [
                                        "title^4",
                                        "title.autocomplete^2",
                                        "short_description^2",
                                        "description",
                                        "tags.text^1.5",
                                        "tag_names^1.5",
                                        "category_name.text",
                                        "characteristics.name",
                                        "characteristics.value",
                                    ],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO",
                                    "prefix_length": 1,
                                    "minimum_should_match": "75%",
                                }
                            }
                        ],
                        "filter": filters,
                    }
                },
                "functions": [
                    {
                        "field_value_factor": {
                            "field": "rating_avg",
                            "factor": 0.15,
                            "modifier": "sqrt",
                            "missing": 0,
                        }
                    },
                    {
                        "field_value_factor": {
                            "field": "view_count",
                            "factor": 0.001,
                            "modifier": "log1p",
                            "missing": 0,
                        }
                    },
                ],
                "boost_mode": "sum",
                "score_mode": "sum",
            }
        }
    elif filters:
        query = {"bool": {"filter": filters}}
    else:
        query = {"match_all": {}}

    return {
        "query": query,
        "sort": _build_sort(params.sort_by, has_search=bool(params.search)),
        "from": params.offset,
        "size": params.limit,
    }


def build_autocomplete_query(query_str: str, limit: int = 8) -> dict:
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": query_str,
                            "fields": ["title.autocomplete^3", "title^4"],
                            "type": "best_fields",
                        }
                    }
                ],
                "filter": [{"term": {"is_published": True}}],
            }
        },
        "size": limit,
        "_source": ["id", "title"],
    }


def _build_filters(params: ItemSearchParams) -> list:
    filters: list = []

    if params.is_published is not None:
        filters.append({"term": {"is_published": params.is_published}})

    if params.category_id is not None:
        filters.append({"term": {"category_id": str(params.category_id)}})

    if params.tags:
        filters.append({"terms": {"tags": params.tags}})

    if params.min_rating is not None:
        filters.append({"range": {"rating_avg": {"gte": params.min_rating}}})

    return filters


def _build_sort(sort_by: str, has_search: bool = False) -> list:
    if sort_by == "relevance" and has_search:
        return [{"_score": {"order": "desc"}}, {"popularity_score": {"order": "desc"}}]
    if sort_by == "rating":
        return [{"rating_avg": {"order": "desc"}}, {"view_count": {"order": "desc"}}]
    if sort_by == "views":
        return [{"view_count": {"order": "desc"}}]
    if sort_by == "newest":
        return [{"created_at": {"order": "desc"}}]
    return [{"popularity_score": {"order": "desc"}}]
