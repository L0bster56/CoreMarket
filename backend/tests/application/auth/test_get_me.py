import pytest

from src.backend.application.auth.dtos.get_me import GetMeCommand
from src.backend.application.auth.errors import InActiveUserError
from src.backend.application.auth.use_cases.get_me import GetMeUseCase
from src.backend.application.user.errors import UserNotFoundError
from src.backend.domain.user.entity import User


class TestGetMeUseCase:

    async def test_returns_user_on_success(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = GetMeUseCase(uow=mock_uow, tokens=mock_tokens)

        result = await uc.execute(GetMeCommand(token="valid_token"))

        assert isinstance(result, User)
        assert result.id == sample_user.id

    async def test_raises_when_user_not_found(self, mock_uow, mock_tokens):
        mock_uow.users.get_by_id.return_value = None
        uc = GetMeUseCase(uow=mock_uow, tokens=mock_tokens)

        with pytest.raises(UserNotFoundError):
            await uc.execute(GetMeCommand(token="valid_token"))

    async def test_raises_when_user_inactive(self, mock_uow, mock_tokens, inactive_user):
        mock_uow.users.get_by_id.return_value = inactive_user
        uc = GetMeUseCase(uow=mock_uow, tokens=mock_tokens)

        with pytest.raises(InActiveUserError):
            await uc.execute(GetMeCommand(token="valid_token"))

    async def test_decodes_access_token(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = GetMeUseCase(uow=mock_uow, tokens=mock_tokens)

        await uc.execute(GetMeCommand(token="my_token"))

        mock_tokens.decode.assert_called_once_with("my_token")

    async def test_commit_not_called(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = GetMeUseCase(uow=mock_uow, tokens=mock_tokens)

        await uc.execute(GetMeCommand(token="token"))

        mock_uow.commit.assert_not_called()
