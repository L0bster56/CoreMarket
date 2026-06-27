from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.shared.entity import BaseEntity


@dataclass(eq=False)
class Gallery(BaseEntity):
    item_id: UUID
    image_url: str

    @classmethod
    def create(cls, item_id: UUID, image_url: str) -> "Gallery":
        return cls(item_id=item_id, image_url=image_url)