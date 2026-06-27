import pytest

from src.backend.domain.user.error import InvalidUsernameError
from src.backend.domain.user.value_objects.username.value_object import Username


# Pattern: ^[a-zA-Z0-9](?:[a-zA-Z0-9_]{1,28}[a-zA-Z0-9])?$
# Valid: 1 char  OR  3–30 chars (start/end alphanumeric, middle may have _)
# NOTE: 2-char usernames do NOT match this regex (known edge case)

VALID_USERNAMES = [
    "a",            # single char is valid per current regex
    "abc",
    "john_doe",
    "User123",
    "user_name_1",
    "a" * 30,       # max length (30 chars)
    "A1b2C3",
]

INVALID_USERNAMES = [
    "",             # empty
    "ab",           # 2 chars — regex gap: optional group needs ≥2 chars
    "a" * 31,       # 31 chars — too long
    "_username",    # starts with underscore
    "username_",    # ends with underscore
    "user-name",    # hyphen not allowed
    "user name",    # space not allowed
    "user@name",    # @ not allowed
    "user.name",    # dot not allowed
]


class TestUsernameValid:
    @pytest.mark.parametrize("value", VALID_USERNAMES)
    def test_valid_username_created(self, value):
        u = Username(value)
        assert u.value == value

    def test_str_returns_value(self):
        u = Username("john_doe")
        assert str(u) == "john_doe"


class TestUsernameInvalid:
    @pytest.mark.parametrize("value", INVALID_USERNAMES)
    def test_invalid_username_raises(self, value):
        with pytest.raises(InvalidUsernameError):
            Username(value)

    def test_invalid_username_is_domain_error(self):
        from src.backend.domain.shared.errors import DomainError
        with pytest.raises(DomainError):
            Username("")
