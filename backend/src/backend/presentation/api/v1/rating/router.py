from uuid import UUID

from fastapi import APIRouter, status

from src.backend.application.rating.dtos.create_rating import CreateRatingCommand
from src.backend.application.rating.dtos.delete_rating import DeleteRatingCommand
from src.backend.application.rating.dtos.get_rating import GetRatingCommand
from src.backend.application.rating.dtos.update_rating import UpdateRatingCommand
from src.backend.presentation.api.v1.auth.dependencies import CurrentUserDep
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.rating.dependencies import (
    CreateRatingDep,
    DeleteRatingDep,
    GetRatingDep,
    OptionalUserDep,
    RatingRepoDep,
    UpdateRatingDep,
)
from src.backend.presentation.api.v1.rating.schemas import (
    CreateRatingRequest,
    RatingResponse,
    UpdateRatingRequest,
)

router = APIRouter(
    prefix="/items/{item_id}/rating",
    tags=["rating"],
    responses={
        401: {"model": ExceptionSchema},
    },
)


@router.get("", status_code=status.HTTP_200_OK, response_model=RatingResponse)
async def get_rating(
    item_id: UUID,
    uc: GetRatingDep,
    optional_user: OptionalUserDep,
    rating_repo: RatingRepoDep,
) -> RatingResponse:
    result = await uc.execute(GetRatingCommand(item_id=item_id))
    user_score = None
    if optional_user is not None:
        rating = await rating_repo.get_by_item_and_user(item_id, optional_user.id)
        user_score = rating.score.value if rating else None
    return RatingResponse(average=result.avg_score, count=result.count, user_score=user_score)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=RatingResponse)
async def create_rating(
    item_id: UUID,
    body: CreateRatingRequest,
    uc: CreateRatingDep,
    rating_repo: RatingRepoDep,
) -> RatingResponse:
    await uc.execute(CreateRatingCommand(item_id=item_id, score=body.score))
    avg = await rating_repo.get_avg_by_item(item_id)
    count = await rating_repo.count_by_item(item_id)

    from src.backend.application.tasks.ratings import recalculate_item_rating
    recalculate_item_rating.delay(str(item_id))

    return RatingResponse(average=avg, count=count, user_score=body.score)


@router.patch("", status_code=status.HTTP_204_NO_CONTENT)
async def update_rating(
    item_id: UUID,
    body: UpdateRatingRequest,
    uc: UpdateRatingDep,
) -> None:
    await uc.execute(UpdateRatingCommand(item_id=item_id, score=body.score))


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rating(item_id: UUID, uc: DeleteRatingDep) -> None:
    await uc.execute(DeleteRatingCommand(item_id=item_id))
