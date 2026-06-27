from dataclasses import dataclass
from uuid import UUID

from src.backend.application.item.dtos.create_item import MarketplaceLinkData


@dataclass
class UpdateItemCommand:
    item_id: UUID
    title: str | None = None
    short_description: str | None = None
    description: str | None = None
    category_id: UUID | None = None
    youtube_url: str | None = None
    marketplace_links: list[MarketplaceLinkData] | None = None
    is_published: bool | None = None
    view_count: int | None = None
