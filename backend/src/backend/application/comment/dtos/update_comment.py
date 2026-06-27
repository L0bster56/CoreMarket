from dataclasses import dataclass
from uuid import UUID


@dataclass
class UpdateCommentCommand:
    comment_id: UUID
    body: str
