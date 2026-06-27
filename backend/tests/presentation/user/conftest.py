from __future__ import annotations

import pytest
from unittest.mock import AsyncMock

from src.backend.domain.user.entity import User, UserRole
from src.backend.main import app
from src.backend.presentation.api.v1.user.dependencies import (
    get_delete_user_use_case,
    get_get_user_use_case,
)


def _make_user_entity() -> User:
    return User.create(
        username="targetuser",
        email="target@example.com",
        hashed_password="hashed",
        role=UserRole.user,
    )


@pytest.fixture
def mock_get_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_user_entity()
    app.dependency_overrides[get_get_user_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_get_user_use_case, None)


@pytest.fixture
def mock_delete_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_user_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_user_use_case, None)
