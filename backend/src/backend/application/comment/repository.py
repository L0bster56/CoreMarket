from __future__ import annotations

from typing import Protocol
from uuid import UUID

from src.backend.domain.comment.entity import Comment


class CommentRepository(Protocol):

    async def get_by_id(self, comment_id: UUID) -> Comment | None: ...

    async def get_by_item(self, item_id: UUID) -> list[Comment]: ...

    async def create(self, comment: Comment) -> Comment: ...

    async def update(self, comment: Comment) -> None: ...

    async def soft_delete(self, comment: Comment) -> None: ...
