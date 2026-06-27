import pytest

from src.backend.application.auth.dtos.refresh_token import RefreshTokenCommand
from src.backend.application.auth.errors import InActiveUserError
from src.backend.application.auth.use_cases.refresh_token import RefreshTokenUseCase


class TestRefreshTokenUseCase:

    async def test_returns_new_tokens_on_success(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = RefreshTokenUseCase(uow=mock_uow, tokens=mock_tokens)

        result = await uc.execute(RefreshTokenCommand(refresh_token="valid_refresh"))

        assert result.access_token == "access_token_value"
        assert result.token_type == "bearer"

    async def test_raises_when_user_inactive(self, mock_uow, mock_tokens, inactive_user):
        mock_uow.users.get_by_id.return_value = inactive_user
        uc = RefreshTokenUseCase(uow=mock_uow, tokens=mock_tokens)

        with pytest.raises(InActiveUserError):
            await uc.execute(RefreshTokenCommand(refresh_token="valid_refresh"))

    async def test_decodes_refresh_token(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = RefreshTokenUseCase(uow=mock_uow, tokens=mock_tokens)

        await uc.execute(RefreshTokenCommand(refresh_token="my_refresh_token"))

        mock_tokens.decode.assert_called_once_with("my_refresh_token", True)

    async def test_encode_called_twice(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = RefreshTokenUseCase(uow=mock_uow, tokens=mock_tokens)

        await uc.execute(RefreshTokenCommand(refresh_token="refresh"))

        assert mock_tokens.encode.call_count == 2

    async def test_commit_not_called(self, mock_uow, mock_tokens, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = RefreshTokenUseCase(uow=mock_uow, tokens=mock_tokens)

        await uc.execute(RefreshTokenCommand(refresh_token="refresh"))

        mock_uow.commit.assert_not_called()
