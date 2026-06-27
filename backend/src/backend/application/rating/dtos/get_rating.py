from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetRatingCommand:
    item_id: UUID


@dataclass
class GetRatingResult:
    item_id: UUID
    avg_score: float | None
    count: int
