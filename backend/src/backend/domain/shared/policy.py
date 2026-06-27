from abc import ABC, abstractmethod

from src.backend.domain.shared.errors import PermissionDeniedError


class Policy(ABC):
    """
    Базовый класс политики авторизации
    """
    @abstractmethod
    def is_satisfied_by(self) -> bool: ...

    @abstractmethod
    def _error_message(self) -> str: ...

    def enforce(self) -> None:
        """
        Применяет политику.
        Вызывает исключение, если условия не выполняются

        Raises:
            PermissionDeniedError: Если действие запрещено
        """
        if not self.is_satisfied_by():
            raise PermissionDeniedError(self._error_message())

