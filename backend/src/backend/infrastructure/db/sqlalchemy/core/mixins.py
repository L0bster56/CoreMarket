import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, BigInteger, Boolean, UUID


class UUIDMixin:
    id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class IntIdMixin:
    id = Column(BigInteger, primary_key=True, autoincrement=True)

class TimeStampMixin:
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

class ActiveMixin:
    is_active = Column(Boolean, default=True)