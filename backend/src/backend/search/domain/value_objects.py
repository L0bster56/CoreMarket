from dataclasses import dataclass, field
from uuid import UUID


@dataclass
class ItemSearchParams:
    search: str | None = None
    category_id: UUID | None = None
    tags: list[str] = field(default_factory=list)
    min_rating: float | None = None
    is_published: bool | None = True
    sort_by: str = "relevance"
    limit: int = 20
    offset: int = 0
