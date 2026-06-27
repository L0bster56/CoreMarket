from unittest.mock import AsyncMock, MagicMock

import pytest

from src.backend.domain.tag.entity import Tag


@pytest.fixture
def mock_tag_repo():
    return AsyncMock()


@pytest.fixture
def mock_uow(mock_tag_repo):
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.rollback = AsyncMock()
    uow.tags = mock_tag_repo
    return uow


@pytest.fixture
def sample_tag():
    return Tag.create(name="Python", slug="python")


@pytest.fixture
def another_tag():
    return Tag.create(name="Django", slug="django")
