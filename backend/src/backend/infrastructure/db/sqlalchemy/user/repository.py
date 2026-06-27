from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, delete, exists

from src.backend.application.user.repository import UserRepository
from src.backend.domain.user.entity import User
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository
from src.backend.infrastructure.db.sqlalchemy.user.mapper import to_model, to_entity
from src.backend.infrastructure.db.sqlalchemy.user.model import UserModel


class SqlAlchemyUserRepository(SqlAlchemyRepository, UserRepository):

    async def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return to_entity(user) if user else None

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return to_entity(user) if user else None

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return to_entity(user) if user else None

    async def create(self, user: User) -> User:
        model = to_model(user)
        self.session.add(model)
        await self.session.flush()
        return to_entity(model)

    async def update(self, user: User) -> None:
        model = to_model(user)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, user: User) -> None:
        stmt = delete(UserModel).where(UserModel.id == user.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def list_all(self) -> list[User]:
        stmt = select(UserModel)
        result = await self.session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def list_by_ids(self, user_ids: list[UUID]) -> list[User]:
        stmt = select(UserModel).where(UserModel.id.in_(user_ids))
        result = await self.session.execute(stmt)
        return [to_entity(m) for m in result.scalars().all()]

    async def exists_username(self, username: str, user_id: UUID = None) -> bool:
        condition = UserModel.username == username
        if user_id:
            condition = condition & (UserModel.id != user_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def exists_email(self, email: str, user_id: UUID = None) -> bool:
        condition = UserModel.email == email
        if user_id:
            condition = condition & (UserModel.id != user_id)
        stmt = select(exists().where(condition))
        result = await self.session.execute(stmt)
        return result.scalar()
