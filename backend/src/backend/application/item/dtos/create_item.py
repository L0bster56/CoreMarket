from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class MarketplaceLinkData:
    name: str
    url: str
    price: str | None = None


@dataclass
class CreateItemCommand:
    title: str
    short_description: str
    description: str
    category_id: UUID
    youtube_url: str | None = None
    marketplace_links: list[MarketplaceLinkData] = field(default_factory=list)


@dataclass
class CreateItemResult:
    id: UUID
    title: str
    short_description: str
    description: str
    category_id: UUID
    youtube_url: str | None
    marketplace_links: list[MarketplaceLinkData]
    is_published: bool
    created_at: datetime
    updated_at: datetime
