from dataclasses import dataclass


@dataclass
class LoginUserCommand:
    """Команда для авторизации"""
    username: str
    password: str


@dataclass
class LoginUserResult:
    """Результат авторизации"""
    access_token: str
    refresh_token: str
    token_type: str
