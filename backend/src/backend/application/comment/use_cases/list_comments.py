from dataclasses import dataclass

from src.backend.application.comment.dtos.list_comments import (
    CommentResult,
    ListCommentsCommand,
    ListCommentsResult,
)
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class ListCommentsUseCase:
    """
    UseCase: получение комментариев объекта в виде дерева.

    Ответственность:
        - Загрузка всех комментариев по item_id
        - Построение иерархии parent → children в памяти
    """

    uow: UnitOfWork

    async def execute(self, cmd: ListCommentsCommand) -> ListCommentsResult:
        """
        Args:
            cmd (ListCommentsCommand): ID объекта

        Returns:
            ListCommentsResult: дерево комментариев верхнего уровня
        """
        async with self.uow:
            all_comments = await self.uow.comments.get_by_item(cmd.item_id)

            nodes: dict = {
                c.id: CommentResult(
                    id=c.id,
                    item_id=c.item_id,
                    user_id=c.user_id,
                    parent_id=c.parent_id,
                    body=c.body,
                    is_deleted=c.is_deleted,
                    created_at=c.created_at,
                    updated_at=c.updated_at,
                )
                for c in all_comments
            }

            roots: list[CommentResult] = []
            for c in all_comments:
                node = nodes[c.id]
                if c.parent_id and c.parent_id in nodes:
                    nodes[c.parent_id].children.append(node)
                else:
                    roots.append(node)

            return ListCommentsResult(items=roots)
