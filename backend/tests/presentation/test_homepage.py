"""
Tests for GET /api/v1/homepage.

Covers:
- Redis cache hit: snapshot returned directly, no DB call
- Redis cache miss: fallback to DB aggregation, snapshot refresh triggered
- Response structure: all required fields present in both paths
- Error handling: 503 when both Redis and DB fail; Redis error falls through to DB
"""
from __future__ import annotations

import json
import time
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.backend.main import app

ENDPOINT = "/api/v1/homepage"
_MODULE = "src.backend.presentation.api.v1.homepage.router"

_SNAPSHOT = {
    "computed_at": time.time() - 30,
    "featured_items": [
        {
            "id": "item-1",
            "title": "Top Item",
            "short_description": "desc",
            "category_id": "cat-1",
            "view_count": 500,
            "avg_rating": 4.5,
            "preview_image": None,
            "created_at": "2025-01-01T00:00:00",
        }
    ],
    "top_rated_items": [
        {
            "id": "item-2",
            "title": "Best Rated",
            "short_description": "top",
            "category_id": "cat-1",
            "view_count": 100,
            "avg_rating": 5.0,
            "preview_image": None,
            "created_at": "2025-01-01T00:00:00",
        }
    ],
    "categories": [
        {"id": "cat-1", "name": "Electronics", "slug": "electronics", "item_count": 42}
    ],
    "recent_posts": [
        {
            "id": "post-1",
            "title": "Blog Post",
            "slug": "blog-post",
            "cover_image_url": None,
            "created_at": "2025-01-01T00:00:00",
            "seo_description": "A post",
        }
    ],
    "stats": {"total_items": 100, "total_categories": 5, "total_posts": 20},
}

_DB_RESULT = {
    "computed_at": time.time(),
    "featured_items": [
        {
            "id": "db-item",
            "title": "DB Item",
            "short_description": "from db",
            "category_id": "cat-1",
            "view_count": 10,
            "avg_rating": None,
            "preview_image": None,
            "created_at": "2025-06-01T00:00:00",
        }
    ],
    "top_rated_items": [],
    "categories": [
        {"id": "cat-1", "name": "Electronics", "slug": "electronics", "item_count": 1}
    ],
    "recent_posts": [],
    "stats": {"total_items": 1, "total_categories": 1, "total_posts": 0},
}


def _make_redis(raw: str | None) -> AsyncMock:
    client = AsyncMock()
    client.get = AsyncMock(return_value=raw)
    client.aclose = AsyncMock()
    return client


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


class TestHomepageCacheHit:
    async def test_returns_200(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis):
            response = await client.get(ENDPOINT)
        assert response.status_code == 200

    async def test_source_is_cache(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis):
            response = await client.get(ENDPOINT)
        assert response.json()["source"] == "cache"

    async def test_no_db_fallback_called(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", new_callable=AsyncMock) as mock_db:
            await client.get(ENDPOINT)
        mock_db.assert_not_awaited()

    async def test_snapshot_refresh_not_triggered(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._trigger_snapshot_refresh") as mock_refresh:
            await client.get(ENDPOINT)
        mock_refresh.assert_not_called()

    async def test_featured_items_returned_from_cache(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis):
            response = await client.get(ENDPOINT)
        assert response.json()["featured_items"] == _SNAPSHOT["featured_items"]

    async def test_stats_returned_from_cache(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis):
            response = await client.get(ENDPOINT)
        assert response.json()["stats"] == _SNAPSHOT["stats"]

    async def test_redis_connection_closed_after_hit(self, client):
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis):
            await client.get(ENDPOINT)
        redis.aclose.assert_awaited_once()


class TestHomepageCacheMiss:
    async def test_returns_200_on_db_fallback(self, client):
        redis = _make_redis(None)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=dict(_DB_RESULT))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        assert response.status_code == 200

    async def test_source_is_db_fallback(self, client):
        redis = _make_redis(None)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=dict(_DB_RESULT))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        assert response.json()["source"] == "db_fallback"

    async def test_inline_query_is_called(self, client):
        redis = _make_redis(None)
        mock_db = AsyncMock(return_value=dict(_DB_RESULT))
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", mock_db), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            await client.get(ENDPOINT)
        mock_db.assert_awaited_once()

    async def test_snapshot_refresh_is_triggered(self, client):
        redis = _make_redis(None)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=dict(_DB_RESULT))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh") as mock_refresh:
            await client.get(ENDPOINT)
        mock_refresh.assert_called_once()

    async def test_db_data_returned_in_response(self, client):
        redis = _make_redis(None)
        db_result = dict(_DB_RESULT)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=db_result)), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        data = response.json()
        assert data["stats"]["total_items"] == db_result["stats"]["total_items"]
        assert data["stats"]["total_categories"] == db_result["stats"]["total_categories"]

    async def test_featured_items_from_db(self, client):
        redis = _make_redis(None)
        db_result = dict(_DB_RESULT)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=db_result)), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        assert response.json()["featured_items"] == db_result["featured_items"]


class TestHomepageResponseStructure:
    """Verify all required fields exist regardless of cache source."""

    async def _get_from_cache(self, client) -> dict:
        redis = _make_redis(json.dumps(_SNAPSHOT))
        with patch(f"{_MODULE}._get_redis", return_value=redis):
            response = await client.get(ENDPOINT)
        return response.json()

    async def test_has_source_field(self, client):
        data = await self._get_from_cache(client)
        assert "source" in data

    async def test_has_computed_at(self, client):
        data = await self._get_from_cache(client)
        assert "computed_at" in data

    async def test_has_featured_items(self, client):
        data = await self._get_from_cache(client)
        assert "featured_items" in data

    async def test_has_top_rated_items(self, client):
        data = await self._get_from_cache(client)
        assert "top_rated_items" in data

    async def test_has_categories(self, client):
        data = await self._get_from_cache(client)
        assert "categories" in data

    async def test_has_recent_posts(self, client):
        data = await self._get_from_cache(client)
        assert "recent_posts" in data

    async def test_has_stats(self, client):
        data = await self._get_from_cache(client)
        assert "stats" in data

    async def test_stats_has_total_items(self, client):
        data = await self._get_from_cache(client)
        assert "total_items" in data["stats"]

    async def test_stats_has_total_categories(self, client):
        data = await self._get_from_cache(client)
        assert "total_categories" in data["stats"]

    async def test_stats_has_total_posts(self, client):
        data = await self._get_from_cache(client)
        assert "total_posts" in data["stats"]

    async def test_featured_items_is_list(self, client):
        data = await self._get_from_cache(client)
        assert isinstance(data["featured_items"], list)

    async def test_categories_is_list(self, client):
        data = await self._get_from_cache(client)
        assert isinstance(data["categories"], list)

    async def test_stats_values_are_numeric(self, client):
        data = await self._get_from_cache(client)
        stats = data["stats"]
        assert isinstance(stats["total_items"], int)
        assert isinstance(stats["total_categories"], int)
        assert isinstance(stats["total_posts"], int)

    async def test_db_fallback_also_has_all_fields(self, client):
        redis = _make_redis(None)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=dict(_DB_RESULT))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        data = response.json()
        for field in ("source", "featured_items", "top_rated_items",
                      "categories", "recent_posts", "stats"):
            assert field in data, f"Missing field: {field}"


class TestHomepageErrorHandling:
    async def test_503_when_db_also_fails(self, client):
        redis = _make_redis(None)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(side_effect=Exception("DB down"))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        assert response.status_code == 503

    async def test_503_response_has_detail_field(self, client):
        redis = _make_redis(None)
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(side_effect=Exception("DB down"))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        assert "detail" in response.json()

    async def test_redis_error_falls_through_to_db(self, client):
        redis = AsyncMock()
        redis.get = AsyncMock(side_effect=ConnectionError("Redis down"))
        redis.aclose = AsyncMock()
        mock_db = AsyncMock(return_value=dict(_DB_RESULT))
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", mock_db), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        mock_db.assert_awaited_once()
        assert response.status_code == 200

    async def test_redis_error_still_returns_db_fallback_source(self, client):
        redis = AsyncMock()
        redis.get = AsyncMock(side_effect=ConnectionError("Redis down"))
        redis.aclose = AsyncMock()
        with patch(f"{_MODULE}._get_redis", return_value=redis), \
             patch(f"{_MODULE}._inline_query", AsyncMock(return_value=dict(_DB_RESULT))), \
             patch(f"{_MODULE}._trigger_snapshot_refresh"):
            response = await client.get(ENDPOINT)
        assert response.json()["source"] == "db_fallback"
