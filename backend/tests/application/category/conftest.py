from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.backend.domain.category.entity import Category


@pytest.fixture
def mock_uow(mock_category_repo):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.categories = mock_category_repo
    return uow


@pytest.fixture
def mock_category_repo():
    return AsyncMock()


@pytest.fixture
def sample_category():
    return Category.create(
        name="Electronics",
        slug="electronics",
        description="All electronics",
        image_url="/media/categories/electronics.jpg",
    )


@pytest.fixture
def another_category():
    return Category.create(
        name="Smartphones",
        slug="smartphones",
        description=None,
        image_url=None,
    )
