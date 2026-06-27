from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt

from src.backend.application.shared.errors import NotAuthorizedError
from src.backend.config import get_settings


class JWTTokenService:
    def encode(self, user_id: UUID, is_refresh: bool = False) -> str:
        settings = get_settings()
        expires = (
            settings.JWT_REFRESH_TOKEN_EXPIRES
            if is_refresh
            else settings.JWT_ACCESS_TOKEN_EXPIRES
        )
        payload = {
            "sub": str(user_id),
            "type": "refresh" if is_refresh else "access",
            "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=expires),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def decode(self, token: str, is_refresh: bool = False) -> UUID:
        settings = get_settings()
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
        except JWTError:
            raise NotAuthorizedError("Invalid credentials")
        expected_type = "refresh" if is_refresh else "access"
        if payload.get("type") != expected_type:
            raise NotAuthorizedError("Invalid token type")
        return UUID(payload["sub"])

    def get_token_type(self) -> str:
        return "bearer"
