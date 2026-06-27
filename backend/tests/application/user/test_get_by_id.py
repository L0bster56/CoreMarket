import pytest

from src.backend.application.user.dtos.get_by_id import GetByIdCommand
from src.backend.application.user.errors import UserNotFoundError
from src.backend.application.user.use_cases.get_by_id import GetByIdUseCase
from src.backend.domain.user.entity import User


class TestGetByIdUseCase:

    async def test_returns_user_on_success(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = GetByIdUseCase(uow=mock_uow)

        result = await uc.execute(GetByIdCommand(user_id=sample_user.id))

        assert isinstance(result, User)
        assert result.id == sample_user.id

    async def test_raises_when_not_found(self, mock_uow, user_id):
        mock_uow.users.get_by_id.return_value = None
        uc = GetByIdUseCase(uow=mock_uow)

        with pytest.raises(UserNotFoundError):
            await uc.execute(GetByIdCommand(user_id=user_id))

    async def test_commit_not_called(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = GetByIdUseCase(uow=mock_uow)

        await uc.execute(GetByIdCommand(user_id=sample_user.id))

        mock_uow.commit.assert_not_called()
