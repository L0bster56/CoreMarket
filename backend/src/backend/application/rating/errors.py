from src.backend.application.shared.errors import ApplicationError, NotFoundError, ConflictError


class RatingError(ApplicationError):
    """Базовая ошибка модуля Rating"""

class RatingNotFoundError(NotFoundError, RatingError):
    pass

class RatingAlreadyExistsError(ConflictError, RatingError):
    pass
