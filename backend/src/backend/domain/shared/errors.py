class DomainError(Exception):
    """
    Базовая ошибка domain слоя
    """

class PermissionDeniedError(DomainError):
    """
    Вызывается когда доступ запрещен
    """