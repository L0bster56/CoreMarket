from dataclasses import dataclass
from uuid import UUID


@dataclass
class RemoveItemTagCommand:
    item_id: UUID
    tag_id: UUID
