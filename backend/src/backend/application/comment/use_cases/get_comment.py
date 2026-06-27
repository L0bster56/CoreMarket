from dataclasses import dataclass

from src.backend.application.comment.dtos.get_comment import GetCommentCommand, GetCommentResult
from src.backend.application.comment.errors import CommentNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class GetCommentUseCase:
    """
    UseCase: получение комментария по ID.

    Ответственность:
        - Проверка существования комментария
        - Возврат данных комментария
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetCommentCommand) -> GetCommentResult:
        """
        Args:
            cmd (GetCommentCommand): ID комментария

        Returns:
            GetCommentResult: данные комментария

        Raises:
            CommentNotFoundError: если комментарий не найден
        """
        async with self.uow:
            comment = await self.uow.comments.get_by_id(cmd.comment_id)

            if comment is None:
                raise CommentNotFoundError("comment not found")

            return GetCommentResult(
                id=comment.id,
                item_id=comment.item_id,
                user_id=comment.user_id,
                parent_id=comment.parent_id,
                body=comment.body,
                is_deleted=comment.is_deleted,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
