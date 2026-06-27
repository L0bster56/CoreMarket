class ApplicationError(Exception):
    """
    Базовая ошибка слоя Application
    """

class BadRequestError(ApplicationError):
    pass

class NotAuthorizedError(ApplicationError):
    pass

class ConflictError(ApplicationError):
    pass

class NotFoundError(ApplicationError):
    pass