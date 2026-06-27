"""Tests for recalculate_item_rating Celery task."""
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry


# ── Task configuration ─────────────────────────────────────────────────────────

class TestRecalculateItemRatingConfig:
    def test_task_name(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        assert recalculate_item_rating.name == "coremarket.tasks.recalculate_item_rating"

    def test_max_retries(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        assert recalculate_item_rating.max_retries == 3


# ── Success paths ──────────────────────────────────────────────────────────────

class TestRecalculateItemRatingSuccess:
    def test_returns_avg_and_count(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.return_value = {"avg_score": 4.25, "count": 8}
            result = recalculate_item_rating.apply(args=("item-uuid-123",))

        assert result.result == {"avg_score": 4.25, "count": 8}

    def test_empty_ratings_returns_zero(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.return_value = {"avg_score": 0.0, "count": 0}
            result = recalculate_item_rating.apply(args=("item-no-ratings",))

        assert result.result["avg_score"] == 0.0
        assert result.result["count"] == 0

    def test_single_rating(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.return_value = {"avg_score": 5.0, "count": 1}
            result = recalculate_item_rating.apply(args=("item-one-rating",))

        assert result.result["avg_score"] == 5.0
        assert result.result["count"] == 1

    def test_avg_score_is_float(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.return_value = {"avg_score": 3.33, "count": 3}
            result = recalculate_item_rating.apply(args=("item-float",))

        assert isinstance(result.result["avg_score"], float)

    def test_task_successful(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.return_value = {"avg_score": 4.0, "count": 5}
            result = recalculate_item_rating.apply(args=("item-ok",))

        assert result.successful()

    def test_passes_coroutine_to_asyncio_run(self):
        import inspect
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.return_value = {"avg_score": 3.5, "count": 4}
            recalculate_item_rating.apply(args=("specific-item-id",))

        coro = mock_run.call_args[0][0]
        assert inspect.iscoroutine(coro)
        coro.close()


# ── Retry behaviour ────────────────────────────────────────────────────────────

class TestRecalculateItemRatingRetry:
    def test_retries_on_db_error(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("db connection error")
            with pytest.raises(Retry):
                recalculate_item_rating.apply(args=("item-uuid",), throw=True)

    def test_exhausted_retries_raises_original_exception(self):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError("DB permanently down")
            with pytest.raises(RuntimeError, match="DB permanently down"):
                recalculate_item_rating.apply(args=("item-uuid",), retries=3, throw=True)


# ── Logging ────────────────────────────────────────────────────────────────────

class TestRecalculateItemRatingLogging:
    def test_logs_task_started(self, caplog):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.ratings"):
            with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
                mock_run.return_value = {"avg_score": 4.0, "count": 5}
                recalculate_item_rating.apply(args=("item-log",))

        assert any("task_started" in r.message for r in caplog.records)

    def test_logs_task_completed(self, caplog):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.ratings"):
            with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
                mock_run.return_value = {"avg_score": 4.0, "count": 5}
                recalculate_item_rating.apply(args=("item-log",))

        assert any("task_completed" in r.message for r in caplog.records)

    def test_logs_task_failed(self, caplog):
        from src.backend.application.tasks.ratings import recalculate_item_rating

        with caplog.at_level(logging.ERROR, logger="coremarket.tasks.ratings"):
            with patch("src.backend.application.tasks.ratings.asyncio.run") as mock_run:
                mock_run.side_effect = RuntimeError("db error")
                try:
                    recalculate_item_rating.apply(args=("item-fail",), throw=True)
                except Exception:
                    pass

        assert any("task_failed" in r.message for r in caplog.records)


# ── Async DB helper ────────────────────────────────────────────────────────────

def _mock_session_ctx(session: AsyncMock, engine: MagicMock) -> tuple:
    """Return (session_cls_mock, engine_mock) for patching SQLAlchemy internals."""
    engine.dispose = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session_cls = MagicMock(return_value=session)
    return session_cls, engine


class TestRecalculateItemRatingAsync:
    """Tests for _recalculate_async — verifies AVG calculation and UPDATE behaviour."""

    async def test_calculates_avg_and_count(self):
        from src.backend.application.tasks.ratings import _recalculate_async

        select_result = MagicMock()
        select_result.fetchone.return_value = MagicMock(avg_score=4.25, total=8)
        update_result = MagicMock()

        session = AsyncMock()
        engine = MagicMock()
        session_cls, engine = _mock_session_ctx(session, engine)
        session.execute = AsyncMock(side_effect=[select_result, update_result])
        session.commit = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            result = await _recalculate_async("item-uuid-123")

        assert result["avg_score"] == 4.25
        assert result["count"] == 8

    async def test_avg_rounded_to_two_decimal_places(self):
        from src.backend.application.tasks.ratings import _recalculate_async

        select_result = MagicMock()
        # 10/3 ≈ 3.333... → should round to 3.33
        select_result.fetchone.return_value = MagicMock(avg_score=3.3333333, total=3)
        update_result = MagicMock()

        session = AsyncMock()
        engine = MagicMock()
        session_cls, engine = _mock_session_ctx(session, engine)
        session.execute = AsyncMock(side_effect=[select_result, update_result])
        session.commit = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            result = await _recalculate_async("item-round")

        assert result["avg_score"] == round(3.3333333, 2)

    async def test_empty_ratings_returns_zero(self):
        from src.backend.application.tasks.ratings import _recalculate_async

        select_result = MagicMock()
        select_result.fetchone.return_value = MagicMock(avg_score=None, total=0)
        update_result = MagicMock()

        session = AsyncMock()
        engine = MagicMock()
        session_cls, engine = _mock_session_ctx(session, engine)
        session.execute = AsyncMock(side_effect=[select_result, update_result])
        session.commit = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            result = await _recalculate_async("item-no-ratings")

        assert result["avg_score"] == 0.0
        assert result["count"] == 0

    async def test_safe_noop_if_update_column_missing(self):
        """UPDATE throwing (e.g. avg_rating column absent) rolls back and still returns avg."""
        from src.backend.application.tasks.ratings import _recalculate_async

        select_result = MagicMock()
        select_result.fetchone.return_value = MagicMock(avg_score=3.5, total=4)

        session = AsyncMock()
        engine = MagicMock()
        session_cls, engine = _mock_session_ctx(session, engine)
        session.execute = AsyncMock(
            side_effect=[select_result, Exception("column avg_rating does not exist")]
        )
        session.rollback = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            result = await _recalculate_async("item-missing-col")

        assert result["avg_score"] == 3.5
        assert result["count"] == 4
        session.rollback.assert_called_once()

    async def test_update_avg_rating_called(self):
        """Verify two execute calls: SELECT then UPDATE."""
        from src.backend.application.tasks.ratings import _recalculate_async

        select_result = MagicMock()
        select_result.fetchone.return_value = MagicMock(avg_score=4.0, total=2)
        update_result = MagicMock()

        session = AsyncMock()
        engine = MagicMock()
        session_cls, engine = _mock_session_ctx(session, engine)
        session.execute = AsyncMock(side_effect=[select_result, update_result])
        session.commit = AsyncMock()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            await _recalculate_async("item-update")

        assert session.execute.call_count == 2
        session.commit.assert_called_once()
