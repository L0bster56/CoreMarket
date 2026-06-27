from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.backend.domain.user.entity import User, UserRole


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.users = AsyncMock()
    return uow


@pytest.fixture
def mock_hasher():
    hasher = MagicMock()
    hasher.hash.return_value = "hashed_password"
    hasher.verify.return_value = True
    return hasher


@pytest.fixture
def sample_user():
    return User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.user,
    )


@pytest.fixture
def user_id():
    return uuid4()
