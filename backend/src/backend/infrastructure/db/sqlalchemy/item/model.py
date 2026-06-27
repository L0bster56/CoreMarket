from sqlalchemy import Column, Integer, String, Text, Boolean, UUID, ForeignKey, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin, TimeStampMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


item_tags = Table(
    'item_tags',
    Base.metadata,
    Column('item_id', UUID(as_uuid=True),
    ForeignKey('items.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', UUID(as_uuid=True),
    ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)# ?



class ItemModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'items'

    name = Column(String(500), nullable=False)
    short_description = Column(String(1000), nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.id'), nullable=False)
    youtube_url = Column(String(500), nullable=True)
    marketplace_links = Column(JSONB, nullable=True)
    is_published = Column(Boolean, default=False, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)

    characteristics = relationship(
        'CharacteristicModel',
        backref='item',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    gallery = relationship(
        'GalleryModel',
        backref='item',
        lazy='selectin',
        cascade='all, delete-orphan',
    )
    tags = relationship(
        'TagModel',
        secondary=item_tags,
        backref='items',
        lazy='selectin',
    )


class CharacteristicModel(Base, UUIDMixin):
    __tablename__ = 'characteristics'

    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    group = Column(String(255), nullable=True)
    name = Column(String(255), nullable=False)
    value = Column(String(500), nullable=False)


class GalleryModel(Base, UUIDMixin):
    __tablename__ = 'gallery'

    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    image_url = Column(String(500), nullable=False)
