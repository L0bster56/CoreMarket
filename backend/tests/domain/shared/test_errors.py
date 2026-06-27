import pytest

from src.backend.domain.shared.errors import DomainError, PermissionDeniedError


class TestDomainError:
    def test_is_exception(self):
        assert issubclass(DomainError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(DomainError):
            raise DomainError("test error")

    def test_message_preserved(self):
        with pytest.raises(DomainError, match="something went wrong"):
            raise DomainError("something went wrong")


class TestPermissionDeniedError:
    def test_is_domain_error(self):
        assert issubclass(PermissionDeniedError, DomainError)

    def test_is_exception(self):
        assert issubclass(PermissionDeniedError, Exception)

    def test_can_be_raised(self):
        with pytest.raises(PermissionDeniedError):
            raise PermissionDeniedError("access denied")

    def test_caught_as_domain_error(self):
        with pytest.raises(DomainError):
            raise PermissionDeniedError("access denied")

    def test_message_preserved(self):
        with pytest.raises(PermissionDeniedError, match="forbidden"):
            raise PermissionDeniedError("forbidden")
