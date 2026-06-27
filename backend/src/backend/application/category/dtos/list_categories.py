from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ListCategoriesCommand:
    pass


@dataclass
class CategoryItem:
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class ListCategoriesResult:
    items: list[CategoryItem]
