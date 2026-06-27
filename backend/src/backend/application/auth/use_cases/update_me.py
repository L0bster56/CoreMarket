from dataclasses import dataclass

from src.backend.application.auth.dtos.update_me import UpdateMeCommand
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.errors import UsernameAlreadyExistsError
from src.backend.domain.user.entity import User


@dataclass
class UpdateMeUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: UpdateMeCommand) -> None:
        async with self.uow:
            if cmd.username is not None:
                if await self.uow.users.exists_username(cmd.username, self.user.id):
                    raise UsernameAlreadyExistsError("username already exists")
                self.user.change_username(cmd.username)

            if cmd.avatar_url is not None:
                self.user.change_avatar_url(cmd.avatar_url)

            await self.uow.users.update(self.user)
            await self.uow.commit()
