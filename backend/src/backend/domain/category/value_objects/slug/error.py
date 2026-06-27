from src.backend.domain.shared.errors import DomainError


class InvalidSlugError(DomainError):
    """Вызывается когда неправильный формат slug"""