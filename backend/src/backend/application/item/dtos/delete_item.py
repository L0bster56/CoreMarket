from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteItemCommand:
    item_id: UUID
