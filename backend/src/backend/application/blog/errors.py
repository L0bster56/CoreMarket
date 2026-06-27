from src.backend.application.shared.errors import ApplicationError, ConflictError, NotFoundError


class BlogError(ApplicationError):
    """Базовая ошибка модуля Blog"""


class BlogPostNotFoundError(NotFoundError, BlogError):
    pass


class BlogTagNotFoundError(NotFoundError, BlogError):
    pass


class BlogSlugAlreadyExistsError(ConflictError, BlogError):
    pass
