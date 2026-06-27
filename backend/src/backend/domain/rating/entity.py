from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.rating.value_objects.score import Score
from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.mixins import TimeActionMixin


@dataclass(eq=False)
class Rating(BaseEntity, TimeActionMixin):
    item_id: UUID
    user_id: UUID
    score: Score

    @classmethod
    def create(cls, item_id: UUID, user_id: UUID, score: Score) -> "Rating":
        return cls(item_id=item_id, user_id=user_id, score=score)

    def update(self, score: int) -> None:
        self.score = Score(score)
        self.touch()

    def change_score(self, score: int) -> None:
        self.update(score)