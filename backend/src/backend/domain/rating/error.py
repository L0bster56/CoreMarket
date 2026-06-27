from src.backend.domain.shared.errors import DomainError


class InvalidScoreError(DomainError):
    """Вызывается когда score выходит за пределы допустимого диапазона (1–5)"""