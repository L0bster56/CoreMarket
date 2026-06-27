from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class CreateCategoryCommand:
    name: str
    slug: str
    description: str | None = field(default=None)
    image_url: str | None = field(default=None)


@dataclass
class CreateCategoryResult:
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    created_at: datetime
    updated_at: datetime
