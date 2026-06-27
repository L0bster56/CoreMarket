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
    hasher.hash.return_value = "new_hashed_password"
    hasher.verify.return_value = True
    return hasher


@pytest.fixture
def mock_tokens():
    user_id = uuid4()
    tokens = MagicMock()
    tokens.encode.return_value = "access_token_value"
    tokens.decode.return_value = user_id
    tokens.get_token_type.return_value = "bearer"
    return tokens


@pytest.fixture
def sample_user():
    return User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        role=UserRole.user,
    )


@pytest.fixture
def inactive_user():
    user = User.create(
        username="inactive",
        email="inactive@example.com",
        hashed_password="hashed_password",
        role=UserRole.user,
    )
    user.is_active = False
    return user
