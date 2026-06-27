from dataclasses import dataclass

from src.backend.application.auth.errors import EmailAlreadyExistsError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.dtos.update_user import UpdateUserCommand
from src.backend.application.user.errors import UserNotFoundError


@dataclass
class UpdateUserUseCase:
    """
    UseCase: обновление данных пользователя (Admin).

    Ответственность:
        - Поиск пользователя по id
        - Проверка уникальности email
        - Обновление email и пароля
        - Сохранение изменений в базе данных
    """

    uow: UnitOfWork

    async def execute(self, cmd: UpdateUserCommand) -> None:
        """
        Обновляет данные пользователя.

        Args:
            cmd (UpdateUserCommand): идентификатор и новые данные пользователя

        Raises:
            UserNotFoundError: если пользователь не найден
            EmailAlreadyExistsError: если email уже используется другим пользователем
        """
        async with self.uow:
            user = await self.uow.users.get_by_id(cmd.user_id)

            if user is None:
                raise UserNotFoundError()

            if await self.uow.users.exists_email(cmd.email, user.id):
                raise EmailAlreadyExistsError("email already exists")

            user.change_email(cmd.email)
            user.change_password(cmd.password)

            await self.uow.users.update(user)
            await self.uow.commit()
