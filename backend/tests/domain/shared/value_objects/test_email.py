import pytest

from src.backend.domain.shared.value_objects.email.error import (
    EmailError,
    InvalidEmailError,
)
from src.backend.domain.shared.value_objects.email.value_object import Email


VALID_EMAILS = [
    "user@example.com",
    "user.name@example.com",
    "user+tag@example.co.uk",
    "user123@subdomain.example.org",
    "a@b.io",
    "USER@EXAMPLE.COM",
    "user_name@example-domain.com",
]

INVALID_EMAILS = [
    "",
    "notanemail",
    "@example.com",
    "user@",
    "user@.com",
    "user@com",
    "user @example.com",
    "user@exam ple.com",
    "user@@example.com",
]


class TestEmailValid:
    @pytest.mark.parametrize("value", VALID_EMAILS)
    def test_valid_email_created(self, value):
        email = Email(value)
        assert email.value == value

    def test_str_returns_value(self):
        email = Email("user@example.com")
        assert str(email) == "user@example.com"

    def test_email_is_frozen(self):
        email = Email("user@example.com")
        with pytest.raises((AttributeError, TypeError)):
            email.value = "other@example.com"  # type: ignore[misc]

    def test_equal_emails(self):
        e1 = Email("user@example.com")
        e2 = Email("user@example.com")
        assert e1 == e2

    def test_different_emails_not_equal(self):
        e1 = Email("a@example.com")
        e2 = Email("b@example.com")
        assert e1 != e2


class TestEmailInvalid:
    @pytest.mark.parametrize("value", INVALID_EMAILS)
    def test_invalid_email_raises(self, value):
        with pytest.raises(InvalidEmailError):
            Email(value)

    def test_invalid_email_error_is_email_error(self):
        with pytest.raises(EmailError):
            Email("bad-email")

    def test_invalid_email_error_is_domain_error(self):
        from src.backend.domain.shared.errors import DomainError
        with pytest.raises(DomainError):
            Email("bad-email")
