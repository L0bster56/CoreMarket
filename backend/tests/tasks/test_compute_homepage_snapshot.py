"""Tests for compute_homepage_snapshot Celery task."""
import json
import logging
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from celery.exceptions import Retry


_SAMPLE_SNAPSHOT = {
    "computed_at": 1234567890.0,
    "featured_items": [
        {"id": "uuid-1", "title": "Item 1", "view_count": 100, "avg_rating": 4.5,
         "short_description": "desc", "category_id": "cat-1",
         "preview_image": None, "created_at": "2026-01-01"},
    ],
    "top_rated_items": [
        {"id": "uuid-2", "title": "Item 2", "avg_rating": 5.0, "view_count": 50,
         "short_description": "desc", "category_id": "cat-1",
         "preview_image": None, "created_at": "2026-01-01"},
    ],
    "categories": [
        {"id": "cat-1", "name": "Electronics", "slug": "electronics", "item_count": 10}
    ],
    "recent_posts": [
        {"id": "post-1", "title": "Post 1", "slug": "post-1",
         "cover_image_url": None, "created_at": "2026-01-01", "seo_description": "x"},
    ],
    "stats": {"total_items": 50, "total_categories": 5, "total_posts": 10},
}


# ── Task configuration ─────────────────────────────────────────────────────────

class TestComputeHomepageSnapshotConfig:
    def test_task_name(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        assert compute_homepage_snapshot.name == "coremarket.tasks.compute_homepage_snapshot"

    def test_max_retries(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        assert compute_homepage_snapshot.max_retries == 2


# ── Success paths ──────────────────────────────────────────────────────────────

class TestComputeHomepageSnapshotSuccess:
    def test_returns_status_ok(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
            mock_run.return_value = _SAMPLE_SNAPSHOT
            result = compute_homepage_snapshot.apply()

        assert result.result["status"] == "ok"

    def test_returns_duration_ms(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
            mock_run.return_value = _SAMPLE_SNAPSHOT
            result = compute_homepage_snapshot.apply()

        assert "duration_ms" in result.result
        assert result.result["duration_ms"] >= 0

    def test_task_successful(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
            mock_run.return_value = _SAMPLE_SNAPSHOT
            result = compute_homepage_snapshot.apply()

        assert result.successful()


# ── Retry behaviour ────────────────────────────────────────────────────────────

class TestComputeHomepageSnapshotRetry:
    def test_retries_on_db_error(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
            mock_run.side_effect = Exception("db connection failed")
            with pytest.raises(Retry):
                compute_homepage_snapshot.apply(throw=True)

    def test_retries_on_redis_unavailable(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
            mock_run.side_effect = ConnectionError("redis unavailable")
            with pytest.raises(Retry):
                compute_homepage_snapshot.apply(throw=True)

    def test_exhausted_retries_raises_original_exception(self):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
            mock_run.side_effect = RuntimeError("hard failure")
            with pytest.raises(RuntimeError, match="hard failure"):
                compute_homepage_snapshot.apply(retries=2, throw=True)


# ── Logging ────────────────────────────────────────────────────────────────────

class TestComputeHomepageSnapshotLogging:
    def test_logs_task_started(self, caplog):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.homepage"):
            with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
                mock_run.return_value = _SAMPLE_SNAPSHOT
                compute_homepage_snapshot.apply()

        assert any("task_started" in r.message for r in caplog.records)

    def test_logs_task_completed(self, caplog):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with caplog.at_level(logging.INFO, logger="coremarket.tasks.homepage"):
            with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
                mock_run.return_value = _SAMPLE_SNAPSHOT
                compute_homepage_snapshot.apply()

        assert any("task_completed" in r.message for r in caplog.records)

    def test_logs_task_failed(self, caplog):
        from src.backend.application.tasks.homepage import compute_homepage_snapshot

        with caplog.at_level(logging.ERROR, logger="coremarket.tasks.homepage"):
            with patch("src.backend.application.tasks.homepage.asyncio.run") as mock_run:
                mock_run.side_effect = RuntimeError("db down")
                try:
                    compute_homepage_snapshot.apply(throw=True)
                except Exception:
                    pass

        assert any("task_failed" in r.message for r in caplog.records)


# ── Snapshot payload structure ─────────────────────────────────────────────────

class TestSnapshotPayloadStructure:
    def test_has_featured_items(self):
        assert "featured_items" in _SAMPLE_SNAPSHOT

    def test_has_top_rated_items(self):
        assert "top_rated_items" in _SAMPLE_SNAPSHOT

    def test_has_categories(self):
        assert "categories" in _SAMPLE_SNAPSHOT

    def test_has_recent_posts(self):
        assert "recent_posts" in _SAMPLE_SNAPSHOT

    def test_has_stats(self):
        assert "stats" in _SAMPLE_SNAPSHOT

    def test_stats_has_total_items(self):
        assert "total_items" in _SAMPLE_SNAPSHOT["stats"]

    def test_stats_has_total_categories(self):
        assert "total_categories" in _SAMPLE_SNAPSHOT["stats"]

    def test_stats_has_total_posts(self):
        assert "total_posts" in _SAMPLE_SNAPSHOT["stats"]


# ── Async DB + Redis helper ────────────────────────────────────────────────────

def _make_db_row(**kwargs) -> MagicMock:
    row = MagicMock()
    row._mapping = kwargs
    return row


def _fetchall_result(rows: list) -> MagicMock:
    r = MagicMock()
    r.fetchall.return_value = rows
    return r


def _fetchone_result(row: object) -> MagicMock:
    r = MagicMock()
    r.fetchone.return_value = row
    return r


def _build_mock_db(featured=None, top_rated=None, categories=None, posts=None, stats=None):
    """Return (mock_session, mock_engine, mock_session_cls) with preset execute side_effects."""
    if featured is None:
        featured = []
    if top_rated is None:
        top_rated = []
    if categories is None:
        categories = []
    if posts is None:
        posts = []
    if stats is None:
        stats_row = MagicMock()
        stats_row.items = 0
        stats_row.categories = 0
        stats_row.posts = 0
    else:
        stats_row = stats

    session = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    session.execute = AsyncMock(side_effect=[
        _fetchall_result(featured),
        _fetchall_result(top_rated),
        _fetchall_result(categories),
        _fetchall_result(posts),
        _fetchone_result(stats_row),
    ])

    engine = MagicMock()
    engine.dispose = AsyncMock()
    session_cls = MagicMock(return_value=session)

    return session, engine, session_cls


def _build_mock_redis(side_effect=None) -> AsyncMock:
    redis = AsyncMock()
    redis.set = AsyncMock(side_effect=side_effect) if side_effect else AsyncMock()
    redis.aclose = AsyncMock()
    return redis


class TestBuildSnapshotAsync:
    """Tests for _build_snapshot — verifies DB queries, Redis write, payload shape."""

    async def test_writes_snapshot_to_redis_with_correct_key(self):
        from src.backend.application.tasks.homepage import _build_snapshot

        featured = [_make_db_row(id="i1", title="T1", view_count=100, avg_rating=4.5,
                                 short_description="d", category_id="c1",
                                 preview_image=None, created_at="2026-01-01")]
        session, engine, session_cls = _build_mock_db(featured=featured)
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            await _build_snapshot()

        mock_redis.set.assert_called_once()
        key_arg = mock_redis.set.call_args[0][0]
        assert key_arg == "homepage:snapshot"

    async def test_writes_snapshot_with_correct_ttl(self):
        from src.backend.application.tasks.homepage import _build_snapshot

        session, engine, session_cls = _build_mock_db()
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=600,
            )
            await _build_snapshot()

        ttl_arg = mock_redis.set.call_args[1]["ex"]
        assert ttl_arg == 600

    async def test_snapshot_has_all_required_sections(self):
        from src.backend.application.tasks.homepage import _build_snapshot

        stats_row = MagicMock()
        stats_row.items = 5
        stats_row.categories = 2
        stats_row.posts = 3
        session, engine, session_cls = _build_mock_db(stats=stats_row)
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            snapshot = await _build_snapshot()

        assert "featured_items" in snapshot
        assert "top_rated_items" in snapshot
        assert "categories" in snapshot
        assert "recent_posts" in snapshot
        assert "stats" in snapshot
        assert "computed_at" in snapshot

    async def test_stats_values_from_db(self):
        from src.backend.application.tasks.homepage import _build_snapshot

        stats_row = MagicMock()
        stats_row.items = 42
        stats_row.categories = 7
        stats_row.posts = 13
        session, engine, session_cls = _build_mock_db(stats=stats_row)
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            snapshot = await _build_snapshot()

        assert snapshot["stats"]["total_items"] == 42
        assert snapshot["stats"]["total_categories"] == 7
        assert snapshot["stats"]["total_posts"] == 13

    async def test_featured_items_populated_from_db(self):
        from src.backend.application.tasks.homepage import _build_snapshot

        featured = [
            _make_db_row(id="i1", title="Top Item", view_count=999, avg_rating=4.9,
                         short_description="d", category_id="c1",
                         preview_image=None, created_at="2026-01-01"),
        ]
        session, engine, session_cls = _build_mock_db(featured=featured)
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            snapshot = await _build_snapshot()

        assert len(snapshot["featured_items"]) == 1
        assert snapshot["featured_items"][0]["id"] == "i1"
        assert snapshot["featured_items"][0]["title"] == "Top Item"

    async def test_stored_json_is_valid_and_complete(self):
        """The value written to Redis must be valid JSON with all sections."""
        from src.backend.application.tasks.homepage import _build_snapshot

        session, engine, session_cls = _build_mock_db()
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            await _build_snapshot()

        json_str = mock_redis.set.call_args[0][1]
        parsed = json.loads(json_str)
        for key in ("featured_items", "top_rated_items", "categories", "recent_posts", "stats"):
            assert key in parsed

    async def test_redis_unavailable_raises_connection_error(self):
        """Redis write failure propagates so the task can retry."""
        from src.backend.application.tasks.homepage import _build_snapshot

        session, engine, session_cls = _build_mock_db()
        mock_redis = _build_mock_redis(side_effect=ConnectionError("Redis down"))

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            with pytest.raises(ConnectionError, match="Redis down"):
                await _build_snapshot()

    async def test_redis_aclose_called_even_on_error(self):
        """Redis client must always be closed to avoid connection leaks."""
        from src.backend.application.tasks.homepage import _build_snapshot

        session, engine, session_cls = _build_mock_db()
        mock_redis = _build_mock_redis(side_effect=RuntimeError("Redis error"))

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            with pytest.raises(RuntimeError):
                await _build_snapshot()

        mock_redis.aclose.assert_called_once()

    async def test_makes_five_db_queries(self):
        """_build_snapshot must make exactly 5 SQL execute calls."""
        from src.backend.application.tasks.homepage import _build_snapshot

        session, engine, session_cls = _build_mock_db()
        mock_redis = _build_mock_redis()

        with patch("sqlalchemy.ext.asyncio.create_async_engine", return_value=engine), \
             patch("sqlalchemy.ext.asyncio.AsyncSession", session_cls), \
             patch("redis.asyncio.from_url", return_value=mock_redis), \
             patch("src.backend.config.get_settings") as mock_cfg:
            mock_cfg.return_value = MagicMock(
                ASYNC_DATABASE_URL="postgresql+asyncpg://test/db",
                REDIS_URL="redis://localhost:6379/0",
                HOMEPAGE_SNAPSHOT_KEY="homepage:snapshot",
                HOMEPAGE_SNAPSHOT_TTL=300,
            )
            await _build_snapshot()

        assert session.execute.call_count == 5
