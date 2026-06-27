from dataclasses import dataclass
from uuid import UUID


@dataclass
class AddItemTagCommand:
    item_id: UUID
    tag_id: UUID
