from src.backend.application.shared.errors import ApplicationError, NotFoundError, ConflictError, NotAuthorizedError, BadRequestError


class ItemError(ApplicationError):
    """Базовая ошибка модуля Item"""

class ItemEditForbiddenError(NotAuthorizedError, ItemError):
    pass

class ItemNotFoundError(NotFoundError, ItemError):
    pass

class ItemTagNotFoundError(NotFoundError, ItemError):
    pass

class ItemTagAlreadyAttachedError(ConflictError, ItemError):
    pass

class CharacteristicNotFoundError(NotFoundError, ItemError):
    pass

class GalleryImageNotFoundError(NotFoundError, ItemError):
    pass

class InvalidViewCountError(BadRequestError, ItemError):
    pass
