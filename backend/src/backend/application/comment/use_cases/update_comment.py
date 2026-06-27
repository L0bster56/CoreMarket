from dataclasses import dataclass

from src.backend.application.comment.dtos.update_comment import UpdateCommentCommand
from src.backend.application.comment.errors import CommentNotFoundError, CommentEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User


@dataclass
class UpdateCommentUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: UpdateCommentCommand) -> None:
        async with self.uow:
            comment = await self.uow.comments.get_by_id(cmd.comment_id)

            if comment is None:
                raise CommentNotFoundError("comment not found")

            if comment.user_id != self.user.id:
                raise CommentEditForbiddenError("not allowed to edit this comment")

            comment.change_body(cmd.body)
            await self.uow.comments.update(comment)
            await self.uow.commit()
