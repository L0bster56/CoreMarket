from dataclasses import dataclass

from src.backend.application.rating.dtos.create_rating import CreateRatingCommand, CreateRatingResult
from src.backend.application.rating.errors import RatingAlreadyExistsError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.rating.entity import Rating
from src.backend.domain.rating.value_objects.score import Score
from src.backend.domain.user.entity import User


@dataclass
class CreateRatingUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: CreateRatingCommand) -> CreateRatingResult:
        async with self.uow:
            existing = await self.uow.ratings.get_by_item_and_user(cmd.item_id, self.user.id)
            if existing is not None:
                raise RatingAlreadyExistsError("user already rated this item")

            rating = Rating.create(
                item_id=cmd.item_id,
                user_id=self.user.id,
                score=Score(cmd.score),
            )
            created = await self.uow.ratings.create(rating)
            await self.uow.commit()

            return CreateRatingResult(
                id=created.id,
                item_id=created.item_id,
                user_id=created.user_id,
                score=created.score.value,
                created_at=created.created_at,
                updated_at=created.updated_at,
            )
