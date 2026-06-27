from src.backend.domain.shared.errors import DomainError


class InvalidNameError(DomainError):
    """Вызывается когда name не соответствует допустимому формату"""