from src.backend.application.shared.errors import ApplicationError, ConflictError, NotFoundError


class UserError(ApplicationError):
    """Базовая ошибка модуля User"""

class UserNotFoundError(NotFoundError, UserError):
    pass

class UsernameAlreadyExistsError(ConflictError, UserError):
    pass