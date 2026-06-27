"""Tests for cleanup_expired_sessions Celery task."""
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry


# ── Task configuration ─────────────────────────────────────────────────────────

class TestCleanupExpiredSessionsConfig:
    def test_task_name(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        assert cleanup_expired_sessions.name == "coremarket.tasks.cleanup_expired_sessions"

    def test_max_retries(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        assert cleanup_expired_sessions.max_retries == 2


# ── Success paths ──────────────────────────────────────────────────────────────

class TestCleanupExpiredSessionsSuccess:
    def test_returns_deleted_comments_count(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
            mock_run.return_value = {"deleted_comments": 7}
            result = cleanup_expired_sessions.apply()

        assert result.result == {"deleted_comments": 7}

    def test_zero_deleted_when_nothing_to_clean(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
            mock_run.return_value = {"deleted_comments": 0}
            result = cleanup_expired_sessions.apply()

        assert result.result["deleted_comments"] == 0

    def test_large_batch_deletion(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
            mock_run.return_value = {"deleted_comments": 500}
            result = cleanup_expired_sessions.apply()

        assert result.result["deleted_comments"] == 500

    def test_task_successful(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
            mock_run.return_value = {"deleted_comments": 3}
            result = cleanup_expired_sessions.apply()

        assert result.successful()


# ── Retry behaviour ────────────────────────────────────────────────────────────

class TestCleanupExpiredSessionsRetry:
    def test_retries_on_db_error(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("db connection error")
            with pytest.raises(Retry):
                cleanup_expired_sessions.apply(throw=True)

    def test_exhausted_retries_raises_original_exception(self):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError("db permanently down")
            with pytest.raises(RuntimeError, match="db permanently down"):
                cleanup_expired_sessions.apply(retries=2, throw=True)


# ── Logging ────────────────────────────────────────────────────────────────────

class TestCleanupExpiredSessionsLogging:
    def test_logs_task_started(self, caplog):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.cleanup"):
            with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
                mock_run.return_value = {"deleted_comments": 5}
                cleanup_expired_sessions.apply()

        assert any("task_started" in r.message for r in caplog.records)

    def test_logs_task_completed(self, caplog):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.cleanup"):
            with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
                mock_run.return_value = {"deleted_comments": 5}
                cleanup_expired_sessions.apply()

        assert any("task_completed" in r.message for r in caplog.records)

    def test_logs_task_failed(self, caplog):
        from src.backend.application.tasks.cleanup import cleanup_expired_sessions

        with caplog.at_level(logging.ERROR, logger="coremarket.tasks.cleanup"):
            with patch("src.backend.application.tasks.cleanup.asyncio.run") as mock_run:
                mock_run.side_effect = RuntimeError("db error")
                try:
                    cleanup_expired_sessions.apply(throw=True)
                except Exception:
                    pass

        assert any("task_failed" in r.message for r in caplog.records)


# ── Async DB helper ────────────────────────────────────────────────────────────

def _mock_db_session(rowcount: int = 0) -> tuple[AsyncMock, MagicMock, MagicMock]:
    """Return (session, engine, session_cls) with execute returning rowcount."""
    mock_result = MagicMock()
    mock_result.rowcount = rowcount

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.execute = AsyncMock(return_value=mock_result)
    session.commit = AsyncMock()

    engine = MagicMock()
    engine.dispose = AsyncMock()
    session_cls = MagicMock(return_value=session)

    return session, engine, session_cls


class TestCleanupAsync:
    """Tests for _cleanup_async — verifies SQL, return value, and edge cases."""

    async def test_returns_deleted_comments_count(self):
        from src.backend.application.tasks.cleanup import _cleanup_async

        session, engine, session_cls = _mock_db_session(rowcount=3)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            result = await _cleanup_async()

        assert result == {"deleted_comments": 3}

    async def test_returns_zero_when_nothing_to_delete(self):
        from src.backend.application.tasks.cleanup import _cleanup_async

        session, engine, session_cls = _mock_db_session(rowcount=0)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            result = await _cleanup_async()

        assert result["deleted_comments"] == 0

    async def test_sql_targets_is_deleted_true(self):
        """DELETE must filter WHERE is_deleted = TRUE."""
        from src.backend.application.tasks.cleanup import _cleanup_async

        captured: list[str] = []
        mock_result = MagicMock()
        mock_result.rowcount = 0

        async def capture_execute(sql, *_args, **_kwargs):
            captured.append(str(sql))
            return mock_result

        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.execute = capture_execute
        session.commit = AsyncMock()

        engine = MagicMock()
        engine.dispose = AsyncMock()
        session_cls = MagicMock(return_value=session)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            await _cleanup_async()

        assert captured, "execute must be called"
        assert "is_deleted" in captured[0]

    async def test_sql_targets_90_day_interval(self):
        """DELETE must filter WHERE updated_at < NOW() - INTERVAL '90 days'."""
        from src.backend.application.tasks.cleanup import _cleanup_async

        captured: list[str] = []
        mock_result = MagicMock()
        mock_result.rowcount = 0

        async def capture_execute(sql, *_args, **_kwargs):
            captured.append(str(sql))
            return mock_result

        session = AsyncMock()
        session.__aenter__ = AsyncMock(return_value=session)
        session.__aexit__ = AsyncMock(return_value=False)
        session.execute = capture_execute
        session.commit = AsyncMock()

        engine = MagicMock()
        engine.dispose = AsyncMock()
        session_cls = MagicMock(return_value=session)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            await _cleanup_async()

        assert "90 days" in captured[0]

    async def test_commit_called_after_delete(self):
        from src.backend.application.tasks.cleanup import _cleanup_async

        session, engine, session_cls = _mock_db_session(rowcount=2)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            await _cleanup_async()

        session.commit.assert_called_once()

    async def test_engine_dispose_called(self):
        from src.backend.application.tasks.cleanup import _cleanup_async

        session, engine, session_cls = _mock_db_session(rowcount=1)

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(ASYNC_DATABASE_URL="postgresql+asyncpg://test/db")
            await _cleanup_async()

        engine.dispose.assert_called_once()
