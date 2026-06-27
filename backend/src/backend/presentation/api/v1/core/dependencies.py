from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.infrastructure.db.sqlalchemy.core.session import async_session
from src.backend.infrastructure.db.sqlalchemy.core.uow import SqlAlchemyUnitOfWork


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_uow(session: AsyncSession = Depends(get_db)) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session=session)


UoWDep = Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]
