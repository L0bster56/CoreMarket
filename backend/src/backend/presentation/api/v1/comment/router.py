from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from src.backend.application.comment.dtos.create_comment import CreateCommentCommand
from src.backend.application.comment.dtos.delete_comment import DeleteCommentCommand
from src.backend.application.comment.dtos.list_comments import ListCommentsCommand
from src.backend.application.comment.dtos.update_comment import UpdateCommentCommand
from src.backend.presentation.api.v1.comment.dependencies import (
    CreateCommentDep,
    DeleteCommentDep,
    ListCommentsDep,
    UpdateCommentDep,
)
from src.backend.presentation.api.v1.comment.schemas import (
    CommentResponse,
    CreateCommentRequest,
    UpdateCommentRequest,
)
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema

router = APIRouter(
    prefix="/items/{item_id}/comments",
    tags=["comments"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


@router.get("", status_code=status.HTTP_200_OK, response_model=list[CommentResponse])
async def list_comments(item_id: UUID, uc: ListCommentsDep) -> list[CommentResponse]:
    result = await uc.execute(ListCommentsCommand(item_id=item_id))
    return [CommentResponse.from_result(c) for c in result.items]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
async def create_comment(
    item_id: UUID,
    body: CreateCommentRequest,
    uc: CreateCommentDep,
) -> CommentResponse:
    result = await uc.execute(
        CreateCommentCommand(item_id=item_id, body=body.body, parent_id=body.parent_id)
    )
    return CommentResponse(
        id=result.id,
        user_id=result.user_id,
        parent_id=result.parent_id,
        body=result.body,
        is_deleted=result.is_deleted,
        created_at=result.created_at,
        children=[],
    )


@router.patch("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_comment(
    item_id: UUID,
    comment_id: UUID,
    body: UpdateCommentRequest,
    uc: UpdateCommentDep,
) -> None:
    await uc.execute(UpdateCommentCommand(comment_id=comment_id, body=body.body))


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    item_id: UUID,
    comment_id: UUID,
    uc: DeleteCommentDep,
) -> None:
    await uc.execute(DeleteCommentCommand(comment_id=comment_id))
