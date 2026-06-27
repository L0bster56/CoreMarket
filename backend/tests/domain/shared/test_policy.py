import pytest

from src.backend.domain.shared.errors import PermissionDeniedError
from src.backend.domain.shared.policy import Policy


class AllowPolicy(Policy):
    def is_satisfied_by(self) -> bool:
        return True

    def _error_message(self) -> str:
        return "should never appear"


class DenyPolicy(Policy):
    def is_satisfied_by(self) -> bool:
        return False

    def _error_message(self) -> str:
        return "action is forbidden"


class DenyWithMessagePolicy(Policy):
    def __init__(self, message: str):
        self._message = message

    def is_satisfied_by(self) -> bool:
        return False

    def _error_message(self) -> str:
        return self._message


class TestPolicyEnforce:
    def test_allow_policy_does_not_raise(self):
        AllowPolicy().enforce()  # must not raise

    def test_deny_policy_raises_permission_denied(self):
        with pytest.raises(PermissionDeniedError):
            DenyPolicy().enforce()

    def test_error_message_passed_to_exception(self):
        with pytest.raises(PermissionDeniedError, match="action is forbidden"):
            DenyPolicy().enforce()

    def test_custom_message_in_exception(self):
        msg = "only admins allowed"
        with pytest.raises(PermissionDeniedError, match=msg):
            DenyWithMessagePolicy(msg).enforce()

    def test_permission_denied_is_domain_error(self):
        from src.backend.domain.shared.errors import DomainError
        with pytest.raises(DomainError):
            DenyPolicy().enforce()
