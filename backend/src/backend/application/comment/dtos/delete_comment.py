from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteCommentCommand:
    comment_id: UUID
