from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.application.comment.use_cases.create_comment import CreateCommentUseCase
from src.backend.application.comment.use_cases.delete_comment import DeleteCommentUseCase
from src.backend.application.comment.use_cases.list_comments import ListCommentsUseCase
from src.backend.application.comment.use_cases.update_comment import UpdateCommentUseCase
from src.backend.domain.comment.entity import Comment
from src.backend.infrastructure.db.sqlalchemy.comment.repository import SqlAlchemyCommentRepository
from src.backend.presentation.api.v1.auth.dependencies import CurrentUserDep
from src.backend.presentation.api.v1.core.dependencies import UoWDep, get_db


async def get_comment_repo(session: AsyncSession = Depends(get_db)) -> SqlAlchemyCommentRepository:
    return SqlAlchemyCommentRepository(session=session)


CommentRepoDep = Annotated[SqlAlchemyCommentRepository, Depends(get_comment_repo)]


async def get_current_comment(comment_id: UUID, repo: CommentRepoDep) -> Comment:
    comment = await repo.get_by_id(comment_id)
    if comment is None or comment.is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


CurrentCommentDep = Annotated[Comment, Depends(get_current_comment)]


def get_list_comments_use_case(uow: UoWDep) -> ListCommentsUseCase:
    return ListCommentsUseCase(uow=uow)


ListCommentsDep = Annotated[ListCommentsUseCase, Depends(get_list_comments_use_case)]


def get_create_comment_use_case(uow: UoWDep, user: CurrentUserDep) -> CreateCommentUseCase:
    return CreateCommentUseCase(uow=uow, user=user)


CreateCommentDep = Annotated[CreateCommentUseCase, Depends(get_create_comment_use_case)]


def get_update_comment_use_case(uow: UoWDep, user: CurrentUserDep) -> UpdateCommentUseCase:
    return UpdateCommentUseCase(uow=uow, user=user)


UpdateCommentDep = Annotated[UpdateCommentUseCase, Depends(get_update_comment_use_case)]


def get_delete_comment_use_case(uow: UoWDep, user: CurrentUserDep) -> DeleteCommentUseCase:
    return DeleteCommentUseCase(uow=uow, user=user)


DeleteCommentDep = Annotated[DeleteCommentUseCase, Depends(get_delete_comment_use_case)]
