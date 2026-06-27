from src.backend.application.shared.errors import ApplicationError, NotFoundError, NotAuthorizedError


class CommentError(ApplicationError):
    """Базовая ошибка модуля Comment"""

class CommentNotFoundError(NotFoundError, CommentError):
    pass

class CommentEditForbiddenError(NotAuthorizedError, CommentError):
    pass
