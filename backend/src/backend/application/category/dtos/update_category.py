from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class UpdateCategoryCommand:
    category_id: UUID
    name: str | None = field(default=None)
    description: str | None = field(default=None)
    image_url: str | None = field(default=None)
