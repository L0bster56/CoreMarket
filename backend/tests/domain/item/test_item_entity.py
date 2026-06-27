import time
import uuid

import pytest

from src.backend.domain.item.entity import Item
from src.backend.domain.item.value_objects.marketplace_link import MarketplaceLink
from src.backend.domain.shared.value_objects.name.error import InvalidNameError
from src.backend.domain.shared.value_objects.name.value_object import Name


def make_item(**kwargs) -> Item:
    defaults = dict(
        name="iPhone 15 Pro",
        short_description="Флагман от Apple",
        description="Полное описание iPhone 15 Pro",
        category_id=uuid.uuid4(),
        youtube_url="https://youtube.com/watch?v=abc",
        marketplace_links=[],
    )
    defaults.update(kwargs)
    return Item.create(**defaults)


def make_link(name="Wildberries", url="https://wb.ru/1", price="12 990 ₽") -> MarketplaceLink:
    return MarketplaceLink(name=Name(name), url=url, price=price)


class TestItemCreate:
    def test_create_sets_all_fields(self):
        cat_id = uuid.uuid4()
        item = Item.create(
            name="iPhone 15 Pro",
            short_description="Краткое описание",
            description="Полное описание",
            category_id=cat_id,
            youtube_url="https://youtube.com/watch?v=abc",
            marketplace_links=[],
        )
        assert str(item.name) == "iPhone 15 Pro"
        assert item.short_description == "Краткое описание"
        assert item.description == "Полное описание"
        assert item.category_id == cat_id
        assert item.youtube_url == "https://youtube.com/watch?v=abc"
        assert item.marketplace_links == []
        assert item.is_published is False

    def test_create_with_marketplace_links(self):
        links = [make_link("Wildberries", "https://wb.ru/1", "12 990 ₽")]
        item = make_item(marketplace_links=links)
        assert len(item.marketplace_links) == 1

    def test_create_with_none_youtube_url(self):
        item = make_item(youtube_url=None)
        assert item.youtube_url is None

    def test_create_with_invalid_name_raises(self):
        with pytest.raises(InvalidNameError):
            make_item(name="X")  # 1-char name

    def test_create_gives_unique_ids(self):
        i1 = make_item()
        i2 = make_item()
        assert i1.id != i2.id

    def test_timestamps_are_utc(self):
        from datetime import timezone
        item = make_item()
        assert item.created_at.tzinfo == timezone.utc
        assert item.updated_at.tzinfo == timezone.utc


class TestItemChangeName:
    def test_change_name_updates_field(self):
        item = make_item()
        item.change_name("Samsung Galaxy S24")
        assert str(item.name) == "Samsung Galaxy S24"

    def test_change_name_with_invalid_raises(self):
        item = make_item()
        with pytest.raises(InvalidNameError):
            item.change_name("X")

    def test_change_name_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_name("Samsung Galaxy S24")
        assert item.updated_at > before


class TestItemChangeShortDescription:
    def test_updates_field(self):
        item = make_item()
        item.change_short_description("Новое краткое описание")
        assert item.short_description == "Новое краткое описание"

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_short_description("New short desc")
        assert item.updated_at > before


class TestItemChangeDescription:
    def test_updates_field(self):
        item = make_item()
        item.change_description("Новое полное описание")
        assert item.description == "Новое полное описание"

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_description("New desc")
        assert item.updated_at > before


class TestItemChangeCategoryId:
    def test_updates_field(self):
        item = make_item()
        new_cat_id = uuid.uuid4()
        item.change_category_id(new_cat_id)
        assert item.category_id == new_cat_id

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_category_id(uuid.uuid4())
        assert item.updated_at > before


class TestItemChangeYoutubeUrl:
    def test_updates_field(self):
        item = make_item()
        item.change_youtube_url("https://youtube.com/watch?v=xyz")
        assert item.youtube_url == "https://youtube.com/watch?v=xyz"

    def test_set_to_none(self):
        item = make_item()
        item.change_youtube_url(None)
        assert item.youtube_url is None

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_youtube_url("https://youtube.com/new")
        assert item.updated_at > before


class TestItemChangeMarketplaceLinks:
    def test_updates_field(self):
        item = make_item()
        links = [make_link(), make_link("Ozon", "https://ozon.ru/2", "13 000 ₽")]
        item.change_marketplace_links(links)
        assert len(item.marketplace_links) == 2

    def test_set_to_empty(self):
        item = make_item(marketplace_links=[make_link()])
        item.change_marketplace_links([])
        assert item.marketplace_links == []

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_marketplace_links([make_link()])
        assert item.updated_at > before


class TestItemChangeIsPublished:
    def test_publish_item(self):
        item = make_item()
        item.change_is_published(True)
        assert item.is_published is True

    def test_unpublish_item(self):
        item = make_item()
        item.change_is_published(True)
        item.change_is_published(False)
        assert item.is_published is False

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.change_is_published(True)
        assert item.updated_at > before


class TestSetViewCount:
    def test_sets_valid_count(self):
        item = make_item()
        item.set_view_count(100)
        assert item.view_count == 100

    def test_sets_minimum_value_one(self):
        item = make_item()
        item.set_view_count(1)
        assert item.view_count == 1

    def test_sets_large_value(self):
        item = make_item()
        item.set_view_count(999_999)
        assert item.view_count == 999_999

    def test_calls_touch(self):
        item = make_item()
        before = item.updated_at
        time.sleep(0.005)
        item.set_view_count(42)
        assert item.updated_at > before

    def test_raises_on_zero(self):
        item = make_item()
        with pytest.raises(ValueError):
            item.set_view_count(0)

    def test_raises_on_negative(self):
        item = make_item()
        with pytest.raises(ValueError):
            item.set_view_count(-5)

    def test_raises_on_bool(self):
        item = make_item()
        with pytest.raises(ValueError):
            item.set_view_count(True)  # bool is subclass of int — must be rejected

    def test_raises_on_float(self):
        item = make_item()
        with pytest.raises((ValueError, TypeError)):
            item.set_view_count(1.5)  # type: ignore[arg-type]
