import pytest

from src.backend.application.rating.dtos.update_rating import UpdateRatingCommand
from src.backend.application.rating.errors import RatingNotFoundError
from src.backend.application.rating.use_cases.update_rating import UpdateRatingUseCase


class TestUpdateRatingUseCase:

    async def test_updates_rating_successfully(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = sample_rating
        uc = UpdateRatingUseCase(uow=mock_uow, user=sample_user)

        result = await uc.execute(UpdateRatingCommand(item_id=item_id, score=5))

        assert result.score == 5
        mock_uow.ratings.update.assert_called_once_with(sample_rating)
        mock_uow.commit.assert_called_once()

    async def test_raises_when_rating_not_found(self, mock_uow, sample_user, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = None
        uc = UpdateRatingUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(RatingNotFoundError):
            await uc.execute(UpdateRatingCommand(item_id=item_id, score=3))

    async def test_commit_not_called_when_not_found(self, mock_uow, sample_user, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = None
        uc = UpdateRatingUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(RatingNotFoundError):
            await uc.execute(UpdateRatingCommand(item_id=item_id, score=3))

        mock_uow.commit.assert_not_called()

    async def test_result_has_correct_fields(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = sample_rating
        uc = UpdateRatingUseCase(uow=mock_uow, user=sample_user)

        result = await uc.execute(UpdateRatingCommand(item_id=item_id, score=2))

        assert result.id == sample_rating.id
        assert result.item_id == sample_rating.item_id
        assert result.user_id == sample_rating.user_id
