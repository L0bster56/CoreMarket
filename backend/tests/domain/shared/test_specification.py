from dataclasses import dataclass

import pytest

from src.backend.domain.shared.specification import (
    AndSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
)


class IsPositive(Specification[int]):
    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate > 0


class IsEven(Specification[int]):
    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate % 2 == 0


class IsGreaterThan(Specification[int]):
    def __init__(self, threshold: int):
        self.threshold = threshold

    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate > self.threshold


class TestAndSpecification:
    def test_both_true_returns_true(self):
        spec = AndSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(4) is True

    def test_left_false_returns_false(self):
        spec = AndSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(-2) is False

    def test_right_false_returns_false(self):
        spec = AndSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(3) is False

    def test_both_false_returns_false(self):
        spec = AndSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(-3) is False


class TestOrSpecification:
    def test_both_true_returns_true(self):
        spec = OrSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(4) is True

    def test_left_true_returns_true(self):
        spec = OrSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(3) is True

    def test_right_true_returns_true(self):
        spec = OrSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(-2) is True

    def test_both_false_returns_false(self):
        spec = OrSpecification(IsPositive(), IsEven())
        assert spec.is_satisfied_by(-3) is False


class TestNotSpecification:
    def test_inverts_true_to_false(self):
        spec = NotSpecification(IsPositive())
        assert spec.is_satisfied_by(5) is False

    def test_inverts_false_to_true(self):
        spec = NotSpecification(IsPositive())
        assert spec.is_satisfied_by(-5) is True


class TestSpecificationOperators:
    def test_and_operator_creates_and_specification(self):
        combined = IsPositive() & IsEven()
        assert isinstance(combined, AndSpecification)

    def test_or_operator_creates_or_specification(self):
        combined = IsPositive() | IsEven()
        assert isinstance(combined, OrSpecification)

    def test_invert_operator_creates_not_specification(self):
        inverted = ~IsPositive()
        assert isinstance(inverted, NotSpecification)

    def test_and_operator_evaluates_correctly(self):
        spec = IsPositive() & IsEven()
        assert spec.is_satisfied_by(4) is True
        assert spec.is_satisfied_by(3) is False

    def test_or_operator_evaluates_correctly(self):
        spec = IsPositive() | IsEven()
        assert spec.is_satisfied_by(3) is True
        assert spec.is_satisfied_by(-3) is False

    def test_invert_operator_evaluates_correctly(self):
        spec = ~IsPositive()
        assert spec.is_satisfied_by(-1) is True
        assert spec.is_satisfied_by(1) is False

    def test_complex_chain(self):
        # positive AND even AND > 10
        spec = IsPositive() & IsEven() & IsGreaterThan(10)
        assert spec.is_satisfied_by(12) is True
        assert spec.is_satisfied_by(8) is False
        assert spec.is_satisfied_by(11) is False

    def test_not_of_and(self):
        spec = ~(IsPositive() & IsEven())
        assert spec.is_satisfied_by(3) is True   # positive but odd → AND is False → NOT is True
        assert spec.is_satisfied_by(4) is False   # positive and even → AND is True → NOT is False
