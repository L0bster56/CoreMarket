import pytest

from src.backend.domain.shared.value_objects.name.error import InvalidNameError
from src.backend.domain.shared.value_objects.name.value_object import Name


VALID_NAMES = [
    "Ab",              # min 2 chars
    "John",
    "John Doe",
    "Ноутбук",         # cyrillic
    "iPhone 15 Pro",   # mix of latin, digits, space
    "A" * 100,         # max 100 chars
    "42",              # digits only
    "Смартфон Samsung",
]

INVALID_NAMES = [
    "",                # empty
    "A",               # 1 char (too short)
    "A" * 101,         # 101 chars (too long)
    "Hello!",          # special char
    "Name@Domain",     # @ symbol
    "test-name",       # hyphen not allowed
    "name_test",       # underscore not allowed
]


class TestNameValid:
    @pytest.mark.parametrize("value", VALID_NAMES)
    def test_valid_name_created(self, value):
        name = Name(value)
        assert name.value == value

    def test_str_returns_value(self):
        name = Name("iPhone 15")
        assert str(name) == "iPhone 15"

    def test_name_is_frozen(self):
        name = Name("iPhone")
        with pytest.raises((AttributeError, TypeError)):
            name.value = "Samsung"  # type: ignore[misc]

    def test_equal_names(self):
        n1 = Name("iPhone")
        n2 = Name("iPhone")
        assert n1 == n2

    def test_different_names_not_equal(self):
        n1 = Name("iPhone")
        n2 = Name("Samsung")
        assert n1 != n2


class TestNameInvalid:
    @pytest.mark.parametrize("value", INVALID_NAMES)
    def test_invalid_name_raises(self, value):
        with pytest.raises(InvalidNameError):
            Name(value)

    def test_invalid_name_is_domain_error(self):
        from src.backend.domain.shared.errors import DomainError
        with pytest.raises(DomainError):
            Name("")
