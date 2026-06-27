import pytest

from src.backend.application.auth.errors import EmailAlreadyExistsError
from src.backend.application.user.dtos.update_user import UpdateUserCommand
from src.backend.application.user.errors import UserNotFoundError
from src.backend.application.user.use_cases.update_user import UpdateUserUseCase


class TestUpdateUserUseCase:

    async def test_updates_user_successfully(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.exists_email.return_value = False
        uc = UpdateUserUseCase(uow=mock_uow)
        cmd = UpdateUserCommand(user_id=sample_user.id, email="new@example.com", password="new_hash")

        await uc.execute(cmd)

        mock_uow.users.update.assert_called_once_with(sample_user)
        mock_uow.commit.assert_called_once()

    async def test_raises_when_user_not_found(self, mock_uow, user_id):
        mock_uow.users.get_by_id.return_value = None
        uc = UpdateUserUseCase(uow=mock_uow)

        with pytest.raises(UserNotFoundError):
            await uc.execute(UpdateUserCommand(user_id=user_id, email="e@e.com", password="hash"))

    async def test_raises_when_email_taken(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.exists_email.return_value = True
        uc = UpdateUserUseCase(uow=mock_uow)

        with pytest.raises(EmailAlreadyExistsError):
            await uc.execute(UpdateUserCommand(user_id=sample_user.id, email="taken@example.com", password="hash"))

    async def test_commit_not_called_on_email_conflict(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.exists_email.return_value = True
        uc = UpdateUserUseCase(uow=mock_uow)

        with pytest.raises(EmailAlreadyExistsError):
            await uc.execute(UpdateUserCommand(user_id=sample_user.id, email="taken@example.com", password="hash"))

        mock_uow.commit.assert_not_called()

    async def test_email_changed_on_user(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        mock_uow.users.exists_email.return_value = False
        uc = UpdateUserUseCase(uow=mock_uow)

        await uc.execute(UpdateUserCommand(user_id=sample_user.id, email="updated@example.com", password="hash"))

        assert str(sample_user.email) == "updated@example.com"
