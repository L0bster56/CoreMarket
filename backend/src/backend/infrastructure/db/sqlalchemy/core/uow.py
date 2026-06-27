from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.infrastructure.db.sqlalchemy.blog.repository import (
    SqlAlchemyBlogPostRepository,
    SqlAlchemyBlogTagRepository,
)
from src.backend.infrastructure.db.sqlalchemy.category.repository import SqlAlchemyCategoryRepository
from src.backend.infrastructure.db.sqlalchemy.comment.repository import SqlAlchemyCommentRepository
from src.backend.infrastructure.db.sqlalchemy.item.repository import (
    SqlAlchemyCharacteristicRepository,
    SqlAlchemyGalleryRepository,
    SqlAlchemyItemRepository,
)
from src.backend.infrastructure.db.sqlalchemy.rating.repository import SqlAlchemyRatingRepository
from src.backend.infrastructure.db.sqlalchemy.tag.repository import SqlAlchemyTagRepository
from src.backend.infrastructure.db.sqlalchemy.user.repository import SqlAlchemyUserRepository


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users = SqlAlchemyUserRepository(session)
        self.categories = SqlAlchemyCategoryRepository(session)
        self.tags = SqlAlchemyTagRepository(session)
        self.comments = SqlAlchemyCommentRepository(session)
        self.items = SqlAlchemyItemRepository(session)
        self.characteristics = SqlAlchemyCharacteristicRepository(session)
        self.gallery = SqlAlchemyGalleryRepository(session)
        self.ratings = SqlAlchemyRatingRepository(session)
        self.blog_posts = SqlAlchemyBlogPostRepository(session)
        self.blog_tags = SqlAlchemyBlogTagRepository(session)
        self.__committed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
            return
        if not self.__committed and self.session.in_transaction():
            await self.rollback()

    async def commit(self) -> None:
        await self.session.commit()
        self.__committed = True

    async def rollback(self) -> None:
        await self.session.rollback()
