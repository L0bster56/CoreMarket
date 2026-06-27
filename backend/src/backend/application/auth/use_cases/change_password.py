from dataclasses import dataclass

from src.backend.application.auth.dtos.change_password import ChangePasswordCommand
from src.backend.application.auth.errors import (
    InvalidPasswordError,
    WeakPasswordError,
    SamePasswordError,
)
from src.backend.application.auth.interfaces.security.hasher import Hasher
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.shared.specification import Specification
from src.backend.domain.user.entity import User


@dataclass
class ChangePasswordUseCase:
    uow: UnitOfWork
    hasher: Hasher
    password_spec: Specification[str]
    password_diff_spec: Specification[tuple[str, str]]
    user: User

    async def execute(self, cmd: ChangePasswordCommand) -> None:
        if not self.password_spec.is_satisfied_by(cmd.new_password):
            raise WeakPasswordError("new password is too weak")

        if not self.password_diff_spec.is_satisfied_by((cmd.old_password, cmd.new_password)):
            raise SamePasswordError("new password is the same as old password")

        if not self.hasher.verify(cmd.old_password, self.user.hashed_password):
            raise InvalidPasswordError("invalid password")

        async with self.uow:
            self.user.change_password(self.hasher.hash(cmd.new_password))
            await self.uow.users.update(self.user)
            await self.uow.commit()
