from sqlalchemy import Column, String

from src.backend.infrastructure.db.sqlalchemy.core.mixins import UUIDMixin, TimeStampMixin, ActiveMixin
from src.backend.infrastructure.db.sqlalchemy.core.models import Base


class UserModel(Base, UUIDMixin, TimeStampMixin, ActiveMixin):
    __tablename__ = 'users'

    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    avatar_url = Column(String(500), nullable=True)
