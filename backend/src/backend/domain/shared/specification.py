from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

# Будет какой, то определенный тип данных
T = TypeVar("T")


class Specification(ABC, Generic[T]):
    """
    Абстрактный класс спецификации
    """
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Метод, который будет проверять подходит ли он по правилам
        """

    def __and__(self, other: "Specification[T]") -> "AndSpecification[T]":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "OrSpecification[T]":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification[T]":
        return NotSpecification(self)

@dataclass
class AndSpecification(Specification[T]):
    """
    Спецификация, объединяющая две спецификации через And

    Attributes:
        left: Первая спецификация.
        right: Вторая спецификация.
    """
    left: Specification[T]
    right: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Проверяет, удовлетворяет ли объект заданной спецификации.

        Attributes:
            candidate: Проверяемый объект.

        Returns:
            True, если оде исходные спецификации выполняется
        """
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


@dataclass
class OrSpecification(Specification[T]):
    """
    Спецификация, объединяющая две спецификации через Or

    Attributes:
        left: Первая спецификация.
        right: Вторая спецификация.
    """
    left: Specification[T]
    right: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Проверяет, удовлетворяет ли объект заданной спецификации.

        Attributes:
            candidate: Проверяемый объект.

        Returns:
            True, если одна из исходных спецификаций выполняется
        """
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


@dataclass
class NotSpecification(Specification[T]):
    """
    Спецификация, инвертирующая результат другой спецификации.

    Attributes:
        spec (Specification[T]): спецификация.
    """
    spec: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        """
        Проверяет, НЕ удовлетворяет ли объект заданной спецификации.

        Attributes:
            candidate: Проверяемый объект.

        Returns:
            True, если исходная спецификация НЕ выполняется
        """
        return not self.spec.is_satisfied_by(candidate)