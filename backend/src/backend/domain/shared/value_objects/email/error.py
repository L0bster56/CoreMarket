from src.backend.domain.shared.errors import DomainError


class EmailError(DomainError):
    """
    Базовая ошибка VO Email
    """

class InvalidEmailError(EmailError):
    """
    Вызывается когда неправильный формат электронной почты
    """