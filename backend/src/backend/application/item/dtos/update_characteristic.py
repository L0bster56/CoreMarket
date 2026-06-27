from dataclasses import dataclass
from uuid import UUID


@dataclass
class UpdateCharacteristicCommand:
    characteristic_id: UUID
    name: str | None = None
    value: str | None = None
    group: str | None = None


@dataclass
class UpdateCharacteristicResult:
    id: UUID
    item_id: UUID
    name: str
    value: str
    group: str | None = None
