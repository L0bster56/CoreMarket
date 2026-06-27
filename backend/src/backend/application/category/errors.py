from src.backend.application.shared.errors import ApplicationError, NotFoundError, ConflictError


class CategoryError(ApplicationError):
    """Базовая ошибка модуля Category"""

class CategoryNotFoundError(NotFoundError, CategoryError):
    pass

class CategorySlugAlreadyExistsError(ConflictError, CategoryError):
    pass
