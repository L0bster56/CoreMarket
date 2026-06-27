"""Tests for delete_item_task Celery task (Elasticsearch deletion)."""
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry


# ── Task configuration ─────────────────────────────────────────────────────────

class TestDeleteItemTaskConfig:
    def test_task_name(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        assert delete_item_task.name == "coremarket.tasks.delete_item_from_index"

    def test_max_retries(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        assert delete_item_task.max_retries == 3


# ── SEARCH_ENABLED=False skip ──────────────────────────────────────────────────

class TestDeleteItemTaskSkip:
    def test_skips_when_search_disabled(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        with patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=False)
            result = delete_item_task.apply(args=["item-skip"])

        assert result.result == {"skipped": True, "reason": "search_disabled"}

    def test_skip_does_not_call_asyncio_run(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch("src.backend.application.tasks.search_sync.asyncio.run") as mock_run:
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=False)
            delete_item_task.apply(args=["item-skip-no-run"])

        mock_run.assert_not_called()


# ── Success paths ──────────────────────────────────────────────────────────────

class TestDeleteItemTaskSuccess:
    def test_returns_deleted_true(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 return_value={"item_id": "item-del-uuid", "deleted": True},
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            result = delete_item_task.apply(args=["item-del-uuid"])

        assert result.result == {"item_id": "item-del-uuid", "deleted": True}

    def test_task_successful(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 return_value={"item_id": "item-ok", "deleted": True},
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            result = delete_item_task.apply(args=["item-ok"])

        assert result.successful()


# ── Retry behaviour ────────────────────────────────────────────────────────────

class TestDeleteItemTaskRetry:
    def test_retries_on_transient_es_error(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 side_effect=ConnectionError("ES unavailable during delete"),
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            with pytest.raises(Retry):
                delete_item_task.apply(args=["item-del-retry"], throw=True)

    def test_exhausted_retries_raises_original_exception(self):
        from src.backend.application.tasks.search_sync import delete_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 side_effect=RuntimeError("ES hard error"),
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            with pytest.raises(RuntimeError, match="ES hard error"):
                delete_item_task.apply(args=["item-del-fail"], retries=3, throw=True)


# ── Logging ────────────────────────────────────────────────────────────────────

class TestDeleteItemTaskLogging:
    def test_logs_task_started(self, caplog):
        from src.backend.application.tasks.search_sync import delete_item_task

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.search_sync"):
            with patch("src.backend.config.get_settings") as mock_cfg, \
                 patch(
                     "src.backend.application.tasks.search_sync.asyncio.run",
                     return_value={"item_id": "log-del", "deleted": True},
                 ):
                mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
                delete_item_task.apply(args=["log-del"])

        assert any("task_started" in r.message for r in caplog.records)

    def test_logs_task_completed(self, caplog):
        from src.backend.application.tasks.search_sync import delete_item_task

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.search_sync"):
            with patch("src.backend.config.get_settings") as mock_cfg, \
                 patch(
                     "src.backend.application.tasks.search_sync.asyncio.run",
                     return_value={"item_id": "log-del", "deleted": True},
                 ):
                mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
                delete_item_task.apply(args=["log-del"])

        assert any("task_completed" in r.message for r in caplog.records)


# ── Async ES helper ────────────────────────────────────────────────────────────

class TestDeleteItemAsync:
    """Tests for _delete_item_async — verifies delete_item_from_index is called."""

    async def test_calls_delete_item_from_index(self):
        from src.backend.application.tasks.search_sync import _delete_item_async

        mock_es = AsyncMock()
        mock_index = MagicMock(index_name="coremarket_items")

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.client.get_es_client",
                 return_value=mock_es,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex",
                 return_value=mock_index,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.sync.item_sync.delete_item_from_index",
                 new_callable=AsyncMock,
             ) as mock_delete:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                ELASTICSEARCH_INDEX_PREFIX="coremarket",
            )
            result = await _delete_item_async("item-del-uuid")

        assert result == {"item_id": "item-del-uuid", "deleted": True}
        mock_delete.assert_called_once()

    async def test_returns_deleted_true_and_item_id(self):
        from src.backend.application.tasks.search_sync import _delete_item_async

        mock_es = AsyncMock()
        mock_index = MagicMock(index_name="coremarket_items")

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.client.get_es_client",
                 return_value=mock_es,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex",
                 return_value=mock_index,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.sync.item_sync.delete_item_from_index",
                 new_callable=AsyncMock,
             ):
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                ELASTICSEARCH_INDEX_PREFIX="coremarket",
            )
            result = await _delete_item_async("any-item-id")

        assert result["deleted"] is True
        assert result["item_id"] == "any-item-id"

    async def test_delete_called_with_correct_index_name(self):
        from src.backend.application.tasks.search_sync import _delete_item_async

        mock_es = AsyncMock()
        mock_index = MagicMock(index_name="coremarket_test_items")

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.client.get_es_client",
                 return_value=mock_es,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex",
                 return_value=mock_index,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.sync.item_sync.delete_item_from_index",
                 new_callable=AsyncMock,
             ) as mock_delete:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                ELASTICSEARCH_INDEX_PREFIX="coremarket_test",
            )
            await _delete_item_async("item-id-idx")

        call_kwargs = mock_delete.call_args.kwargs
        assert call_kwargs["index_name"] == "coremarket_test_items"
        assert call_kwargs["item_id"] == "item-id-idx"
