from dataclasses import dataclass

from src.backend.application.rating.dtos.delete_rating import DeleteRatingCommand
from src.backend.application.rating.errors import RatingNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User


@dataclass
class DeleteRatingUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: DeleteRatingCommand) -> None:
        async with self.uow:
            rating = await self.uow.ratings.get_by_item_and_user(cmd.item_id, self.user.id)
            if rating is None:
                raise RatingNotFoundError("rating not found")

            await self.uow.ratings.delete(rating)
            await self.uow.commit()
