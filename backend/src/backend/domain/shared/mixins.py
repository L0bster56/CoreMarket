import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass(kw_only=True)
class IDMixin:
    """
    Mixin для уникальных идентификаторов сущностей

    Attributes:
        id: Уникальный идентификатор
    """
    id: UUID = field(default_factory=uuid.uuid4)


@dataclass(kw_only=True)
class TimeActionMixin:
    """
    Mixin для временный меток
    используется как дополнение к основной сущности

    Attributes:
        created_at: Временная метка создания
        updated_at: Временная метка обновления
    """
    created_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))

    def touch(self) -> None:
        """
        Будет фиксировать время изменения
        """
        self.updated_at = datetime.now(tz=timezone.utc)
