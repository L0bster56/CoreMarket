from uuid import UUID

from sqlalchemy import select, delete, func

from src.backend.application.rating.repository import RatingRepository
from src.backend.domain.rating.entity import Rating
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository
from src.backend.infrastructure.db.sqlalchemy.rating.mapper import to_entity, to_model
from src.backend.infrastructure.db.sqlalchemy.rating.model import RatingModel


class SqlAlchemyRatingRepository(SqlAlchemyRepository, RatingRepository):

    async def get_by_item_and_user(self, item_id: UUID, user_id: UUID) -> Rating | None:
        stmt = select(RatingModel).where(
            RatingModel.item_id == item_id,
            RatingModel.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def get_avg_by_item(self, item_id: UUID) -> float | None:
        stmt = select(func.avg(RatingModel.score)).where(RatingModel.item_id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def count_by_item(self, item_id: UUID) -> int:
        stmt = select(func.count(RatingModel.id)).where(RatingModel.item_id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(self, rating: Rating) -> Rating:
        model = to_model(rating)
        self.session.add(model)
        await self.session.flush()
        return to_entity(model)

    async def update(self, rating: Rating) -> None:
        model = to_model(rating)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, rating: Rating) -> None:
        stmt = delete(RatingModel).where(RatingModel.id == rating.id)
        await self.session.execute(stmt)
        await self.session.flush()
