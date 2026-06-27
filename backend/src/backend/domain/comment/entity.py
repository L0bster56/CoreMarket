from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.mixins import TimeActionMixin


@dataclass(eq=False)
class Comment(BaseEntity, TimeActionMixin):
    item_id: UUID
    user_id: UUID
    parent_id: UUID | None
    body: str
    is_deleted: bool = False

    @classmethod
    def create(
            cls,
            item_id: UUID,
            user_id: UUID,
            parent_id: UUID | None,
            body: str,
    ) -> "Comment":
        return cls(
            item_id=item_id,
            user_id=user_id,
            parent_id=parent_id,
            body=body,
        )

    def soft_delete(self) -> None:
        self.is_deleted = True
        self.touch()

    def change_body(self, body: str) -> None:
        self.body = body
        self.touch()
