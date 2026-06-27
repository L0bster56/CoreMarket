from dataclasses import dataclass

from src.backend.application.rating.dtos.update_rating import UpdateRatingCommand, UpdateRatingResult
from src.backend.application.rating.errors import RatingNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User


@dataclass
class UpdateRatingUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: UpdateRatingCommand) -> UpdateRatingResult:
        async with self.uow:
            rating = await self.uow.ratings.get_by_item_and_user(cmd.item_id, self.user.id)
            if rating is None:
                raise RatingNotFoundError("rating not found")

            rating.change_score(cmd.score)
            await self.uow.ratings.update(rating)
            await self.uow.commit()

            return UpdateRatingResult(
                id=rating.id,
                item_id=rating.item_id,
                user_id=rating.user_id,
                score=rating.score.value,
                created_at=rating.created_at,
                updated_at=rating.updated_at,
            )
