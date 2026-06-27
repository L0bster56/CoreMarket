from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from src.backend.domain.category.entity import Category
from src.backend.domain.item.characteristic import Characteristic
from src.backend.domain.item.entity import Item
from src.backend.domain.item.gallery import Gallery
from src.backend.domain.tag.entity import Tag
from src.backend.domain.user.entity import User, UserRole


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.__aenter__ = AsyncMock(return_value=uow)
    uow.__aexit__ = AsyncMock(return_value=None)
    uow.commit = AsyncMock()
    uow.items = AsyncMock()
    uow.tags = AsyncMock()
    uow.characteristics = AsyncMock()
    uow.gallery = AsyncMock()
    return uow


@pytest.fixture
def admin_user():
    return User.create(
        username="admin",
        email="admin@example.com",
        hashed_password="hashed",
        role=UserRole.admin,
    )


@pytest.fixture
def regular_user():
    return User.create(
        username="user",
        email="user@example.com",
        hashed_password="hashed",
        role=UserRole.user,
    )


@pytest.fixture
def item_id():
    return uuid4()


@pytest.fixture
def category_id():
    return uuid4()


@pytest.fixture
def sample_item(category_id):
    return Item.create(
        name="Test Item",
        short_description="Short desc",
        description="Full description",
        category_id=category_id,
        youtube_url=None,
        marketplace_links=[],
    )


@pytest.fixture
def sample_tag():
    return Tag.create(name="Python", slug="python")


@pytest.fixture
def sample_characteristic(item_id):
    return Characteristic.create(item_id=item_id, name="Weight", value="1kg")


@pytest.fixture
def sample_gallery(item_id):
    return Gallery.create(item_id=item_id, image_url="/media/items/img.jpg")
