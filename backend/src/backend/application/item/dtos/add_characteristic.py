from dataclasses import dataclass
from uuid import UUID


@dataclass
class AddCharacteristicCommand:
    item_id: UUID
    name: str
    value: str
    group: str | None = None


@dataclass
class AddCharacteristicResult:
    id: UUID
    item_id: UUID
    name: str
    value: str
    group: str | None = None
