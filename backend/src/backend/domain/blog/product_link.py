from dataclasses import dataclass, field
from uuid import UUID

from src.backend.domain.shared.entity import BaseEntity


@dataclass(eq=False)
class BlogProductLink(BaseEntity):
    blog_post_id: UUID
    product_id: UUID
    display_order: int = field(default=0)
