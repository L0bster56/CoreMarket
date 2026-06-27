"""
Tests for BcryptHasher (infrastructure/security/bcrypt/hasher.py).

Covers:
- hash(): returns non-plaintext bcrypt string
- hash uniqueness: same password produces different hashes (random salt)
- verify(): correct password returns True
- verify(): wrong password returns False
- case sensitivity: passwords are case-sensitive
"""
from __future__ import annotations

import pytest

from src.backend.infrastructure.security.bcrypt.hasher import BcryptHasher


class TestBcryptHasherHash:
    def test_returns_non_empty_string(self):
        result = BcryptHasher().hash("mypassword")
        assert isinstance(result, str) and len(result) > 0

    def test_hash_is_not_plaintext(self):
        result = BcryptHasher().hash("mypassword")
        assert result != "mypassword"

    def test_hash_starts_with_bcrypt_prefix(self):
        result = BcryptHasher().hash("mypassword")
        assert result.startswith("$2b$") or result.startswith("$2a$")

    def test_two_hashes_of_same_password_differ(self):
        hasher = BcryptHasher()
        h1 = hasher.hash("samepassword")
        h2 = hasher.hash("samepassword")
        assert h1 != h2

    def test_hash_of_empty_string(self):
        result = BcryptHasher().hash("")
        assert isinstance(result, str) and len(result) > 0

    def test_hash_of_unicode_password(self):
        result = BcryptHasher().hash("пароль123")
        assert isinstance(result, str) and len(result) > 0

    def test_hash_long_password(self):
        long_pw = "x" * 64
        result = BcryptHasher().hash(long_pw)
        assert isinstance(result, str) and len(result) > 0


class TestBcryptHasherVerify:
    def test_correct_password_returns_true(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("correct_password")
        assert hasher.verify("correct_password", hashed) is True

    def test_wrong_password_returns_false(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("correct_password")
        assert hasher.verify("wrong_password", hashed) is False

    def test_empty_password_verifies_empty_hash(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("")
        assert hasher.verify("", hashed) is True

    def test_empty_password_fails_nonempty_hash(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("somepassword")
        assert hasher.verify("", hashed) is False

    def test_nonempty_password_fails_empty_hash(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("")
        assert hasher.verify("notEmpty", hashed) is False

    def test_multiple_hashes_of_same_password_all_verify(self):
        hasher = BcryptHasher()
        hashed1 = hasher.hash("password123")
        hashed2 = hasher.hash("password123")
        assert hasher.verify("password123", hashed1) is True
        assert hasher.verify("password123", hashed2) is True

    def test_verify_is_case_sensitive_lower(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("Password")
        assert hasher.verify("password", hashed) is False

    def test_verify_is_case_sensitive_upper(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("Password")
        assert hasher.verify("PASSWORD", hashed) is False

    def test_verify_is_case_sensitive_correct_case(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("Password")
        assert hasher.verify("Password", hashed) is True

    def test_unicode_password_verifies(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("пароль123")
        assert hasher.verify("пароль123", hashed) is True

    def test_unicode_wrong_password_fails(self):
        hasher = BcryptHasher()
        hashed = hasher.hash("пароль123")
        assert hasher.verify("пароль456", hashed) is False
