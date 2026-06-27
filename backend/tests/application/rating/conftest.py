from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.backend.domain.rating.entity import Rating
from src.backend.domain.rating.value_objects.score import Score
from src.backend.domain.user.entity import User, UserRole


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.ratings = AsyncMock()
    return uow


@pytest.fixture
def sample_user():
    return User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        role=UserRole.user,
    )


@pytest.fixture
def item_id():
    return uuid4()


@pytest.fixture
def sample_rating(item_id, sample_user):
    return Rating.create(
        item_id=item_id,
        user_id=sample_user.id,
        score=Score(4),
    )
