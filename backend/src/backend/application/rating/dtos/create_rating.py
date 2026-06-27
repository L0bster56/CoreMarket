from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateRatingCommand:
    item_id: UUID
    score: int


@dataclass
class CreateRatingResult:
    id: UUID
    item_id: UUID
    user_id: UUID
    score: int
    created_at: datetime
    updated_at: datetime
