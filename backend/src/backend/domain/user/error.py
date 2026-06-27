from src.backend.domain.shared.errors import DomainError


class InvalidUsernameError(DomainError):
    """Вызывается когда username не соответствует допустимому формату"""

class InvalidPasswordError(DomainError):
    """Вызывается когда пароль не соответствует требованиям"""