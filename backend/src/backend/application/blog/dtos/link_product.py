from dataclasses import dataclass
from uuid import UUID


@dataclass
class LinkProductCommand:
    slug: str
    product_id: UUID
    display_order: int = 0


@dataclass
class LinkProductResult:
    id: UUID
    product_id: UUID
    display_order: int


@dataclass
class UnlinkProductCommand:
    slug: str
    link_id: UUID
