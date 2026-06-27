from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class GetCommentCommand:
    comment_id: UUID


@dataclass
class GetCommentResult:
    id: UUID
    item_id: UUID
    user_id: UUID
    parent_id: UUID | None
    body: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
