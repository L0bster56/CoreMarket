from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from unittest.mock import AsyncMock

from src.backend.application.item.dtos.add_characteristic import AddCharacteristicResult
from src.backend.application.item.dtos.add_gallery_image import AddGalleryImageResult
from src.backend.application.item.dtos.create_item import CreateItemResult
from src.backend.application.item.dtos.get_item import GetItemResult
from src.backend.application.item.dtos.list_items import ItemListEntry, ListItemsResult
from src.backend.main import app
from src.backend.presentation.api.v1.item.dependencies import (
    get_add_characteristic_use_case,
    get_add_gallery_image_use_case,
    get_add_item_tag_use_case,
    get_create_item_use_case,
    get_delete_characteristic_use_case,
    get_delete_gallery_image_use_case,
    get_delete_item_use_case,
    get_get_item_use_case,
    get_list_items_use_case,
    get_remove_item_tag_use_case,
    get_update_characteristic_use_case,
    get_update_item_use_case,
)

_ITEM_ID = uuid4()
_CAT_ID = uuid4()


def _make_item_result() -> GetItemResult:
    now = datetime.now(timezone.utc)
    return GetItemResult(
        id=_ITEM_ID,
        title="Test Item",
        short_description="Short desc",
        description="Full description",
        category_id=_CAT_ID,
        youtube_url="https://youtube.com/watch?v=abc123",
        marketplace_links=[],
        is_published=True,
        view_count=0,
        characteristics=[],
        gallery=[],
        tags=[],
        created_at=now,
        updated_at=now,
    )


def _make_list_result() -> ListItemsResult:
    now = datetime.now(timezone.utc)
    return ListItemsResult(
        items=[
            ItemListEntry(
                id=_ITEM_ID,
                title="Test Item",
                short_description="Short desc",
                category_id=_CAT_ID,
                youtube_url=None,
                is_published=True,
                view_count=0,
                created_at=now,
                updated_at=now,
            )
        ],
        total=1,
    )


def _make_create_result() -> CreateItemResult:
    now = datetime.now(timezone.utc)
    return CreateItemResult(
        id=_ITEM_ID,
        title="Test Item",
        short_description="Short desc",
        description="Full description",
        category_id=_CAT_ID,
        youtube_url=None,
        marketplace_links=[],
        is_published=False,
        created_at=now,
        updated_at=now,
    )


def _make_char_result() -> AddCharacteristicResult:
    return AddCharacteristicResult(
        id=uuid4(),
        item_id=_ITEM_ID,
        name="Color",
        value="Red",
    )


def _make_gallery_result() -> AddGalleryImageResult:
    return AddGalleryImageResult(
        id=uuid4(),
        item_id=_ITEM_ID,
        image_url="/media/items/test.jpg",
    )


@pytest.fixture
def mock_list_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_list_result()
    app.dependency_overrides[get_list_items_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_list_items_use_case, None)


@pytest.fixture
def mock_get_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_item_result()
    app.dependency_overrides[get_get_item_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_get_item_use_case, None)


@pytest.fixture
def mock_create_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_create_result()
    app.dependency_overrides[get_create_item_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_create_item_use_case, None)


@pytest.fixture
def mock_update_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_item_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_item_use_case, None)


@pytest.fixture
def mock_delete_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_item_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_item_use_case, None)


@pytest.fixture
def mock_add_tag_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_add_item_tag_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_add_item_tag_use_case, None)


@pytest.fixture
def mock_remove_tag_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_remove_item_tag_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_remove_item_tag_use_case, None)


@pytest.fixture
def mock_add_char_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_char_result()
    app.dependency_overrides[get_add_characteristic_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_add_characteristic_use_case, None)


@pytest.fixture
def mock_update_char_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_update_characteristic_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_update_characteristic_use_case, None)


@pytest.fixture
def mock_delete_char_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_characteristic_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_characteristic_use_case, None)


@pytest.fixture
def mock_add_gallery_uc():
    uc = AsyncMock()
    uc.execute.return_value = _make_gallery_result()
    app.dependency_overrides[get_add_gallery_image_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_add_gallery_image_use_case, None)


@pytest.fixture
def mock_delete_gallery_uc():
    uc = AsyncMock()
    uc.execute.return_value = None
    app.dependency_overrides[get_delete_gallery_image_use_case] = lambda: uc
    yield uc
    app.dependency_overrides.pop(get_delete_gallery_image_use_case, None)
