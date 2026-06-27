from sqlalchemy import Column, String

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


class TagModel(Base, UUIDMixin):
    __tablename__ = 'tags'

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)


