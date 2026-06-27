from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, delete, exists

from src.backend.application.tag.repository import TagRepository
from src.backend.domain.tag.entity import Tag
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository
from src.backend.infrastructure.db.sqlalchemy.tag.mapper import to_model, to_entity
from src.backend.infrastructure.db.sqlalchemy.tag.model import TagModel


class SqlAlchemyTagRepository(SqlAlchemyRepository, TagRepository):

    async def get_by_id(self, tag_id: UUID) -> Tag | None:
        stmt = select(TagModel).where(TagModel.id == tag_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Tag | None:
        stmt = select(TagModel).where(TagModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def list_all(self) -> list[Tag]:
        stmt = select(TagModel)
        result = await self.session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def create(self, tag: Tag) -> Tag:
        model = to_model(tag)
        self.session.add(model)
        await self.session.flush()
        return to_entity(model)

    async def delete(self, tag: Tag) -> None:
        stmt = delete(TagModel).where(TagModel.id == tag.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def exists_slug(self, slug: str, exclude_id: UUID | None = None) -> bool:
        condition = TagModel.slug == slug
        if exclude_id:
            condition = condition & (TagModel.id != exclude_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()
