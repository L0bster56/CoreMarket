from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class GetItemCommand:
    item_id: UUID


@dataclass
class MarketplaceLinkItem:
    name: str
    url: str
    price: str | None


@dataclass
class CharacteristicItem:
    id: UUID
    name: str
    value: str
    group: str | None = None


@dataclass
class GalleryItem:
    id: UUID
    image_url: str


@dataclass
class TagItem:
    id: UUID
    name: str
    slug: str


@dataclass
class GetItemResult:
    id: UUID
    title: str
    short_description: str
    description: str
    category_id: UUID
    youtube_url: str | None
    marketplace_links: list[MarketplaceLinkItem]
    is_published: bool
    view_count: int
    characteristics: list[CharacteristicItem]
    gallery: list[GalleryItem]
    tags: list[TagItem]
    created_at: datetime
    updated_at: datetime
