import pytest

from src.backend.application.rating.dtos.delete_rating import DeleteRatingCommand
from src.backend.application.rating.errors import RatingNotFoundError
from src.backend.application.rating.use_cases.delete_rating import DeleteRatingUseCase


class TestDeleteRatingUseCase:

    async def test_deletes_rating_successfully(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = sample_rating
        uc = DeleteRatingUseCase(uow=mock_uow, user=sample_user)

        await uc.execute(DeleteRatingCommand(item_id=item_id))

        mock_uow.ratings.delete.assert_called_once_with(sample_rating)
        mock_uow.commit.assert_called_once()

    async def test_raises_when_rating_not_found(self, mock_uow, sample_user, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = None
        uc = DeleteRatingUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(RatingNotFoundError):
            await uc.execute(DeleteRatingCommand(item_id=item_id))

    async def test_commit_not_called_when_not_found(self, mock_uow, sample_user, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = None
        uc = DeleteRatingUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(RatingNotFoundError):
            await uc.execute(DeleteRatingCommand(item_id=item_id))

        mock_uow.commit.assert_not_called()

    async def test_queries_by_item_and_user(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = sample_rating
        uc = DeleteRatingUseCase(uow=mock_uow, user=sample_user)

        await uc.execute(DeleteRatingCommand(item_id=item_id))

        mock_uow.ratings.get_by_item_and_user.assert_called_once_with(item_id, sample_user.id)
