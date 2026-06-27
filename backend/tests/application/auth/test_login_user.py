import pytest

from src.backend.application.auth.dtos.login_user import LoginUserCommand
from src.backend.application.auth.errors import AuthUserNotFoundError, InActiveUserError, InvalidPasswordError
from src.backend.application.auth.use_cases.login_user import LoginUserUseCase


class TestLoginUserUseCase:

    async def test_returns_tokens_on_success(self, mock_uow, mock_hasher, mock_tokens, sample_user):
        mock_uow.users.get_by_username.return_value = sample_user
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        result = await uc.execute(LoginUserCommand(username="testuser", password="password123"))

        assert result.access_token == "access_token_value"
        assert result.refresh_token == "access_token_value"
        assert result.token_type == "bearer"

    async def test_raises_when_user_not_found(self, mock_uow, mock_hasher, mock_tokens):
        mock_uow.users.get_by_username.return_value = None
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        with pytest.raises(AuthUserNotFoundError):
            await uc.execute(LoginUserCommand(username="unknown", password="pass"))

    async def test_raises_when_password_wrong(self, mock_uow, mock_hasher, mock_tokens, sample_user):
        mock_uow.users.get_by_username.return_value = sample_user
        mock_hasher.verify.return_value = False
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        with pytest.raises(InvalidPasswordError):
            await uc.execute(LoginUserCommand(username="testuser", password="wrong"))

    async def test_raises_when_user_inactive(self, mock_uow, mock_hasher, mock_tokens, inactive_user):
        mock_uow.users.get_by_username.return_value = inactive_user
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        with pytest.raises(InActiveUserError):
            await uc.execute(LoginUserCommand(username="inactive", password="password"))

    async def test_commit_called_on_success(self, mock_uow, mock_hasher, mock_tokens, sample_user):
        mock_uow.users.get_by_username.return_value = sample_user
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        await uc.execute(LoginUserCommand(username="testuser", password="password"))

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_user_not_found(self, mock_uow, mock_hasher, mock_tokens):
        mock_uow.users.get_by_username.return_value = None
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        with pytest.raises(AuthUserNotFoundError):
            await uc.execute(LoginUserCommand(username="unknown", password="pass"))

        mock_uow.commit.assert_not_called()

    async def test_encode_called_twice_for_access_and_refresh(self, mock_uow, mock_hasher, mock_tokens, sample_user):
        mock_uow.users.get_by_username.return_value = sample_user
        uc = LoginUserUseCase(uow=mock_uow, tokens=mock_tokens, hasher=mock_hasher)

        await uc.execute(LoginUserCommand(username="testuser", password="password"))

        assert mock_tokens.encode.call_count == 2
