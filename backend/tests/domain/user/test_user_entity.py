import time
import uuid

import pytest

from src.backend.domain.user.entity import User, UserRole
from src.backend.domain.shared.value_objects.email.error import InvalidEmailError
from src.backend.domain.user.error import InvalidUsernameError


class TestUserRole:
    def test_user_role_values(self):
        assert UserRole.user == "user"
        assert UserRole.admin == "admin"

    def test_user_role_is_str(self):
        assert isinstance(UserRole.user, str)
        assert isinstance(UserRole.admin, str)


class TestUserCreate:
    def test_create_with_defaults(self):
        user = User.create(
            username="john_doe",
            email="john@example.com",
            hashed_password="hashed_secret",
        )
        assert str(user.username) == "john_doe"
        assert str(user.email) == "john@example.com"
        assert user.hashed_password == "hashed_secret"
        assert user.role == UserRole.user
        assert user.is_active is True
        assert user.avatar_url is None

    def test_create_with_admin_role(self):
        user = User.create(
            username="admin_user",
            email="admin@example.com",
            hashed_password="hashed",
            role=UserRole.admin,
        )
        assert user.role == UserRole.admin

    def test_create_gives_unique_ids(self):
        u1 = User.create("user_one", "one@example.com", "hash1")
        u2 = User.create("user_two", "two@example.com", "hash2")
        assert u1.id != u2.id

    def test_create_with_invalid_username_raises(self):
        with pytest.raises(InvalidUsernameError):
            User.create(
                username="ab",   # 2-char is invalid per current regex
                email="user@example.com",
                hashed_password="hash",
            )

    def test_create_with_invalid_email_raises(self):
        with pytest.raises(InvalidEmailError):
            User.create(
                username="john_doe",
                email="not-an-email",
                hashed_password="hash",
            )

    def test_id_is_uuid(self):
        user = User.create("john_doe", "john@example.com", "hash")
        assert isinstance(user.id, uuid.UUID)

    def test_timestamps_set_on_create(self):
        from datetime import timezone
        user = User.create("john_doe", "john@example.com", "hash")
        assert user.created_at.tzinfo == timezone.utc
        assert user.updated_at.tzinfo == timezone.utc


class TestUserChangePassword:
    def test_change_password_updates_hash(self):
        user = User.create("john_doe", "john@example.com", "old_hash")
        user.change_password("new_hash")
        assert user.hashed_password == "new_hash"

    def test_change_password_calls_touch(self):
        user = User.create("john_doe", "john@example.com", "old_hash")
        before = user.updated_at
        time.sleep(0.005)
        user.change_password("new_hash")
        assert user.updated_at > before


class TestUserChangeEmail:
    def test_change_email_updates_email(self):
        user = User.create("john_doe", "john@example.com", "hash")
        user.change_email("new@example.com")
        assert str(user.email) == "new@example.com"

    def test_change_email_with_invalid_raises(self):
        user = User.create("john_doe", "john@example.com", "hash")
        with pytest.raises(InvalidEmailError):
            user.change_email("bad-email")

    def test_change_email_calls_touch(self):
        user = User.create("john_doe", "john@example.com", "hash")
        before = user.updated_at
        time.sleep(0.005)
        user.change_email("new@example.com")
        assert user.updated_at > before


class TestUserEndureActive:
    def test_returns_true_when_active(self):
        user = User.create("john_doe", "john@example.com", "hash")
        assert user.endure_active() is True

    def test_returns_false_when_inactive(self):
        user = User.create("john_doe", "john@example.com", "hash")
        user.is_active = False
        assert user.endure_active() is False


class TestUserEquality:
    def test_same_id_equal(self):
        uid = uuid.uuid4()
        u1 = User.create("user_one", "one@example.com", "hash1")
        u2 = User.create("user_two", "two@example.com", "hash2")
        object.__setattr__(u1, "id", uid) if hasattr(u1, "__dataclass_fields__") else None
        # Use direct construction to test equality
        from src.backend.domain.shared.value_objects.email.value_object import Email
        from src.backend.domain.user.value_objects.username.value_object import Username
        from datetime import datetime, timezone
        u_a = User(
            id=uid,
            username=Username("user_aaa"),
            email=Email("a@example.com"),
            hashed_password="h",
            role=UserRole.user,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        u_b = User(
            id=uid,
            username=Username("user_bbb"),
            email=Email("b@example.com"),
            hashed_password="h2",
            role=UserRole.admin,
            created_at=datetime.now(tz=timezone.utc),
            updated_at=datetime.now(tz=timezone.utc),
        )
        assert u_a == u_b

    def test_different_id_not_equal(self):
        u1 = User.create("user_one", "one@example.com", "hash1")
        u2 = User.create("user_two", "two@example.com", "hash2")
        assert u1 != u2
