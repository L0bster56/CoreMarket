from sqlalchemy import Column, Integer, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin, TimeStampMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


class RatingModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'ratings'

    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)

    item = relationship(
        'ItemModel',
        backref='ratings',
        lazy='selectin',
    )
    user = relationship(
        'UserModel',
        backref='ratings',
        lazy='selectin',
    )

    __table_args__ = (
        UniqueConstraint('item_id', 'user_id', name='uq_rating_item_user'),
    )
