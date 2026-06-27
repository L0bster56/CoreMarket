from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteCharacteristicCommand:
    characteristic_id: UUID
