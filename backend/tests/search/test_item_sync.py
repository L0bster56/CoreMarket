import math
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.backend.search.infrastructure.elasticsearch.sync.item_sync import (
    _popularity_score,
    build_item_document,
    bulk_reindex,
    delete_item_from_index,
    index_item,
)


class TestPopularityScore:
    def test_zero_rating_and_views(self):
        score = _popularity_score(0.0, 0)
        assert score >= 0.0

    def test_higher_rating_increases_score(self):
        low = _popularity_score(1.0, 100)
        high = _popularity_score(5.0, 100)
        assert high > low

    def test_higher_views_increases_score(self):
        low = _popularity_score(3.0, 10)
        high = _popularity_score(3.0, 1000)
        assert high > low

    def test_formula_rating_0_6_views_0_4(self):
        rating = 4.0
        views = 100
        expected = round(rating * 0.6 + math.log1p(views) * 0.4, 4)
        assert _popularity_score(rating, views) == expected

    def test_returns_float(self):
        assert isinstance(_popularity_score(3.5, 50), float)


class TestIndexItem:
    async def test_returns_true_when_item_found(self):
        item_id = uuid4()
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        doc = {"id": str(item_id), "title": "Test Item"}

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document"
        ) as mock_build:
            mock_build.return_value = doc
            result = await index_item(
                item_id=item_id,
                session=mock_session,
                es=mock_es,
                index_name="test-items",
            )

        assert result is True
        mock_es.index.assert_called_once_with(
            index="test-items", id=str(item_id), document=doc
        )

    async def test_returns_false_when_item_not_found(self):
        item_id = uuid4()
        mock_session = AsyncMock()
        mock_es = AsyncMock()

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document"
        ) as mock_build:
            mock_build.return_value = None
            result = await index_item(
                item_id=item_id,
                session=mock_session,
                es=mock_es,
                index_name="test-items",
            )

        assert result is False
        mock_es.index.assert_not_called()


class TestDeleteItemFromIndex:
    async def test_calls_es_delete(self):
        mock_es = AsyncMock()
        await delete_item_from_index(
            item_id="item-uuid-123",
            es=mock_es,
            index_name="test-items",
        )
        mock_es.delete.assert_called_once_with(
            index="test-items", id="item-uuid-123", ignore_status=404
        )

    async def test_ignores_404_errors(self):
        mock_es = AsyncMock()
        await delete_item_from_index(
            item_id="nonexistent-id",
            es=mock_es,
            index_name="test-items",
        )
        call_kwargs = mock_es.delete.call_args[1]
        assert call_kwargs.get("ignore_status") == 404


class TestBulkReindex:
    async def test_returns_zero_for_empty_db(self):
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        mock_result = MagicMock()
        mock_result.all.return_value = []
        mock_session.execute.return_value = mock_result

        indexed = await bulk_reindex(
            session=mock_session,
            es=mock_es,
            index_name="test-items",
        )

        assert indexed == 0

    async def test_indexes_items_in_batches(self):
        from unittest.mock import patch

        item_ids = [uuid4() for _ in range(3)]
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        mock_result = MagicMock()
        rows = [MagicMock(id=id_) for id_ in item_ids]
        mock_result.all.return_value = rows
        mock_session.execute.return_value = mock_result
        mock_es.bulk.return_value = {"errors": False, "items": []}

        docs = [{"id": str(id_), "title": f"Item {i}"} for i, id_ in enumerate(item_ids)]

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            side_effect=docs,
        ):
            indexed = await bulk_reindex(
                session=mock_session,
                es=mock_es,
                index_name="test-items",
            )

        assert indexed == 3
        mock_es.bulk.assert_called_once()


class TestBulkReindexEdgeCases:
    async def test_none_docs_skipped(self):
        item_ids = [uuid4(), uuid4(), uuid4()]
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        r = MagicMock()
        r.all.return_value = [MagicMock(id=id_) for id_ in item_ids]
        mock_session.execute.return_value = r
        mock_es.bulk.return_value = {"errors": False, "items": []}

        # Middle item is not found in DB → None
        docs = [{"id": str(item_ids[0]), "title": "A"}, None, {"id": str(item_ids[2]), "title": "C"}]

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            side_effect=docs,
        ):
            indexed = await bulk_reindex(
                session=mock_session, es=mock_es, index_name="test-items"
            )

        assert indexed == 2

    async def test_bulk_errors_do_not_raise(self):
        item_id = uuid4()
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        r = MagicMock()
        r.all.return_value = [MagicMock(id=item_id)]
        mock_session.execute.return_value = r

        error_response = {
            "errors": True,
            "items": [{"index": {"error": {"reason": "shard_failure", "type": "shard_error"}}}],
        }
        mock_es.bulk.return_value = error_response

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            return_value={"id": str(item_id), "title": "T"},
        ):
            indexed = await bulk_reindex(
                session=mock_session, es=mock_es, index_name="test-items"
            )

        assert indexed == 1

    async def test_large_dataset_two_batches(self):
        item_ids = [uuid4() for _ in range(150)]
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        r = MagicMock()
        r.all.return_value = [MagicMock(id=id_) for id_ in item_ids]
        mock_session.execute.return_value = r
        mock_es.bulk.return_value = {"errors": False, "items": []}

        docs = [{"id": str(id_), "title": "Item"} for id_ in item_ids]

        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            side_effect=docs,
        ):
            indexed = await bulk_reindex(
                session=mock_session, es=mock_es, index_name="test-items"
            )

        assert indexed == 150
        assert mock_es.bulk.call_count == 2

    async def test_operations_alternate_action_and_doc(self):
        item_id = uuid4()
        mock_session = AsyncMock()
        mock_es = AsyncMock()
        r = MagicMock()
        r.all.return_value = [MagicMock(id=item_id)]
        mock_session.execute.return_value = r
        mock_es.bulk.return_value = {"errors": False, "items": []}

        doc = {"id": str(item_id), "title": "T"}
        with patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.build_item_document",
            return_value=doc,
        ):
            await bulk_reindex(session=mock_session, es=mock_es, index_name="idx")

        operations = mock_es.bulk.call_args.kwargs["operations"]
        assert operations[0] == {"index": {"_index": "idx", "_id": str(item_id)}}
        assert operations[1] == doc


class TestBuildItemDocument:
    def _make_item(self, item_id, cat_id=None, characteristics=None):
        item = MagicMock()
        item.id = item_id
        item.name = "Test Item"
        item.short_description = "Short desc"
        item.description = "Long description"
        item.category_id = cat_id if cat_id is not None else uuid4()
        item.is_published = True
        item.view_count = 42
        dt = datetime(2026, 1, 1, tzinfo=timezone.utc)
        item.created_at = dt
        item.updated_at = dt
        item.characteristics = characteristics or []
        item.marketplace_links = None
        return item

    def _make_session(self, item, category_name="Category", tag_rows=None, avg_rating=4.0, preview=None):
        mock_session = AsyncMock()
        r_item = MagicMock()
        r_item.scalar_one_or_none.return_value = item
        r_cat = MagicMock()
        r_cat.scalar_one_or_none.return_value = category_name
        r_tags = MagicMock()
        r_tags.all.return_value = tag_rows or []
        r_rating = MagicMock()
        r_rating.scalar_one_or_none.return_value = avg_rating
        r_gallery = MagicMock()
        r_gallery.scalar_one_or_none.return_value = preview
        mock_session.execute.side_effect = [r_item, r_cat, r_tags, r_rating, r_gallery]
        return mock_session

    async def test_returns_none_when_item_not_found(self):
        mock_session = AsyncMock()
        r = MagicMock()
        r.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = r
        assert await build_item_document(uuid4(), mock_session) is None

    async def test_title_comes_from_item_name(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["title"] == "Test Item"

    async def test_id_is_stringified_uuid(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["id"] == str(item_id)

    async def test_category_name_fetched_from_db(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item, category_name="Electronics"))
        assert doc["category_name"] == "Electronics"

    async def test_category_id_cast_to_str(self):
        item_id = uuid4()
        cat_id = uuid4()
        item = self._make_item(item_id, cat_id=cat_id)
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["category_id"] == str(cat_id)

    async def test_tag_slugs_in_tags_field(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        t1, t2 = MagicMock(), MagicMock()
        t1.slug, t1.name = "tech", "Technology"
        t2.slug, t2.name = "ai", "AI"
        doc = await build_item_document(item_id, self._make_session(item, tag_rows=[t1, t2]))
        assert doc["tags"] == ["tech", "ai"]

    async def test_tag_names_space_joined(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        t1, t2 = MagicMock(), MagicMock()
        t1.slug, t1.name = "tech", "Technology"
        t2.slug, t2.name = "ai", "AI"
        doc = await build_item_document(item_id, self._make_session(item, tag_rows=[t1, t2]))
        assert "Technology" in doc["tag_names"]
        assert "AI" in doc["tag_names"]

    async def test_no_tags_gives_empty_list_and_string(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item, tag_rows=[]))
        assert doc["tags"] == []
        assert doc["tag_names"] == ""

    async def test_rating_avg_from_db(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item, avg_rating=4.8))
        assert doc["rating_avg"] == 4.8

    async def test_rating_none_defaults_to_zero(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item, avg_rating=None))
        assert doc["rating_avg"] == 0.0

    async def test_preview_image_key_from_gallery(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item, preview="items/abc.jpg"))
        assert doc["preview_image_key"] == "items/abc.jpg"

    async def test_no_gallery_preview_is_none(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item, preview=None))
        assert doc["preview_image_key"] is None

    async def test_characteristics_mapped_to_dicts(self):
        item_id = uuid4()
        char = MagicMock()
        char.name = "RAM"
        char.value = "16GB"
        char.group = "Memory"
        item = self._make_item(item_id, characteristics=[char])
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["characteristics"] == [{"name": "RAM", "value": "16GB", "group": "Memory"}]

    async def test_empty_characteristics_gives_empty_list(self):
        item_id = uuid4()
        item = self._make_item(item_id, characteristics=[])
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["characteristics"] == []

    async def test_popularity_score_calculated_correctly(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.view_count = 100
        doc = await build_item_document(item_id, self._make_session(item, avg_rating=4.0))
        assert doc["popularity_score"] == _popularity_score(4.0, 100)

    async def test_marketplace_links_included(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.marketplace_links = {"amazon": "https://amazon.com/test"}
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["marketplace_links"] == {"amazon": "https://amazon.com/test"}

    async def test_view_count_in_doc(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.view_count = 888
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["view_count"] == 888

    async def test_is_published_true(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.is_published = True
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["is_published"] is True

    async def test_is_published_false(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.is_published = False
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["is_published"] is False

    async def test_created_at_isoformat(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        dt = datetime(2026, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
        item.created_at = dt
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["created_at"] == dt.isoformat()

    async def test_created_at_none_gives_none(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.created_at = None
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["created_at"] is None

    async def test_no_category_id_skips_category_query(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.category_id = None

        mock_session = AsyncMock()
        r_item = MagicMock()
        r_item.scalar_one_or_none.return_value = item
        r_tags = MagicMock()
        r_tags.all.return_value = []
        r_rating = MagicMock()
        r_rating.scalar_one_or_none.return_value = 0.0
        r_gallery = MagicMock()
        r_gallery.scalar_one_or_none.return_value = None
        mock_session.execute.side_effect = [r_item, r_tags, r_rating, r_gallery]

        doc = await build_item_document(item_id, mock_session)
        assert doc["category_name"] is None
        assert mock_session.execute.call_count == 4

    async def test_short_description_in_doc(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        item.short_description = "My short desc"
        doc = await build_item_document(item_id, self._make_session(item))
        assert doc["short_description"] == "My short desc"

    async def test_all_required_keys_present(self):
        item_id = uuid4()
        item = self._make_item(item_id)
        doc = await build_item_document(item_id, self._make_session(item))
        required_keys = {
            "id", "title", "short_description", "description",
            "category_id", "category_name", "tags", "tag_names",
            "rating_avg", "view_count", "is_published",
            "created_at", "updated_at", "characteristics",
            "popularity_score", "preview_image_key", "marketplace_links",
        }
        assert required_keys.issubset(doc.keys())
