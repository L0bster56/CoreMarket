from fastapi import APIRouter, Depends, Request, status
from fastapi_utils.cbv import cbv

from src.backend.application.auth.dtos.login_user import LoginUserCommand
from src.backend.application.auth.dtos.refresh_token import RefreshTokenCommand
from src.backend.application.auth.dtos.change_password import ChangePasswordCommand
from src.backend.application.auth.dtos.update_me import UpdateMeCommand
from src.backend.application.auth.specifications import (
    PasswordDiffSpecification,
    PasswordStrengthSpecification,
)
from src.backend.application.auth.use_cases.change_password import ChangePasswordUseCase
from src.backend.application.auth.use_cases.login_user import LoginUserUseCase
from src.backend.application.auth.use_cases.refresh_token import RefreshTokenUseCase
from src.backend.application.auth.use_cases.update_me import UpdateMeUseCase
from src.backend.application.user.dtos.create_user import CreateUserCommand
from src.backend.application.user.use_cases.create_user import CreateUserUseCase
from src.backend.infrastructure.db.sqlalchemy.core.uow import SqlAlchemyUnitOfWork
from src.backend.infrastructure.security.bcrypt.hasher import BcryptHasher
from src.backend.infrastructure.security.jose.token import JWTTokenService
from src.backend.presentation.api.v1.auth.dependencies import (
    CurrentUserDep,
    get_hasher,
    get_token_service,
)
from src.backend.presentation.api.v1.auth.schemas import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UpdateMeRequest,
    UserResponse,
)
from src.backend.presentation.api.v1.core.dependencies import get_uow
from src.backend.presentation.api.v1.core.limiter import limiter
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema

# Отдельный роутер для rate-limited эндпоинтов.
# @cbv(router) оборачивает ВСЕ маршруты на своём роутере и уничтожает
# slowapi-атрибуты, поэтому login/register живут на изолированном роутере.
auth_rate_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"model": ExceptionSchema}},
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"model": ExceptionSchema}},
)


@auth_rate_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit("5/minute")
async def register(
        request: Request,
        body: RegisterRequest,
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
        hasher: BcryptHasher = Depends(get_hasher),
) -> UserResponse:
    result = await CreateUserUseCase(
        uow=uow,
        hasher=hasher,
        password_spec=PasswordStrengthSpecification(),
    ).execute(
        CreateUserCommand(username=body.username, email=body.email, password=body.password)
    )
    user = await uow.users.get_by_id(result.user_id)

    from src.backend.application.tasks.notifications import send_welcome_email
    send_welcome_email.delay(str(result.user_id))

    return UserResponse.from_entity(user)


@auth_rate_router.post("/login", status_code=status.HTTP_200_OK, response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
        request: Request,
        body: LoginRequest,
        uow: SqlAlchemyUnitOfWork = Depends(get_uow),
        hasher: BcryptHasher = Depends(get_hasher),
        tokens: JWTTokenService = Depends(get_token_service),
) -> TokenResponse:
    result = await LoginUserUseCase(
        uow=uow,
        tokens=tokens,
        hasher=hasher,
    ).execute(LoginUserCommand(username=body.username, password=body.password))
    return TokenResponse.model_validate(result)


@cbv(router)
class AuthRouter:
    uow: SqlAlchemyUnitOfWork = Depends(get_uow)

    @router.post("/refresh", status_code=status.HTTP_200_OK, response_model=TokenResponse)
    async def refresh(
            self,
            body: RefreshRequest,
            tokens: JWTTokenService = Depends(get_token_service),
    ) -> TokenResponse:
        result = await RefreshTokenUseCase(
            uow=self.uow,
            tokens=tokens,
        ).execute(RefreshTokenCommand(refresh_token=body.refresh_token))
        return TokenResponse.model_validate(result)

    @router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
    async def logout(self, _: CurrentUserDep) -> None:
        ...

    @router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
    async def get_me(self, user: CurrentUserDep) -> UserResponse:
        return UserResponse.from_entity(user)

    @router.patch("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
    async def update_me(self, body: UpdateMeRequest, user: CurrentUserDep) -> UserResponse:
        await UpdateMeUseCase(uow=self.uow, user=user).execute(
            UpdateMeCommand(username=body.username, avatar_url=body.avatar_url)
        )
        return UserResponse.from_entity(user)

    @router.patch("/change-password", status_code=status.HTTP_204_NO_CONTENT)
    async def change_password(
            self,
            body: ChangePasswordRequest,
            user: CurrentUserDep,
            hasher: BcryptHasher = Depends(get_hasher),
    ) -> None:
        await ChangePasswordUseCase(
            uow=self.uow,
            hasher=hasher,
            password_spec=PasswordStrengthSpecification(),
            password_diff_spec=PasswordDiffSpecification(),
            user=user,
        ).execute(
            ChangePasswordCommand(
                old_password=body.old_password,
                new_password=body.new_password,
            )
        )
