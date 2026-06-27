from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, delete, exists

from src.backend.application.category.repository import CategoryRepository
from src.backend.domain.category.entity import Category
from src.backend.infrastructure.db.sqlalchemy.category.mapper import to_model, to_entity
from src.backend.infrastructure.db.sqlalchemy.category.model import CategoryModel
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository


class SqlAlchemyCategoryRepository(SqlAlchemyRepository, CategoryRepository):

    async def get_by_id(self, category_id: UUID) -> Category | None:
        stmt = select(CategoryModel).where(CategoryModel.id == category_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(CategoryModel).where(CategoryModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def list_all(self) -> list[Category]:
        stmt = select(CategoryModel)
        result = await self.session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def create(self, category: Category) -> Category:
        model = to_model(category)
        self.session.add(model)
        await self.session.flush()
        return to_entity(model)

    async def update(self, category: Category) -> None:
        model = to_model(category)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, category: Category) -> None:
        stmt = delete(CategoryModel).where(CategoryModel.id == category.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def exists_slug(self, slug: str, exclude_id: UUID | None = None) -> bool:
        condition = CategoryModel.slug == slug
        if exclude_id:
            condition = condition & (CategoryModel.id != exclude_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()
