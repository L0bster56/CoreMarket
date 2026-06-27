from src.backend.domain.shared.specification import Specification


class PasswordStrengthSpecification(Specification[str]):
    """Пароль должен быть не короче 8 символов"""

    def is_satisfied_by(self, candidate: str) -> bool:
        return len(candidate) >= 8


class PasswordDiffSpecification(Specification[tuple[str, str]]):
    """Новый пароль должен отличаться от старого"""

    def is_satisfied_by(self, candidate: tuple[str, str]) -> bool:
        old_password, new_password = candidate
        return old_password != new_password
