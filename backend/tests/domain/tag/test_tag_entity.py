import uuid

import pytest

from src.backend.domain.category.value_objects.slug.error import InvalidSlugError
from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.value_objects.name.error import InvalidNameError
from src.backend.domain.tag.entity import Tag


class TestTagCreate:
    def test_create_tag(self):
        slug = Slug("flagship")
        tag = Tag.create(name="Flagship", slug=slug)
        assert str(tag.name) == "Flagship"
        assert tag.slug.value == "flagship"

    def test_create_gives_unique_ids(self):
        t1 = Tag.create("Flagship", Slug("flagship"))
        t2 = Tag.create("Budget", Slug("budget"))
        assert t1.id != t2.id

    def test_id_is_uuid(self):
        tag = Tag.create("Flagship", Slug("flagship"))
        assert isinstance(tag.id, uuid.UUID)

    def test_create_with_invalid_name_raises(self):
        with pytest.raises(InvalidNameError):
            Tag.create(name="X", slug=Slug("x"))  # 1-char name

    def test_create_with_invalid_slug_raises(self):
        with pytest.raises(InvalidSlugError):
            Tag.create(name="Flagship", slug=Slug("Invalid Slug"))


class TestTagEquality:
    def test_same_id_equal(self):
        uid = uuid.uuid4()
        from src.backend.domain.shared.value_objects.name.value_object import Name
        t1 = Tag(id=uid, name=Name("Flagship"), slug=Slug("flagship"))
        t2 = Tag(id=uid, name=Name("Budget"), slug=Slug("budget"))
        assert t1 == t2

    def test_different_id_not_equal(self):
        t1 = Tag.create("Flagship", Slug("flagship"))
        t2 = Tag.create("Budget", Slug("budget"))
        assert t1 != t2
