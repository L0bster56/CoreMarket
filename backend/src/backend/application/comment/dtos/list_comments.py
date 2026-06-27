from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class ListCommentsCommand:
    item_id: UUID


@dataclass
class CommentResult:
    id: UUID
    item_id: UUID
    user_id: UUID
    parent_id: UUID | None
    body: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    children: list[CommentResult] = field(default_factory=list)


@dataclass
class ListCommentsResult:
    items: list[CommentResult]
