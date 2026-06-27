from dataclasses import dataclass

from src.backend.application.comment.dtos.delete_comment import DeleteCommentCommand
from src.backend.application.comment.errors import CommentNotFoundError, CommentEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class DeleteCommentUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: DeleteCommentCommand) -> None:
        async with self.uow:
            comment = await self.uow.comments.get_by_id(cmd.comment_id)

            if comment is None:
                raise CommentNotFoundError("comment not found")

            if comment.user_id != self.user.id and self.user.role != UserRole.admin:
                raise CommentEditForbiddenError("not allowed to delete this comment")

            comment.soft_delete()
            await self.uow.comments.soft_delete(comment)
            await self.uow.commit()
