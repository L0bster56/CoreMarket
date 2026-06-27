from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class GetCategoryCommand:
    category_id: UUID


@dataclass
class GetCategoryResult:
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    created_at: datetime
    updated_at: datetime
