from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from src.backend.application.item.dtos.get_item import GetItemResult


class MarketplaceLinkSchema(BaseModel):
    name: str
    url: str
    price: str | None = None


class CharacteristicSchema(BaseModel):
    id: UUID
    group: str | None = None
    name: str
    value: str


class GalleryImageSchema(BaseModel):
    id: UUID
    image_url: str


class TagSchema(BaseModel):
    id: UUID
    name: str
    slug: str


class ItemResponse(BaseModel):
    id: UUID
    title: str
    short_description: str
    description: str
    category_id: UUID
    youtube_url: str | None
    marketplace_links: list[MarketplaceLinkSchema]
    is_published: bool
    view_count: int
    characteristics: list[CharacteristicSchema]
    gallery: list[GalleryImageSchema]
    tags: list[TagSchema]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_result(cls, result: GetItemResult) -> "ItemResponse":
        return cls(
            id=result.id,
            title=result.title,
            short_description=result.short_description,
            description=result.description,
            category_id=result.category_id,
            youtube_url=result.youtube_url,
            marketplace_links=[
                MarketplaceLinkSchema(name=m.name, url=m.url, price=m.price)
                for m in result.marketplace_links
            ],
            is_published=result.is_published,
            view_count=result.view_count,
            characteristics=[
                CharacteristicSchema(id=c.id, group=c.group, name=c.name, value=c.value)
                for c in result.characteristics
            ],
            gallery=[
                GalleryImageSchema(id=g.id, image_url=g.image_url)
                for g in result.gallery
            ],
            tags=[
                TagSchema(id=t.id, name=t.name, slug=t.slug)
                for t in result.tags
            ],
            created_at=result.created_at,
            updated_at=result.updated_at,
        )


class ItemListEntry(BaseModel):
    id: UUID
    title: str
    short_description: str
    category_id: UUID
    youtube_url: str | None
    is_published: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    preview_image: str | None = None


class ItemListResponse(BaseModel):
    items: list[ItemListEntry]
    total: int


class CreateItemRequest(BaseModel):
    title: str
    short_description: str
    description: str
    category_id: UUID
    youtube_url: str | None = None
    marketplace_links: list[MarketplaceLinkSchema] = []


class UpdateItemRequest(BaseModel):
    title: str | None = None
    short_description: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    youtube_url: str | None = None
    marketplace_links: list[MarketplaceLinkSchema] | None = None
    is_published: bool | None = None
    view_count: int | None = Field(default=None, ge=1, description="Количество просмотров (≥ 1)")


class AddTagRequest(BaseModel):
    tag_id: UUID


class AddCharacteristicRequest(BaseModel):
    group: str | None = None
    name: str
    value: str


class UpdateCharacteristicRequest(BaseModel):
    group: str | None = None
    name: str | None = None
    value: str | None = None


class AddGalleryImageRequest(BaseModel):
    image_url: str
