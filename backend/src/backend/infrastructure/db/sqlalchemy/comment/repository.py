from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update

from src.backend.application.comment.repository import CommentRepository
from src.backend.domain.comment.entity import Comment
from src.backend.infrastructure.db.sqlalchemy.comment.mapper import to_model, to_entity
from src.backend.infrastructure.db.sqlalchemy.comment.model import CommentModel
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository


class SqlAlchemyCommentRepository(SqlAlchemyRepository, CommentRepository):

    async def get_by_id(self, comment_id: UUID) -> Comment | None:
        stmt = select(CommentModel).where(CommentModel.id == comment_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def get_by_item(self, item_id: UUID) -> list[Comment]:
        stmt = (
            select(CommentModel)
            .where(CommentModel.item_id == item_id)
            .where(CommentModel.is_deleted == False)
            .order_by(CommentModel.created_at)
        )
        result = await self.session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def create(self, comment: Comment) -> Comment:
        model = to_model(comment)
        self.session.add(model)
        await self.session.flush()
        return to_entity(model)

    async def update(self, comment: Comment) -> None:
        model = to_model(comment)
        await self.session.merge(model)
        await self.session.flush()

    async def soft_delete(self, comment: Comment) -> None:
        stmt = (
            update(CommentModel)
            .where(CommentModel.id == comment.id)
            .values(is_deleted=True)
        )
        await self.session.execute(stmt)
        await self.session.flush()
