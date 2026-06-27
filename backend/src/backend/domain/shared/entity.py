from dataclasses import dataclass

from src.backend.domain.shared.mixins import IDMixin

@dataclass(eq=False)
class BaseEntity(IDMixin):
    """
    Базовая сущность

    Attributes:
        id: Уникальный идентификатор
    """

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


