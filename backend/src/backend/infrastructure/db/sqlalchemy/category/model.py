from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin, TimeStampMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


class CategoryModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'categories'

    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    items = relationship(
        'ItemModel',
        backref='category',
        lazy='selectin',
    )
