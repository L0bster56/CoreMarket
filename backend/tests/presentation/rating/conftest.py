from __future__ import annotations

from uuid import uuid4

import pytest
from unittest.mock import AsyncMock, MagicMock

from src.backend.application.rating.dtos.get_rating import GetRatingResult
from src.backend.main import app
from src.backend.presentation.api.v1.rating.dependencies import (
    get_create_rating_use_case,
    get_delete_rating_use_case,
    get_get_rating_use_case,
    get_optional_user,
    get_rating_repo,
    get_update_rating_use_case,
)

_ITEM_ID = uuid4()


def _make_get_result() -> GetRatingResult:
    return GetRatingResult(item_id=_ITEM_ID, avg_score=4.2, count=15)


@pytest.fixture
def mock_get_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_get_result()
    app.dependency_overrides[get_get_rating_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_get_rating_use_case, None)


@pytest.fixture
def mock_create_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_create_rating_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_rating_use_case, None)


@pytest.fixture
def mock_update_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_rating_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_rating_use_case, None)


@pytest.fixture
def mock_delete_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_rating_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_rating_use_case, None)


@pytest.fixture
def mock_rating_repo():
    repo = AsyncMock()
    repo.get_by_item_and_user.return_value = None
    repo.get_avg_by_item.return_value = 4.2
    repo.count_by_item.return_value = 15
    app.dependency_overrides[get_rating_repo] = lambda: repo
    yield repo
    app.dependency_overrides.pop(get_rating_repo, None)


@pytest.fixture
def mock_optional_user_none():
    app.dependency_overrides[get_optional_user] = lambda: None
    yield None
    app.dependency_overrides.pop(get_optional_user, None)


@pytest.fixture
def mock_optional_user_authenticated(mock_regular_user):
    app.dependency_overrides[get_optional_user] = lambda: mock_regular_user
    yield mock_regular_user
    app.dependency_overrides.pop(get_optional_user, None)
