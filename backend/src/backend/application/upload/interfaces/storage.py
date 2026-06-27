from typing import Protocol


class FileStorage(Protocol):
    async def save(self, data: bytes, section: str, ext: str) -> str:
        # Returns the storage key (e.g. "items/uuid.jpg"), not a full URL
        ...

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str: ...

    async def get_presigned_urls(self, keys: list[str], expires_in: int = 3600) -> dict[str, str]: ...
