from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, delete, update, func, or_

from src.backend.application.item.dtos.list_items import ListItemsFilters
from src.backend.application.item.repository import CharacteristicRepository, GalleryRepository, ItemRepository
from src.backend.domain.item.characteristic import Characteristic
from src.backend.domain.item.entity import Item
from src.backend.domain.item.gallery import Gallery
from src.backend.domain.tag.entity import Tag
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository
from src.backend.infrastructure.db.sqlalchemy.item.mapper import (
    characteristic_to_entity,
    characteristic_to_model,
    gallery_to_entity,
    gallery_to_model,
    item_to_entity,
    item_to_model,
    tag_to_entity,
)
from src.backend.infrastructure.db.sqlalchemy.item.model import CharacteristicModel, GalleryModel, ItemModel, item_tags
from src.backend.infrastructure.db.sqlalchemy.rating.model import RatingModel
from src.backend.infrastructure.db.sqlalchemy.tag.model import TagModel


class SqlAlchemyItemRepository(SqlAlchemyRepository, ItemRepository):

    def _apply_filters(self, stmt, filters: ListItemsFilters):
        if filters.search:
            stmt = stmt.where(or_(
                ItemModel.name.ilike(f'%{filters.search}%'),
                ItemModel.short_description.ilike(f'%{filters.search}%'),
            ))
        if filters.category_id:
            stmt = stmt.where(ItemModel.category_id == filters.category_id)
        if filters.tag:
            stmt = (
                stmt
                .join(item_tags, ItemModel.id == item_tags.c.item_id)
                .join(TagModel, TagModel.id == item_tags.c.tag_id)
                .where(TagModel.slug == filters.tag)
            )
        if filters.min_rating is not None:
            avg_subq = (
                select(func.avg(RatingModel.score))
                .where(RatingModel.item_id == ItemModel.id)
                .correlate(ItemModel)
                .scalar_subquery()
            )
            stmt = stmt.where(avg_subq >= filters.min_rating)
        if filters.is_published is not None:
            stmt = stmt.where(ItemModel.is_published == filters.is_published)
        return stmt

    async def get_by_id(self, item_id: UUID) -> Item | None:
        stmt = select(ItemModel).where(ItemModel.id == item_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return item_to_entity(model) if model else None

    async def list(self, filters: ListItemsFilters) -> list[Item]:
        stmt = select(ItemModel).distinct()
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(filters.offset).limit(filters.limit)
        result = await self.session.execute(stmt)
        return [item_to_entity(m) for m in result.scalars().all()]

    async def count(self, filters: ListItemsFilters) -> int:
        inner = self._apply_filters(select(ItemModel.id).distinct(), filters).subquery()
        stmt = select(func.count()).select_from(inner)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(self, item: Item) -> Item:
        model = item_to_model(item)
        self.session.add(model)
        await self.session.flush()
        return item_to_entity(model)

    async def update(self, item: Item) -> None:
        model = item_to_model(item)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, item: Item) -> None:
        stmt = delete(ItemModel).where(ItemModel.id == item.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_tags(self, item_id: UUID) -> list[Tag]:
        stmt = (
            select(TagModel)
            .join(item_tags, TagModel.id == item_tags.c.tag_id)
            .where(item_tags.c.item_id == item_id)
        )
        result = await self.session.execute(stmt)
        return [tag_to_entity(m) for m in result.scalars().all()]

    async def add_tag(self, item_id: UUID, tag_id: UUID) -> None:
        stmt = item_tags.insert().values(item_id=item_id, tag_id=tag_id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def remove_tag(self, item_id: UUID, tag_id: UUID) -> None:
        stmt = delete(item_tags).where(
            item_tags.c.item_id == item_id,
            item_tags.c.tag_id == tag_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def increment_view_count(self, item_id: UUID) -> None:
        stmt = (
            update(ItemModel)
            .where(ItemModel.id == item_id)
            .values(view_count=ItemModel.view_count + 1)
        )
        await self.session.execute(stmt)
        await self.session.flush()


class SqlAlchemyCharacteristicRepository(SqlAlchemyRepository, CharacteristicRepository):

    async def get_by_id(self, characteristic_id: UUID) -> Characteristic | None:
        stmt = select(CharacteristicModel).where(CharacteristicModel.id == characteristic_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return characteristic_to_entity(model) if model else None

    async def list_by_item(self, item_id: UUID) -> list[Characteristic]:
        stmt = select(CharacteristicModel).where(CharacteristicModel.item_id == item_id)
        result = await self.session.execute(stmt)
        return [characteristic_to_entity(m) for m in result.scalars().all()]

    async def create(self, characteristic: Characteristic) -> Characteristic:
        model = characteristic_to_model(characteristic)
        self.session.add(model)
        await self.session.flush()
        return characteristic_to_entity(model)

    async def update(self, characteristic: Characteristic) -> None:
        model = characteristic_to_model(characteristic)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, characteristic: Characteristic) -> None:
        stmt = delete(CharacteristicModel).where(CharacteristicModel.id == characteristic.id)
        await self.session.execute(stmt)
        await self.session.flush()


class SqlAlchemyGalleryRepository(SqlAlchemyRepository, GalleryRepository):

    async def get_by_id(self, gallery_id: UUID) -> Gallery | None:
        stmt = select(GalleryModel).where(GalleryModel.id == gallery_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return gallery_to_entity(model) if model else None

    async def list_by_item(self, item_id: UUID) -> list[Gallery]:
        stmt = select(GalleryModel).where(GalleryModel.item_id == item_id)
        result = await self.session.execute(stmt)
        return [gallery_to_entity(m) for m in result.scalars().all()]

    async def get_preview_keys(self, item_ids: list[UUID]) -> dict[UUID, str | None]:
        if not item_ids:
            return {}
        stmt = (
            select(GalleryModel.item_id, GalleryModel.image_url)
            .where(GalleryModel.item_id.in_(item_ids))
            .distinct(GalleryModel.item_id)
            .order_by(GalleryModel.item_id)
        )
        result = await self.session.execute(stmt)
        return {row.item_id: row.image_url for row in result.all()}

    async def create(self, gallery: Gallery) -> Gallery:
        model = gallery_to_model(gallery)
        self.session.add(model)
        await self.session.flush()
        return gallery_to_entity(model)

    async def delete(self, gallery: Gallery) -> None:
        stmt = delete(GalleryModel).where(GalleryModel.id == gallery.id)
        await self.session.execute(stmt)
        await self.session.flush()
