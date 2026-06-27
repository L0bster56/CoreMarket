import uuid

import pytest

from src.backend.domain.blog.entity import BlogTag
from src.backend.domain.category.value_objects.slug.error import InvalidSlugError
from src.backend.domain.shared.value_objects.name.error import InvalidNameError


class TestBlogTagCreate:
    def test_create_sets_name_and_slug(self):
        tag = BlogTag.create(name="Python", slug="python")
        assert str(tag.name) == "Python"
        assert str(tag.slug) == "python"

    def test_create_gives_unique_ids(self):
        t1 = BlogTag.create(name="Python", slug="python")
        t2 = BlogTag.create(name="Django", slug="django")
        assert t1.id != t2.id

    def test_id_is_uuid(self):
        tag = BlogTag.create(name="Python", slug="python")
        assert isinstance(tag.id, uuid.UUID)

    def test_create_with_invalid_name_raises(self):
        with pytest.raises(InvalidNameError):
            BlogTag.create(name="X", slug="x")

    def test_create_with_invalid_slug_raises(self):
        with pytest.raises(InvalidSlugError):
            BlogTag.create(name="Python", slug="Invalid Slug!")


class TestBlogTagChangeName:
    def test_change_name_updates_field(self):
        tag = BlogTag.create(name="Python", slug="python")
        tag.change_name("Django")
        assert str(tag.name) == "Django"

    def test_change_name_with_invalid_raises(self):
        tag = BlogTag.create(name="Python", slug="python")
        with pytest.raises(InvalidNameError):
            tag.change_name("X")


class TestBlogTagEquality:
    def test_same_id_equal(self):
        t1 = BlogTag.create(name="Python", slug="python")
        t2 = BlogTag.create(name="Django", slug="django")
        t2.id = t1.id
        assert t1 == t2

    def test_different_id_not_equal(self):
        t1 = BlogTag.create(name="Python", slug="python")
        t2 = BlogTag.create(name="Django", slug="django")
        assert t1 != t2
