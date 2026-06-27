from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.backend.application.comment.dtos.create_comment import CreateCommentResult
from src.backend.application.comment.dtos.list_comments import CommentResult, ListCommentsResult
from src.backend.main import app
from src.backend.presentation.api.v1.comment.dependencies import (
    get_create_comment_use_case,
    get_delete_comment_use_case,
    get_list_comments_use_case,
    get_update_comment_use_case,
)

_ITEM_ID = uuid4()
_USER_ID = uuid4()
_COMMENT_ID = uuid4()


def _make_comment_result(
    children: list[CommentResult] | None = None,
) -> CommentResult:
    now = datetime.now(timezone.utc)
    return CommentResult(
        id=_COMMENT_ID,
        item_id=_ITEM_ID,
        user_id=_USER_ID,
        parent_id=None,
        body="Great product!",
        is_deleted=False,
        created_at=now,
        updated_at=now,
        children=children or [],
    )


def _make_list_result() -> ListCommentsResult:
    return ListCommentsResult(items=[_make_comment_result()])


def _make_create_result() -> CreateCommentResult:
    now = datetime.now(timezone.utc)
    return CreateCommentResult(
        id=_COMMENT_ID,
        item_id=_ITEM_ID,
        user_id=_USER_ID,
        parent_id=None,
        body="Great product!",
        is_deleted=False,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def mock_list_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_list_result()
    app.dependency_overrides[get_list_comments_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_list_comments_use_case, None)


@pytest.fixture
def mock_create_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_create_result()
    app.dependency_overrides[get_create_comment_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_comment_use_case, None)


@pytest.fixture
def mock_update_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_comment_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_comment_use_case, None)


@pytest.fixture
def mock_delete_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_comment_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_comment_use_case, None)
