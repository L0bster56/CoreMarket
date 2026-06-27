from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.backend.domain.tag.entity import Tag


class TagRepository(Protocol):

    async def get_by_id(self, tag_id: UUID) -> Tag | None: ...

    async def get_by_slug(self, slug: str) -> Tag | None: ...

    async def list_all(self) -> list[Tag]: ...

    async def create(self, tag: Tag) -> Tag: ...

    async def delete(self, tag: Tag) -> None: ...

    async def exists_slug(self, slug: str, exclude_id: UUID | None = None) -> bool: ...
