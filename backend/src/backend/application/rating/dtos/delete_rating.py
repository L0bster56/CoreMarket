from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteRatingCommand:
    item_id: UUID
