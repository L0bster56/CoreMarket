from src.backend.application.shared.errors import ApplicationError, NotFoundError, ConflictError


class TagError(ApplicationError):
    """Базовая ошибка модуля Tag"""

class TagNotFoundError(NotFoundError, TagError):
    pass

class TagSlugAlreadyExistsError(ConflictError, TagError):
    pass
