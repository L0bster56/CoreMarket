import time
import uuid

import pytest

from src.backend.domain.category.entity import Category
from src.backend.domain.category.value_objects.slug.error import InvalidSlugError
from src.backend.domain.shared.value_objects.name.error import InvalidNameError


class TestCategoryCreate:
    def test_create_required_fields(self):
        cat = Category.create(name="Electronics", slug="electronics")
        assert str(cat.name) == "Electronics"
        assert cat.slug.value == "electronics"
        assert cat.description is None
        assert cat.image_url is None

    def test_create_with_all_fields(self):
        cat = Category.create(
            name="Smart Phones",
            slug="smart-phones",
            description="All smartphones",
            image_url="/media/categories/phones.jpg",
        )
        assert str(cat.name) == "Smart Phones"
        assert cat.slug.value == "smart-phones"
        assert cat.description == "All smartphones"
        assert cat.image_url == "/media/categories/phones.jpg"

    def test_create_gives_unique_ids(self):
        c1 = Category.create("Electronics", "electronics")
        c2 = Category.create("Tablets", "tablets")
        assert c1.id != c2.id

    def test_create_with_invalid_name_raises(self):
        with pytest.raises(InvalidNameError):
            Category.create(name="A", slug="a")  # 1-char name is invalid

    def test_create_with_invalid_slug_raises(self):
        with pytest.raises(InvalidSlugError):
            Category.create(name="Electronics", slug="Invalid Slug")

    def test_timestamps_set_on_create(self):
        from datetime import timezone
        cat = Category.create("Electronics", "electronics")
        assert cat.created_at.tzinfo == timezone.utc
        assert cat.updated_at.tzinfo == timezone.utc


class TestCategoryChangeName:
    def test_change_name_updates_field(self):
        cat = Category.create("Electronics", "electronics")
        cat.change_name("Gadgets")
        assert str(cat.name) == "Gadgets"

    def test_change_name_with_invalid_raises(self):
        cat = Category.create("Electronics", "electronics")
        with pytest.raises(InvalidNameError):
            cat.change_name("X")  # 1 char — too short

    def test_change_name_calls_touch(self):
        cat = Category.create("Electronics", "electronics")
        before = cat.updated_at
        time.sleep(0.005)
        cat.change_name("Gadgets")
        assert cat.updated_at > before


class TestCategoryChangeDescription:
    def test_change_description_updates_field(self):
        cat = Category.create("Electronics", "electronics")
        cat.change_description("Updated description")
        assert cat.description == "Updated description"

    def test_change_description_to_none(self):
        cat = Category.create("Electronics", "electronics", description="Old desc")
        cat.change_description(None)
        assert cat.description is None

    def test_change_description_calls_touch(self):
        cat = Category.create("Electronics", "electronics")
        before = cat.updated_at
        time.sleep(0.005)
        cat.change_description("New desc")
        assert cat.updated_at > before


class TestCategoryChangeImageUrl:
    def test_change_image_url_updates_field(self):
        cat = Category.create("Electronics", "electronics")
        cat.change_image_url("/media/categories/new.jpg")
        assert cat.image_url == "/media/categories/new.jpg"

    def test_change_image_url_to_none(self):
        cat = Category.create("Electronics", "electronics", image_url="/old.jpg")
        cat.change_image_url(None)
        assert cat.image_url is None

    def test_change_image_url_calls_touch(self):
        cat = Category.create("Electronics", "electronics")
        before = cat.updated_at
        time.sleep(0.005)
        cat.change_image_url("/new.jpg")
        assert cat.updated_at > before


class TestCategoryEquality:
    def test_same_id_equal(self):
        uid = uuid.uuid4()
        from src.backend.domain.category.value_objects.slug.value_object import Slug
        from src.backend.domain.shared.value_objects.name.value_object import Name
        from datetime import datetime, timezone
        c1 = Category(
            id=uid, name=Name("Electronics"), slug=Slug("electronics"),
            description=None, image_url=None,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        c2 = Category(
            id=uid, name=Name("Tablets"), slug=Slug("tablets"),
            description="Other", image_url="/img.jpg",
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        assert c1 == c2

    def test_different_id_not_equal(self):
        c1 = Category.create("Electronics", "electronics")
        c2 = Category.create("Tablets", "tablets")
        assert c1 != c2
