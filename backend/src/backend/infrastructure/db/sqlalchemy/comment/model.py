from sqlalchemy import Column, Text, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin, TimeStampMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


class CommentModel(Base, UUIDMixin, TimeStampMixin):
    __tablename__ = 'comments'

    item_id = Column(UUID(as_uuid=True), ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('comments.id'), nullable=True)
    body = Column(Text, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    children = relationship(
        'CommentModel',
        lazy='selectin',
        foreign_keys='CommentModel.parent_id',
        primaryjoin='CommentModel.parent_id == CommentModel.id',
    )
