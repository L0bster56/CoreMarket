import pytest

from src.backend.application.auth.dtos.change_password import ChangePasswordCommand
from src.backend.application.auth.errors import InvalidPasswordError, SamePasswordError, WeakPasswordError
from src.backend.application.auth.specifications import PasswordDiffSpecification, PasswordStrengthSpecification
from src.backend.application.auth.use_cases.change_password import ChangePasswordUseCase


class TestChangePasswordUseCase:

    def _make_uc(self, mock_uow, mock_hasher, sample_user):
        return ChangePasswordUseCase(
            uow=mock_uow,
            hasher=mock_hasher,
            password_spec=PasswordStrengthSpecification(),
            password_diff_spec=PasswordDiffSpecification(),
            user=sample_user,
        )

    async def test_changes_password_successfully(self, mock_uow, mock_hasher, sample_user):
        uc = self._make_uc(mock_uow, mock_hasher, sample_user)

        await uc.execute(ChangePasswordCommand(old_password="OldPass1", new_password="NewPass123"))

        mock_uow.commit.assert_called_once()
        mock_uow.users.update.assert_called_once_with(sample_user)

    async def test_raises_when_new_password_weak(self, mock_uow, mock_hasher, sample_user):
        uc = self._make_uc(mock_uow, mock_hasher, sample_user)

        with pytest.raises(WeakPasswordError):
            await uc.execute(ChangePasswordCommand(old_password="OldPass1", new_password="short"))

    async def test_raises_when_same_password(self, mock_uow, mock_hasher, sample_user):
        uc = self._make_uc(mock_uow, mock_hasher, sample_user)

        with pytest.raises(SamePasswordError):
            await uc.execute(ChangePasswordCommand(old_password="SamePass1", new_password="SamePass1"))

    async def test_raises_when_old_password_wrong(self, mock_uow, mock_hasher, sample_user):
        mock_hasher.verify.return_value = False
        uc = self._make_uc(mock_uow, mock_hasher, sample_user)

        with pytest.raises(InvalidPasswordError):
            await uc.execute(ChangePasswordCommand(old_password="WrongOld", new_password="NewPass123"))

    async def test_commit_not_called_on_weak_password(self, mock_uow, mock_hasher, sample_user):
        uc = self._make_uc(mock_uow, mock_hasher, sample_user)

        with pytest.raises(WeakPasswordError):
            await uc.execute(ChangePasswordCommand(old_password="OldPass1", new_password="123"))

        mock_uow.commit.assert_not_called()

    async def test_hasher_hash_called_with_new_password(self, mock_uow, mock_hasher, sample_user):
        uc = self._make_uc(mock_uow, mock_hasher, sample_user)

        await uc.execute(ChangePasswordCommand(old_password="OldPass1", new_password="NewPass123"))

        mock_hasher.hash.assert_called_once_with("NewPass123")
