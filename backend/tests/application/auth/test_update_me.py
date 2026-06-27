import pytest

from src.backend.application.auth.dtos.update_me import UpdateMeCommand
from src.backend.application.auth.use_cases.update_me import UpdateMeUseCase
from src.backend.application.user.errors import UsernameAlreadyExistsError


class TestUpdateMeUseCase:

    async def test_updates_username_successfully(self, mock_uow, sample_user):
        mock_uow.users.exists_username.return_value = False
        uc = UpdateMeUseCase(uow=mock_uow, user=sample_user)

        await uc.execute(UpdateMeCommand(username="newname"))

        assert str(sample_user.username) == "newname"
        mock_uow.commit.assert_called_once()

    async def test_updates_avatar_url_successfully(self, mock_uow, sample_user):
        uc = UpdateMeUseCase(uow=mock_uow, user=sample_user)

        await uc.execute(UpdateMeCommand(avatar_url="/media/users/avatar.jpg"))

        assert sample_user.avatar_url == "/media/users/avatar.jpg"
        mock_uow.commit.assert_called_once()

    async def test_raises_when_username_taken(self, mock_uow, sample_user):
        mock_uow.users.exists_username.return_value = True
        uc = UpdateMeUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(UsernameAlreadyExistsError):
            await uc.execute(UpdateMeCommand(username="taken_name"))

    async def test_commit_not_called_on_username_conflict(self, mock_uow, sample_user):
        mock_uow.users.exists_username.return_value = True
        uc = UpdateMeUseCase(uow=mock_uow, user=sample_user)

        with pytest.raises(UsernameAlreadyExistsError):
            await uc.execute(UpdateMeCommand(username="taken_name"))

        mock_uow.commit.assert_not_called()

    async def test_no_change_when_command_empty(self, mock_uow, sample_user):
        original_username = str(sample_user.username)
        uc = UpdateMeUseCase(uow=mock_uow, user=sample_user)

        await uc.execute(UpdateMeCommand())

        assert str(sample_user.username) == original_username
        mock_uow.commit.assert_called_once()

    async def test_update_called_on_repo(self, mock_uow, sample_user):
        mock_uow.users.exists_username.return_value = False
        uc = UpdateMeUseCase(uow=mock_uow, user=sample_user)

        await uc.execute(UpdateMeCommand(username="newname"))

        mock_uow.users.update.assert_called_once_with(sample_user)
