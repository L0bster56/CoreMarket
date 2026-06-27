from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from src.backend.domain.user.entity import User, UserRole
from src.backend.main import app
from src.backend.presentation.api.v1.auth.dependencies import (
    get_current_user,
    get_hasher,
    get_token_service,
)
from src.backend.presentation.api.v1.core.dependencies import get_uow


def _sample_user() -> User:
    return User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        role=UserRole.user,
    )


@pytest.fixture
def mock_uow():
    sample = _sample_user()
    uow = AsyncMock()
    uow.users.exists_email = AsyncMock(return_value=False)
    uow.users.exists_username = AsyncMock(return_value=False)
    uow.users.create = AsyncMock(side_effect=lambda u: u)
    uow.users.get_by_id = AsyncMock(return_value=sample)
    uow.users.get_by_username = AsyncMock(return_value=sample)
    uow.users.update = AsyncMock()
    uow.commit = AsyncMock()
    return uow


@pytest.fixture
def mock_hasher():
    h = MagicMock()
    h.hash.return_value = "hashed"
    h.verify.return_value = True
    return h


@pytest.fixture
def mock_tokens():
    t = MagicMock()
    t.encode.return_value = "token_value"
    t.get_token_type.return_value = "Bearer"
    t.decode.return_value = uuid4()
    return t


@pytest.fixture
async def public_client(mock_uow, mock_hasher, mock_tokens):
    """Infra deps mocked, no auth override — for register/login/refresh and 403 tests."""
    app.dependency_overrides[get_uow] = lambda: mock_uow
    app.dependency_overrides[get_hasher] = lambda: mock_hasher
    app.dependency_overrides[get_token_service] = lambda: mock_tokens
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_uow, None)
    app.dependency_overrides.pop(get_hasher, None)
    app.dependency_overrides.pop(get_token_service, None)


@pytest.fixture
async def logged_in_client(mock_uow, mock_hasher, mock_tokens):
    """All infra deps mocked + authenticated as regular user."""
    user = _sample_user()
    app.dependency_overrides[get_uow] = lambda: mock_uow
    app.dependency_overrides[get_hasher] = lambda: mock_hasher
    app.dependency_overrides[get_token_service] = lambda: mock_tokens
    app.dependency_overrides[get_current_user] = lambda: user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_uow, None)
    app.dependency_overrides.pop(get_hasher, None)
    app.dependency_overrides.pop(get_token_service, None)
    app.dependency_overrides.pop(get_current_user, None)
