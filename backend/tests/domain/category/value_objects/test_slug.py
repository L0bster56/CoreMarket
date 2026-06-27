import pytest

from src.backend.domain.category.value_objects.slug.error import InvalidSlugError
from src.backend.domain.category.value_objects.slug.value_object import Slug


VALID_SLUGS = [
    "electronics",
    "smart-phones",
    "iphone-15-pro",
    "abc123",
    "a",
    "category-1",
    "a-b-c",
    "123",
]

INVALID_SLUGS = [
    "",                  # empty
    "Hello",             # uppercase
    "hello world",       # space
    "-hello",            # starts with hyphen
    "hello-",            # ends with hyphen
    "hello--world",      # double hyphen
    "hello_world",       # underscore not allowed
    "UPPER",             # uppercase
    "Hello-World",       # mixed case
    "café",              # non-ASCII
]


class TestSlugValid:
    @pytest.mark.parametrize("value", VALID_SLUGS)
    def test_valid_slug_created(self, value):
        slug = Slug(value)
        assert slug.value == value

    def test_slug_is_frozen(self):
        slug = Slug("electronics")
        with pytest.raises((AttributeError, TypeError)):
            slug.value = "other"  # type: ignore[misc]

    def test_equal_slugs(self):
        s1 = Slug("electronics")
        s2 = Slug("electronics")
        assert s1 == s2

    def test_different_slugs_not_equal(self):
        s1 = Slug("phones")
        s2 = Slug("tablets")
        assert s1 != s2


class TestSlugInvalid:
    @pytest.mark.parametrize("value", INVALID_SLUGS)
    def test_invalid_slug_raises(self, value):
        with pytest.raises(InvalidSlugError):
            Slug(value)

    def test_invalid_slug_is_domain_error(self):
        from src.backend.domain.shared.errors import DomainError
        with pytest.raises(DomainError):
            Slug("Invalid Slug")
