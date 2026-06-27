from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.backend.application.category.dtos.create_category import CreateCategoryResult
from src.backend.application.category.dtos.list_categories import CategoryItem, ListCategoriesResult
from src.backend.domain.category.entity import Category
from src.backend.main import app
from src.backend.presentation.api.v1.category.dependencies import (
    get_create_category_use_case,
    get_current_category,
    get_delete_category_use_case,
    get_list_categories_use_case,
    get_update_category_use_case,
)


def _sample_category() -> Category:
    return Category.create(
        name="Electronics",
        slug="electronics",
        description="All gadgets",
        image_url=None,
    )


def _make_list_result() -> ListCategoriesResult:
    now = datetime.now(timezone.utc)
    return ListCategoriesResult(
        items=[
            CategoryItem(
                id=uuid4(),
                name="Electronics",
                slug="electronics",
                description="All gadgets",
                image_url=None,
                created_at=now,
                updated_at=now,
            )
        ]
    )


def _make_create_result() -> CreateCategoryResult:
    now = datetime.now(timezone.utc)
    return CreateCategoryResult(
        id=uuid4(),
        name="Electronics",
        slug="electronics",
        description="All gadgets",
        image_url=None,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def sample_category() -> Category:
    return _sample_category()


@pytest.fixture
def mock_current_category(sample_category):
    app.dependency_overrides[get_current_category] = lambda: sample_category
    yield sample_category
    app.dependency_overrides.pop(get_current_category, None)


@pytest.fixture
def mock_list_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_list_result()
    app.dependency_overrides[get_list_categories_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_list_categories_use_case, None)


@pytest.fixture
def mock_create_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_create_result()
    app.dependency_overrides[get_create_category_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_category_use_case, None)


@pytest.fixture
def mock_update_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_category_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_category_use_case, None)


@pytest.fixture
def mock_delete_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_category_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_category_use_case, None)
