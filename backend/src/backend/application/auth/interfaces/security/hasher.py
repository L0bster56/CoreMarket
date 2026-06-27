from typing import Protocol


class Hasher(Protocol):
    """
    Interface для хэширования
    """
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed_password: str) -> bool: ...