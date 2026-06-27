from src.backend.domain.shared.specification import Specification, T


class PasswordLengthSpecification(Specification[str]):
    def is_satisfied_by(self, password: str) -> bool:
        """
        Проверяет, что пароль соответствует минимальной длине.

        Attributes:
            password: пароль

        Returns:
            True если пароль соответствует
        """
        return len(password) >= 8


class PasswordUpperLetterSpecification(Specification[str]):
    def is_satisfied_by(self, password: str) -> bool:
        """
        Проверяет, что пароль имеет заглавную букву.

        Attributes:
            password: пароль

        Returns:
            True если пароль соответствует
        """
        return any(c.isupper() for c in password)


class PasswordLowerLetterSpecification(Specification[str]):
    def is_satisfied_by(self, password: str) -> bool:
        """
        Проверяет, что пароль имеет строчную букву.

        Attributes:
            password: пароль

        Returns:
            True если пароль соответствует
        """
        return any(c.islower() for c in password)


class PasswordDigitSpecification(Specification[str]):
    def is_satisfied_by(self, password: str) -> bool:
        """
        Проверяет, что пароль имеет цифру.

        Attributes:
            password: пароль

        Returns:
            True если пароль соответствует
        """
        return any(c.isdigit() for c in password)


class PasswordSpecialCharacterSpecification(Specification[str]):
    SPECIAL = set("!@#$%^&*()-_+=/{}[];:'\"\\|`~?,.")
    def is_satisfied_by(self, password: T) -> bool:
        """
        Проверяет, что пароль имеет спец символ.

        Attributes:
            password: пароль

        Returns:
            True если пароль соответствует
        """
        return any(c in self.SPECIAL for c in password)

class PasswordDifferenceSpecification(Specification[tuple[str, str]]):
    def is_satisfied_by(self, passwords: tuple[str, str]) -> bool:
        """
        Проверяет, разные ли два пароля.

        Attributes:
            passwords: кортеж паролей

        Returns:
            True если пароли разные
        """
        old_password, new_password = passwords
        return old_password != new_password
