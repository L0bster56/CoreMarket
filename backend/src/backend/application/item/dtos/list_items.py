from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class ListItemsFilters:
    search: str | None = None
    category_id: UUID | None = None
    tag: str | None = None
    min_rating: float | None = None
    is_published: bool | None = None
    limit: int = 20
    offset: int = 0


@dataclass
class ListItemsCommand:
    filters: ListItemsFilters = field(default_factory=ListItemsFilters)


@dataclass
class ItemListEntry:
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


@dataclass
class ListItemsResult:
    items: list[ItemListEntry]
    total: int
