from typing import Protocol
from uuid import UUID


class TokenService(Protocol):
    """
    Interface сервиса токенов
    """
    def encode(self, user_id: UUID, is_refresh: bool = False) -> str: ...

    def decode(self, token: str, is_refresh: bool = False) -> UUID: ...

    def get_token_type(self) -> str: ...