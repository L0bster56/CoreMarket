from __future__ import annotations

from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.backend.application.tag.dtos.create_tag import CreateTagResult
from src.backend.application.tag.dtos.list_tags import ListTagsResult, TagSummary
from src.backend.main import app
from src.backend.presentation.api.v1.tag.dependencies import (
    get_create_tag_use_case,
    get_delete_tag_use_case,
    get_list_tags_use_case,
)


def _make_list_result() -> ListTagsResult:
    return ListTagsResult(
        items=[
            TagSummary(id=uuid4(), name="Python", slug="python"),
            TagSummary(id=uuid4(), name="Django", slug="django"),
        ]
    )


def _make_create_result() -> CreateTagResult:
    return CreateTagResult(id=uuid4(), name="Python", slug="python")


@pytest.fixture
def mock_list_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_list_result()
    app.dependency_overrides[get_list_tags_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_list_tags_use_case, None)


@pytest.fixture
def mock_create_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_create_result()
    app.dependency_overrides[get_create_tag_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_tag_use_case, None)


@pytest.fixture
def mock_delete_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_tag_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_tag_use_case, None)
