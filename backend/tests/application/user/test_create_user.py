import pytest

from src.backend.application.auth.errors import EmailAlreadyExistsError, WeakPasswordError
from src.backend.application.auth.specifications import PasswordStrengthSpecification
from src.backend.application.user.dtos.create_user import CreateUserCommand
from src.backend.application.user.errors import UsernameAlreadyExistsError
from src.backend.application.user.use_cases.create_user import CreateUserUseCase
from src.backend.domain.user.entity import UserRole


class TestCreateUserUseCase:

    def _make_uc(self, mock_uow, mock_hasher):
        return CreateUserUseCase(
            uow=mock_uow,
            hasher=mock_hasher,
            password_spec=PasswordStrengthSpecification(),
        )

    async def test_creates_user_successfully(self, mock_uow, mock_hasher, sample_user):
        mock_uow.users.exists_email.return_value = False
        mock_uow.users.exists_username.return_value = False
        mock_uow.users.create.return_value = sample_user
        uc = self._make_uc(mock_uow, mock_hasher)
        cmd = CreateUserCommand(username="testuser", email="test@example.com", password="password123")

        result = await uc.execute(cmd)

        assert result.user_id == sample_user.id

    async def test_raises_when_email_exists(self, mock_uow, mock_hasher):
        mock_uow.users.exists_email.return_value = True
        uc = self._make_uc(mock_uow, mock_hasher)
        cmd = CreateUserCommand(username="testuser", email="taken@example.com", password="password123")

        with pytest.raises(EmailAlreadyExistsError):
            await uc.execute(cmd)

    async def test_raises_when_username_exists(self, mock_uow, mock_hasher):
        mock_uow.users.exists_email.return_value = False
        mock_uow.users.exists_username.return_value = True
        uc = self._make_uc(mock_uow, mock_hasher)
        cmd = CreateUserCommand(username="taken", email="new@example.com", password="password123")

        with pytest.raises(UsernameAlreadyExistsError):
            await uc.execute(cmd)

    async def test_raises_when_password_weak(self, mock_uow, mock_hasher):
        mock_uow.users.exists_email.return_value = False
        mock_uow.users.exists_username.return_value = False
        uc = self._make_uc(mock_uow, mock_hasher)
        cmd = CreateUserCommand(username="testuser", email="test@example.com", password="short")

        with pytest.raises(WeakPasswordError):
            await uc.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_hasher, sample_user):
        mock_uow.users.exists_email.return_value = False
        mock_uow.users.exists_username.return_value = False
        mock_uow.users.create.return_value = sample_user
        uc = self._make_uc(mock_uow, mock_hasher)

        await uc.execute(CreateUserCommand(username="testuser", email="test@example.com", password="password123"))

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_on_email_conflict(self, mock_uow, mock_hasher):
        mock_uow.users.exists_email.return_value = True
        uc = self._make_uc(mock_uow, mock_hasher)

        with pytest.raises(EmailAlreadyExistsError):
            await uc.execute(CreateUserCommand(username="u", email="taken@example.com", password="password123"))

        mock_uow.commit.assert_not_called()

    async def test_default_role_is_user(self, mock_uow, mock_hasher, sample_user):
        mock_uow.users.exists_email.return_value = False
        mock_uow.users.exists_username.return_value = False
        mock_uow.users.create.return_value = sample_user
        uc = self._make_uc(mock_uow, mock_hasher)
        cmd = CreateUserCommand(username="testuser", email="test@example.com", password="password123")

        await uc.execute(cmd)

        created_arg = mock_uow.users.create.call_args[0][0]
        assert created_arg.role == UserRole.user

    async def test_password_is_hashed(self, mock_uow, mock_hasher, sample_user):
        mock_uow.users.exists_email.return_value = False
        mock_uow.users.exists_username.return_value = False
        mock_uow.users.create.return_value = sample_user
        uc = self._make_uc(mock_uow, mock_hasher)

        await uc.execute(CreateUserCommand(username="testuser", email="test@example.com", password="password123"))

        mock_hasher.hash.assert_called_once_with("password123")
