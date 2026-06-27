import pytest

from src.backend.application.user.dtos.delete_user import DeleteUserCommand
from src.backend.application.user.errors import UserNotFoundError
from src.backend.application.user.use_cases.delete_user import DeleteUserUseCase


class TestDeleteUserUseCase:

    async def test_deletes_user_successfully(self, mock_uow, sample_user):
        mock_uow.users.get_by_id.return_value = sample_user
        uc = DeleteUserUseCase(uow=mock_uow)

        await uc.execute(DeleteUserCommand(user_id=sample_user.id))

        mock_uow.users.delete.assert_called_once_with(sample_user)
        mock_uow.commit.assert_called_once()

    async def test_raises_when_user_not_found(self, mock_uow, user_id):
        mock_uow.users.get_by_id.return_value = None
        uc = DeleteUserUseCase(uow=mock_uow)

        with pytest.raises(UserNotFoundError):
            await uc.execute(DeleteUserCommand(user_id=user_id))

    async def test_commit_not_called_when_not_found(self, mock_uow, user_id):
        mock_uow.users.get_by_id.return_value = None
        uc = DeleteUserUseCase(uow=mock_uow)

        with pytest.raises(UserNotFoundError):
            await uc.execute(DeleteUserCommand(user_id=user_id))

        mock_uow.commit.assert_not_called()
