from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.backend.application.comment.dtos.list_comments import CommentResult


class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    parent_id: UUID | None
    body: str
    is_deleted: bool
    created_at: datetime
    children: list[CommentResponse] = []

    @classmethod
    def from_result(cls, result: CommentResult) -> CommentResponse:
        return cls(
            id=result.id,
            user_id=result.user_id,
            parent_id=result.parent_id,
            body=result.body,
            is_deleted=result.is_deleted,
            created_at=result.created_at,
            children=[cls.from_result(c) for c in result.children],
        )


CommentResponse.model_rebuild()


class CreateCommentRequest(BaseModel):
    body: str
    parent_id: UUID | None = None


class UpdateCommentRequest(BaseModel):
    body: str
