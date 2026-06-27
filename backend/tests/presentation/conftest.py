from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from src.backend.domain.user.entity import User, UserRole
from src.backend.main import app
from src.backend.presentation.api.v1.auth.dependencies import get_current_user, require_admin


def make_user(role: UserRole = UserRole.user) -> User:
    return User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        role=role,
    )


@pytest.fixture
def mock_regular_user() -> User:
    return make_user(UserRole.user)


@pytest.fixture
def mock_admin_user() -> User:
    return make_user(UserRole.admin)


@pytest.fixture
async def anon_client():
    """Client with no auth headers."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def user_client(mock_regular_user: User):
    """Client authenticated as a regular user."""
    app.dependency_overrides[get_current_user] = lambda: mock_regular_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
async def admin_client(mock_admin_user: User):
    """Client authenticated as an admin."""
    app.dependency_overrides[get_current_user] = lambda: mock_admin_user
    app.dependency_overrides[require_admin] = lambda: mock_admin_user
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)
