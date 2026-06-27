from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.shared.entity import BaseEntity


@dataclass(eq=False)
class Characteristic(BaseEntity):
    item_id: UUID
    name: str
    value: str
    group: str | None = None

    @classmethod
    def create(cls, item_id: UUID, name: str, value: str, group: str | None = None) -> "Characteristic":
        return cls(item_id=item_id, name=name, value=value, group=group)
