import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.backend.domain.comment.entity import Comment
from src.backend.domain.user.entity import User, UserRole


@pytest.fixture
def mock_comment_repo():
    return AsyncMock()


@pytest.fixture
def mock_uow(mock_comment_repo):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.comments = mock_comment_repo
    return uow


@pytest.fixture
def item_id():
    return uuid.uuid4()


@pytest.fixture
def user_id():
    return uuid.uuid4()


@pytest.fixture
def sample_user(user_id):
    user = User.create(username="testuser", email="test@test.com", hashed_password="hash")
    object.__setattr__(user, "id", user_id)
    return user


@pytest.fixture
def admin_user():
    return User.create(
        username="adminuser",
        email="admin@test.com",
        hashed_password="hash",
        role=UserRole.admin,
    )


@pytest.fixture
def other_user():
    return User.create(username="otheruser", email="other@test.com", hashed_password="hash")


@pytest.fixture
def sample_comment(item_id, user_id):
    return Comment.create(
        item_id=item_id,
        user_id=user_id,
        parent_id=None,
        body="Отличный товар!",
    )


@pytest.fixture
def child_comment(item_id, user_id, sample_comment):
    return Comment.create(
        item_id=item_id,
        user_id=user_id,
        parent_id=sample_comment.id,
        body="Согласен!",
    )
