import math
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.backend.search.infrastructure.elasticsearch.sync.item_sync import _popularity_score


class TestPopularityScore:
    def test_zero_rating_zero_views(self):
        score = _popularity_score(0.0, 0)
        assert score == 0.0

    def test_high_rating_no_views(self):
        score = _popularity_score(5.0, 0)
        assert abs(score - 5.0 * 0.6) < 0.001

    def test_no_rating_many_views(self):
        score = _popularity_score(0.0, 1000)
        expected = math.log1p(1000) * 0.4
        assert abs(score - expected) < 0.001

    def test_combined(self):
        score = _popularity_score(4.0, 100)
        expected = 4.0 * 0.6 + math.log1p(100) * 0.4
        assert abs(score - round(expected, 4)) < 0.001

    def test_result_is_rounded_to_4_decimals(self):
        score = _popularity_score(3.7, 57)
        assert score == round(score, 4)


class TestIndexItem:
    async def test_index_item_calls_es_index(self):
        from src.backend.search.infrastructure.elasticsearch.sync.item_sync import index_item

        item_id = uuid4()
        mock_session = AsyncMock()
        mock_es = AsyncMock()

        doc = {
            "id": str(item_id),
            "title": "Test",
            "short_description": "s",
            "description": "d",
            "category_id": str(uuid4()),
            "category_name": "Cat",
            "tags": [],
            "tag_names": "",
            "rating_avg": 0.0,
            "view_count": 0,
            "is_published": True,
            "created_at": None,
            "updated_at": None,
            "characteristics": [],
            "popularity_score": 0.0,
            "preview_image_key": None,
            "marketplace_links": None,
        }

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            return_value=doc,
        ):
            result = await index_item(
                item_id=item_id,
                session=mock_session,
                es=mock_es,
                index_name="coremarket_items",
            )

        assert result is True
        mock_es.index.assert_called_once_with(
            index="coremarket_items",
            id=str(item_id),
            document=doc,
        )

    async def test_index_item_returns_false_when_not_found(self):
        from src.backend.search.infrastructure.elasticsearch.sync.item_sync import index_item

        item_id = uuid4()
        mock_session = AsyncMock()
        mock_es = AsyncMock()

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            return_value=None,
        ):
            result = await index_item(
                item_id=item_id,
                session=mock_session,
                es=mock_es,
                index_name="coremarket_items",
            )

        assert result is False
        mock_es.index.assert_not_called()


class TestDeleteItemFromIndex:
    async def test_delete_calls_es_delete_with_ignore_status(self):
        from src.backend.search.infrastructure.elasticsearch.sync.item_sync import delete_item_from_index

        mock_es = AsyncMock()
        item_id = str(uuid4())

        await delete_item_from_index(item_id=item_id, es=mock_es, index_name="coremarket_items")

        mock_es.delete.assert_called_once_with(
            index="coremarket_items", id=item_id, ignore_status=404
        )

    async def test_delete_uses_ignore_status_404(self):
        from src.backend.search.infrastructure.elasticsearch.sync.item_sync import delete_item_from_index

        mock_es = AsyncMock()

        await delete_item_from_index(item_id="any-id", es=mock_es, index_name="coremarket_items")

        call_kwargs = mock_es.delete.call_args.kwargs
        assert call_kwargs.get("ignore_status") == 404
