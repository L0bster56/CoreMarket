from src.backend.application.rating.dtos.get_rating import GetRatingCommand
from src.backend.application.rating.use_cases.get_rating import GetRatingUseCase


class TestGetRatingUseCase:

    async def test_returns_avg_and_count(self, mock_uow, item_id):
        mock_uow.ratings.get_avg_by_item.return_value = 4.5
        mock_uow.ratings.count_by_item.return_value = 10
        uc = GetRatingUseCase(uow=mock_uow)

        result = await uc.execute(GetRatingCommand(item_id=item_id))

        assert result.avg_score == 4.5
        assert result.count == 10
        assert result.item_id == item_id

    async def test_returns_none_avg_when_no_ratings(self, mock_uow, item_id):
        mock_uow.ratings.get_avg_by_item.return_value = None
        mock_uow.ratings.count_by_item.return_value = 0
        uc = GetRatingUseCase(uow=mock_uow)

        result = await uc.execute(GetRatingCommand(item_id=item_id))

        assert result.avg_score is None
        assert result.count == 0

    async def test_commit_not_called(self, mock_uow, item_id):
        mock_uow.ratings.get_avg_by_item.return_value = 3.0
        mock_uow.ratings.count_by_item.return_value = 2
        uc = GetRatingUseCase(uow=mock_uow)

        await uc.execute(GetRatingCommand(item_id=item_id))

        mock_uow.commit.assert_not_called()

    async def test_queries_correct_item(self, mock_uow, item_id):
        mock_uow.ratings.get_avg_by_item.return_value = None
        mock_uow.ratings.count_by_item.return_value = 0
        uc = GetRatingUseCase(uow=mock_uow)

        await uc.execute(GetRatingCommand(item_id=item_id))

        mock_uow.ratings.get_avg_by_item.assert_called_once_with(item_id)
        mock_uow.ratings.count_by_item.assert_called_once_with(item_id)
