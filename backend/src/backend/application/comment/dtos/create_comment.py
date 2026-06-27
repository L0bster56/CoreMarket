from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateCommentCommand:
    item_id: UUID
    body: str
    parent_id: UUID | None = None


@dataclass
class CreateCommentResult:
    id: UUID
    item_id: UUID
    user_id: UUID
    parent_id: UUID | None
    body: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
