from dataclasses import dataclass

from src.backend.application.comment.dtos.create_comment import CreateCommentCommand, CreateCommentResult
from src.backend.application.comment.errors import CommentNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.comment.entity import Comment
from src.backend.domain.user.entity import User


@dataclass
class CreateCommentUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: CreateCommentCommand) -> CreateCommentResult:
        async with self.uow:
            if cmd.parent_id is not None:
                parent = await self.uow.comments.get_by_id(cmd.parent_id)
                if parent is None:
                    raise CommentNotFoundError("parent comment not found")

            comment = Comment.create(
                item_id=cmd.item_id,
                user_id=self.user.id,
                parent_id=cmd.parent_id,
                body=cmd.body,
            )
            created = await self.uow.comments.create(comment)
            await self.uow.commit()

            return CreateCommentResult(
                id=created.id,
                item_id=created.item_id,
                user_id=created.user_id,
                parent_id=created.parent_id,
                body=created.body,
                is_deleted=created.is_deleted,
                created_at=created.created_at,
                updated_at=created.updated_at,
            )
