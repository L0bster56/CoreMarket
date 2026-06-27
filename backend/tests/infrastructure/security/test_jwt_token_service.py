"""
Tests for JWTTokenService (infrastructure/security/jose/token.py).

Covers:
- encode: returns valid JWT with correct payload (sub, type, exp)
- decode: returns correct UUID for valid token
- expired token: raises NotAuthorizedError
- invalid signature: raises NotAuthorizedError
- malformed token: raises NotAuthorizedError
- wrong token type mismatch: raises NotAuthorizedError
- get_token_type: returns "bearer"
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from jose import jwt

from src.backend.application.shared.errors import NotAuthorizedError
from src.backend.infrastructure.security.jose.token import JWTTokenService

_MODULE = "src.backend.infrastructure.security.jose.token"


def _settings(
    *,
    secret: str = "supersecretkey-for-tests",
    algorithm: str = "HS256",
    access_exp: int = 3600,
    refresh_exp: int = 86400,
) -> MagicMock:
    s = MagicMock()
    s.JWT_SECRET = secret
    s.JWT_ALGORITHM = algorithm
    s.JWT_ACCESS_TOKEN_EXPIRES = access_exp
    s.JWT_REFRESH_TOKEN_EXPIRES = refresh_exp
    return s


def _make_expired_token(user_id: UUID, s: MagicMock, is_refresh: bool = False) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh" if is_refresh else "access",
        "exp": datetime.now(tz=timezone.utc) - timedelta(seconds=60),
    }
    return jwt.encode(payload, s.JWT_SECRET, algorithm=s.JWT_ALGORITHM)


class TestJWTTokenServiceEncode:
    async def test_returns_non_empty_string(self):
        with patch(f"{_MODULE}.get_settings", return_value=_settings()):
            token = JWTTokenService().encode(uuid4())
        assert isinstance(token, str) and len(token) > 0

    async def test_jwt_has_three_parts(self):
        with patch(f"{_MODULE}.get_settings", return_value=_settings()):
            token = JWTTokenService().encode(uuid4())
        assert token.count(".") == 2

    async def test_access_token_has_type_access(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            token = JWTTokenService().encode(user_id, is_refresh=False)
        payload = jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALGORITHM])
        assert payload["type"] == "access"

    async def test_refresh_token_has_type_refresh(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            token = JWTTokenService().encode(user_id, is_refresh=True)
        payload = jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALGORITHM])
        assert payload["type"] == "refresh"

    async def test_sub_matches_user_id(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            token = JWTTokenService().encode(user_id)
        payload = jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALGORITHM])
        assert payload["sub"] == str(user_id)

    async def test_access_token_expiry_uses_access_exp(self):
        s = _settings(access_exp=1800)
        user_id = uuid4()
        before = datetime.now(tz=timezone.utc)
        with patch(f"{_MODULE}.get_settings", return_value=s):
            token = JWTTokenService().encode(user_id, is_refresh=False)
        payload = jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        diff = (exp - before).total_seconds()
        assert 1798 <= diff <= 1802

    async def test_refresh_token_expiry_uses_refresh_exp(self):
        s = _settings(refresh_exp=604800)
        user_id = uuid4()
        before = datetime.now(tz=timezone.utc)
        with patch(f"{_MODULE}.get_settings", return_value=s):
            token = JWTTokenService().encode(user_id, is_refresh=True)
        payload = jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        diff = (exp - before).total_seconds()
        assert 604798 <= diff <= 604802

    async def test_default_is_access_token(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            token = JWTTokenService().encode(user_id)
        payload = jwt.decode(token, s.JWT_SECRET, algorithms=[s.JWT_ALGORITHM])
        assert payload["type"] == "access"


class TestJWTTokenServiceDecode:
    async def test_decode_returns_correct_uuid(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            svc = JWTTokenService()
            token = svc.encode(user_id)
            result = svc.decode(token)
        assert result == user_id

    async def test_decode_returns_uuid_type(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            svc = JWTTokenService()
            token = svc.encode(user_id)
            result = svc.decode(token)
        assert isinstance(result, UUID)

    async def test_decode_refresh_token(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            svc = JWTTokenService()
            token = svc.encode(user_id, is_refresh=True)
            result = svc.decode(token, is_refresh=True)
        assert result == user_id

    async def test_decode_raises_on_expired_access_token(self):
        s = _settings()
        user_id = uuid4()
        expired = _make_expired_token(user_id, s, is_refresh=False)
        with patch(f"{_MODULE}.get_settings", return_value=s):
            with pytest.raises(NotAuthorizedError):
                JWTTokenService().decode(expired, is_refresh=False)

    async def test_decode_raises_on_expired_refresh_token(self):
        s = _settings()
        user_id = uuid4()
        expired = _make_expired_token(user_id, s, is_refresh=True)
        with patch(f"{_MODULE}.get_settings", return_value=s):
            with pytest.raises(NotAuthorizedError):
                JWTTokenService().decode(expired, is_refresh=True)

    async def test_decode_raises_on_invalid_signature(self):
        s_encode = _settings(secret="secret-A")
        s_decode = _settings(secret="secret-B")
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s_encode):
            token = JWTTokenService().encode(user_id)
        with patch(f"{_MODULE}.get_settings", return_value=s_decode):
            with pytest.raises(NotAuthorizedError):
                JWTTokenService().decode(token)

    async def test_decode_raises_on_malformed_token(self):
        s = _settings()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            with pytest.raises(NotAuthorizedError):
                JWTTokenService().decode("not.a.valid.jwt")

    async def test_decode_raises_on_garbage_string(self):
        s = _settings()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            with pytest.raises(NotAuthorizedError):
                JWTTokenService().decode("garbage")

    async def test_decode_raises_on_empty_string(self):
        s = _settings()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            with pytest.raises(NotAuthorizedError):
                JWTTokenService().decode("")

    async def test_decode_raises_when_access_used_as_refresh(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            svc = JWTTokenService()
            access_token = svc.encode(user_id, is_refresh=False)
            with pytest.raises(NotAuthorizedError):
                svc.decode(access_token, is_refresh=True)

    async def test_decode_raises_when_refresh_used_as_access(self):
        s = _settings()
        user_id = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            svc = JWTTokenService()
            refresh_token = svc.encode(user_id, is_refresh=True)
            with pytest.raises(NotAuthorizedError):
                svc.decode(refresh_token, is_refresh=False)

    async def test_decode_different_users_return_different_uuids(self):
        s = _settings()
        user_a = uuid4()
        user_b = uuid4()
        with patch(f"{_MODULE}.get_settings", return_value=s):
            svc = JWTTokenService()
            token_a = svc.encode(user_a)
            token_b = svc.encode(user_b)
            result_a = svc.decode(token_a)
            result_b = svc.decode(token_b)
        assert result_a != result_b
        assert result_a == user_a
        assert result_b == user_b


class TestJWTTokenServiceGetTokenType:
    def test_returns_bearer(self):
        assert JWTTokenService().get_token_type() == "bearer"

    def test_is_lowercase(self):
        result = JWTTokenService().get_token_type()
        assert result == result.lower()
