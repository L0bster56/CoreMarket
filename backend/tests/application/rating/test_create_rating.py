import pytest

from src.backend.application.rating.dtos.create_rating import CreateRatingCommand
from src.backend.application.rating.errors import RatingAlreadyExistsError
from src.backend.application.rating.use_cases.create_rating import CreateRatingUseCase


class TestCreateRatingUseCase:

    async def test_creates_rating_successfully(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = None
        mock_uow.ratings.create.return_value = sample_rating
        uc = CreateRatingUseCase(uow=mock_uow, user=sample_user)

        result = await uc.execute(CreateRatingCommand(item_id=item_id, score=4))

        assert result.id == sample_rating.id
        assert result.score == sample_rating.score.value
        mock_uow.commit.assert_called_once()

    async def test_raises_when_rating_already_exists(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = sample_rating
        uc = CreateRatingUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(RatingAlreadyExistsError):
            await uc.execute(CreateRatingCommand(item_id=item_id, score=4))

    async def test_commit_not_called_on_conflict(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = sample_rating
        uc = CreateRatingUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(RatingAlreadyExistsError):
            await uc.execute(CreateRatingCommand(item_id=item_id, score=4))

        mock_uow.commit.assert_not_called()

    async def test_result_has_correct_fields(self, mock_uow, sample_user, sample_rating, item_id):
        mock_uow.ratings.get_by_item_and_user.return_value = None
        mock_uow.ratings.create.return_value = sample_rating
        uc = CreateRatingUseCase(uow=mock_uow, user=sample_user)

        result = await uc.execute(CreateRatingCommand(item_id=item_id, score=4))

        assert result.item_id == sample_rating.item_id
        assert result.user_id == sample_rating.user_id
