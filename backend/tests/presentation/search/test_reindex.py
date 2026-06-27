from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from elasticsearch import TransportError

from src.backend.main import app
from src.backend.presentation.api.v1.core.dependencies import get_uow

BASE = "/api/v1/search/reindex"


@pytest.fixture(autouse=True)
def _mock_uow():
    """Override get_uow so SQLAlchemy never attempts a real session in these tests.

    The reindex endpoint declares `uow: UoWDep` in its signature (even though
    the body doesn't use it), so FastAPI resolves the dep for every request —
    including auth-only calls (401/403) — which would otherwise crash with
    'greenlet library is required'.
    """
    mock = MagicMock()
    mock.__aenter__ = AsyncMock(return_value=mock)
    mock.__aexit__ = AsyncMock(return_value=None)
    app.dependency_overrides[get_uow] = lambda: mock
    yield
    app.dependency_overrides.pop(get_uow, None)


async def test_reindex_200_admin(admin_client):
    # The endpoint body uses LOCAL imports for all search/db helpers, so patches
    # must target the original module namespaces, not the router module.
    with (
        patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_router_cfg,
        patch("src.backend.config.get_settings") as mock_cfg,
        patch("src.backend.search.infrastructure.elasticsearch.client.get_es_client"),
        patch(
            "src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex"
        ) as mock_index_cls,
        patch(
            "src.backend.search.infrastructure.elasticsearch.sync.item_sync.bulk_reindex"
        ) as mock_reindex,
        patch(
            "src.backend.infrastructure.db.sqlalchemy.core.session.async_session"
        ) as mock_session_ctx,
    ):
        mock_router_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.ELASTICSEARCH_INDEX_PREFIX = "coremarket"
        mock_index = AsyncMock()
        mock_index.index_name = "coremarket-items"
        mock_index.recreate_index = AsyncMock()
        mock_index_cls.return_value = mock_index
        mock_reindex.return_value = 42
        mock_session = AsyncMock()
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=None)

        response = await admin_client.post(BASE)

    assert response.status_code == 200
    data = response.json()
    assert data["indexed"] == 42
    assert "message" in data


async def test_reindex_503_when_disabled(admin_client):
    with patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_cfg:
        mock_cfg.return_value.SEARCH_ENABLED = False
        response = await admin_client.post(BASE)

    assert response.status_code == 503


async def test_reindex_401_anon(anon_client):
    # Auth guard rejects before function body runs — no settings patch needed.
    response = await anon_client.post(BASE)
    assert response.status_code == 401


async def test_reindex_403_regular_user(user_client):
    # require_admin raises 403 for non-admin users.
    response = await user_client.post(BASE)
    assert response.status_code == 403


def _full_patch_ctx(search_enabled: bool = True):
    return (
        patch("src.backend.presentation.api.v1.search.router.get_settings"),
        patch("src.backend.config.get_settings"),
        patch("src.backend.search.infrastructure.elasticsearch.client.get_es_client"),
        patch("src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex"),
        patch("src.backend.search.infrastructure.elasticsearch.sync.item_sync.bulk_reindex"),
        patch("src.backend.infrastructure.db.sqlalchemy.core.session.async_session"),
    )


async def test_reindex_503_on_es_exception(admin_client):
    with (
        patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_router_cfg,
        patch("src.backend.config.get_settings") as mock_cfg,
        patch("src.backend.search.infrastructure.elasticsearch.client.get_es_client"),
        patch("src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex") as mock_index_cls,
        patch("src.backend.infrastructure.db.sqlalchemy.core.session.async_session") as mock_sess_ctx,
    ):
        mock_router_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.ELASTICSEARCH_INDEX_PREFIX = "coremarket"

        mock_index = AsyncMock()
        mock_index.recreate_index.side_effect = TransportError("es unavailable")
        mock_index_cls.return_value = mock_index

        mock_sess = AsyncMock()
        mock_sess_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_sess)
        mock_sess_ctx.return_value.__aexit__ = AsyncMock(return_value=None)

        response = await admin_client.post(BASE)

    assert response.status_code == 503


async def test_reindex_calls_recreate_index(admin_client):
    with (
        patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_router_cfg,
        patch("src.backend.config.get_settings") as mock_cfg,
        patch("src.backend.search.infrastructure.elasticsearch.client.get_es_client"),
        patch("src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex") as mock_index_cls,
        patch("src.backend.search.infrastructure.elasticsearch.sync.item_sync.bulk_reindex") as mock_reindex,
        patch("src.backend.infrastructure.db.sqlalchemy.core.session.async_session") as mock_sess_ctx,
    ):
        mock_router_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.ELASTICSEARCH_INDEX_PREFIX = "coremarket"

        mock_index = AsyncMock()
        mock_index.index_name = "coremarket-items"
        mock_index.recreate_index = AsyncMock()
        mock_index_cls.return_value = mock_index
        mock_reindex.return_value = 5

        mock_sess = AsyncMock()
        mock_sess_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_sess)
        mock_sess_ctx.return_value.__aexit__ = AsyncMock(return_value=None)

        await admin_client.post(BASE)

    mock_index.recreate_index.assert_called_once()


async def test_reindex_response_message_contains_count(admin_client):
    with (
        patch("src.backend.presentation.api.v1.search.router.get_settings") as mock_router_cfg,
        patch("src.backend.config.get_settings") as mock_cfg,
        patch("src.backend.search.infrastructure.elasticsearch.client.get_es_client"),
        patch("src.backend.search.infrastructure.elasticsearch.indexes.items.ItemIndex") as mock_index_cls,
        patch("src.backend.search.infrastructure.elasticsearch.sync.item_sync.bulk_reindex") as mock_reindex,
        patch("src.backend.infrastructure.db.sqlalchemy.core.session.async_session") as mock_sess_ctx,
    ):
        mock_router_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.SEARCH_ENABLED = True
        mock_cfg.return_value.ELASTICSEARCH_INDEX_PREFIX = "coremarket"

        mock_index = AsyncMock()
        mock_index.index_name = "coremarket-items"
        mock_index.recreate_index = AsyncMock()
        mock_index_cls.return_value = mock_index
        mock_reindex.return_value = 17

        mock_sess = AsyncMock()
        mock_sess_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_sess)
        mock_sess_ctx.return_value.__aexit__ = AsyncMock(return_value=None)

        response = await admin_client.post(BASE)

    data = response.json()
    assert data["indexed"] == 17
    assert "17" in data["message"]
