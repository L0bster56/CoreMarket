"""Tests for index_item_task Celery task."""
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry


# ── Task configuration ─────────────────────────────────────────────────────────

class TestIndexItemTaskConfig:
    def test_task_name(self):
        from src.backend.application.tasks.search_sync import index_item_task

        assert index_item_task.name == "coremarket.tasks.index_item"

    def test_max_retries(self):
        from src.backend.application.tasks.search_sync import index_item_task

        assert index_item_task.max_retries == 3


# ── SEARCH_ENABLED=False skip ──────────────────────────────────────────────────

class TestIndexItemTaskSkip:
    def test_skips_when_search_disabled(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=False)
            result = index_item_task.apply(args=("item-uuid",))

        assert result.result == {"skipped": True, "reason": "search_disabled"}

    def test_skip_does_not_call_asyncio_run(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch("src.backend.application.tasks.search_sync.asyncio.run") as mock_run:
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=False)
            index_item_task.apply(args=("item-skip",))

        mock_run.assert_not_called()


# ── Success paths ──────────────────────────────────────────────────────────────

class TestIndexItemTaskSuccess:
    def test_returns_indexed_true(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 return_value={"item_id": "item-uuid", "indexed": True},
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            result = index_item_task.apply(args=("item-uuid",))

        assert result.result["indexed"] is True

    def test_returns_item_id_in_result(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 return_value={"item_id": "item-uuid-abc", "indexed": True},
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            result = index_item_task.apply(args=("item-uuid-abc",))

        assert result.result["item_id"] == "item-uuid-abc"

    def test_task_successful(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 return_value={"item_id": "item-uuid", "indexed": True},
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            result = index_item_task.apply(args=("item-uuid",))

        assert result.successful()


# ── Retry behaviour ────────────────────────────────────────────────────────────

class TestIndexItemTaskRetry:
    def test_retries_on_es_connection_error(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 side_effect=ConnectionError("ES unavailable"),
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            with pytest.raises(Retry):
                index_item_task.apply(args=("item-uuid",), throw=True)

    def test_retries_on_generic_exception(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 side_effect=Exception("ES indexing failed"),
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            with pytest.raises(Retry):
                index_item_task.apply(args=("item-uuid",), throw=True)

    def test_exhausted_retries_raises_original_exception(self):
        from src.backend.application.tasks.search_sync import index_item_task

        with patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.application.tasks.search_sync.asyncio.run",
                 side_effect=RuntimeError("ES hard failure"),
             ):
            mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
            with pytest.raises(RuntimeError, match="ES hard failure"):
                index_item_task.apply(args=("item-uuid",), retries=3, throw=True)


# ── Logging ────────────────────────────────────────────────────────────────────

class TestIndexItemTaskLogging:
    def test_logs_task_started(self, caplog):
        from src.backend.application.tasks.search_sync import index_item_task

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.search_sync"):
            with patch("src.backend.config.get_settings") as mock_cfg, \
                 patch(
                     "src.backend.application.tasks.search_sync.asyncio.run",
                     return_value={"item_id": "log-item", "indexed": True},
                 ):
                mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
                index_item_task.apply(args=("log-item",))

        assert any("task_started" in r.message for r in caplog.records)

    def test_logs_task_completed(self, caplog):
        from src.backend.application.tasks.search_sync import index_item_task

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.search_sync"):
            with patch("src.backend.config.get_settings") as mock_cfg, \
                 patch(
                     "src.backend.application.tasks.search_sync.asyncio.run",
                     return_value={"item_id": "log-item", "indexed": True},
                 ):
                mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
                index_item_task.apply(args=("log-item",))

        assert any("task_completed" in r.message for r in caplog.records)

    def test_logs_task_failed(self, caplog):
        from src.backend.application.tasks.search_sync import index_item_task

        with caplog.at_level(logging.ERROR, logger="coremarket.tasks.search_sync"):
            with patch("src.backend.config.get_settings") as mock_cfg, \
                 patch(
                     "src.backend.application.tasks.search_sync.asyncio.run",
                     side_effect=RuntimeError("ES error"),
                 ):
                mock_cfg.return_value = MagicMock(SEARCH_ENABLED=True)
                try:
                    index_item_task.apply(args=("fail-item",), throw=True)
                except Exception:
                    pass

        assert any("task_failed" in r.message for r in caplog.records)


# ── Async ES helper ────────────────────────────────────────────────────────────

class TestIndexItemAsync:
    """Tests for _index_item_async — verifies ES indexing call and return value."""

    async def test_calls_index_item_and_returns_result(self):
        from src.backend.application.tasks.search_sync import _index_item_async

        item_uuid = "550e8400-e29b-41d4-a716-446655440000"

        mock_es = AsyncMock()
        mock_index = MagicMock(index_name="coremarket_items")

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        mock_session_cls = MagicMock(return_value=mock_session)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", mock_session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.client.get_es_client",
                 return_value=mock_es,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex",
                 return_value=mock_index,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.sync.item_sync.index_item",
                 new_callable=AsyncMock,
                 return_value=True,
             ) as mock_index_fn:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                ELASTICSEARCH_INDEX_PREFIX="coremarket",
            )
            result = await _index_item_async(item_uuid)

        assert result == {"item_id": item_uuid, "indexed": True}
        mock_index_fn.assert_called_once()

    async def test_index_item_called_with_session(self):
        from src.backend.application.tasks.search_sync import _index_item_async

        item_uuid = "550e8400-e29b-41d4-a716-446655440001"

        mock_es = AsyncMock()
        mock_index = MagicMock(index_name="coremarket_items")

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        mock_engine = MagicMock()
        mock_engine.dispose = AsyncMock()
        mock_session_cls = MagicMock(return_value=mock_session)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=mock_engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", mock_session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg, \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.client.get_es_client",
                 return_value=mock_es,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex",
                 return_value=mock_index,
             ), \
             patch(
                 "src.backend.search.infrastructure.elasticsearch.sync.item_sync.index_item",
                 new_callable=AsyncMock,
                 return_value=False,
             ) as mock_index_fn:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                ELASTICSEARCH_INDEX_PREFIX="coremarket",
            )
            result = await _index_item_async(item_uuid)

        # index_item called with the session from the async context manager
        call_kwargs = mock_index_fn.call_args.kwargs
        assert call_kwargs["session"] is mock_session
        assert result["indexed"] is False
