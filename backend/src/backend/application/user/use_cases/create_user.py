from dataclasses import dataclass

from src.backend.application.auth.errors import EmailAlreadyExistsError, WeakPasswordError
from src.backend.application.auth.interfaces.security.hasher import Hasher
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.application.user.dtos.create_user import CreateUserCommand, CreateUserResult
from src.backend.application.user.errors import UsernameAlreadyExistsError
from src.backend.domain.shared.specification import Specification
from src.backend.domain.user.entity import User


@dataclass
class CreateUserUseCase:
    """
    UseCase: создание нового пользователя.

    Ответственность:
        - Проверка уникальности email и username
        - Проверка сложности пароля
        - Хэширование пароля
        - Создание и сохранение пользователя
    """

    uow: UnitOfWork
    hasher: Hasher
    password_spec: Specification[str]

    async def execute(self, cmd: CreateUserCommand) -> CreateUserResult:
        """
        Создаёт нового пользователя.

        Args:
            cmd (CreateUserCommand): данные нового пользователя

        Returns:
            CreateUserResult: идентификатор созданного пользователя

        Raises:
            EmailAlreadyExistsError: если email уже используется
            UsernameAlreadyExistsError: если username уже используется
            WeakPasswordError: если пароль слишком слабый
        """
        async with self.uow:
            if await self.uow.users.exists_email(cmd.email):
                raise EmailAlreadyExistsError("email already exists")

            if await self.uow.users.exists_username(cmd.username):
                raise UsernameAlreadyExistsError("username already exists")

            if not self.password_spec.is_satisfied_by(cmd.password):
                raise WeakPasswordError("password is too weak")

            user = User.create(
                email=cmd.email,
                username=cmd.username,
                hashed_password=self.hasher.hash(cmd.password),
                role=cmd.role,
            )

            created = await self.uow.users.create(user)
            await self.uow.commit()

            return CreateUserResult(user_id=created.id)
