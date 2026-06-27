from src.backend.application.shared.errors import ApplicationError, NotAuthorizedError, BadRequestError, ConflictError


class AuthError(ApplicationError):
    """
    Базовая ошибка Auth
    """

class AuthUserNotFoundError(NotAuthorizedError, AuthError):
    pass

class InvalidPasswordError(NotAuthorizedError, AuthError):
    pass

class InActiveUserError(NotAuthorizedError, AuthError):
    pass

class WeakPasswordError(BadRequestError, AuthError):
    pass

class SamePasswordError(BadRequestError, AuthError):
    pass

class EmailAlreadyExistsError(ConflictError, AuthError):
    pass

