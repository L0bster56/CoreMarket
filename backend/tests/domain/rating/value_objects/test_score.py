import pytest

from src.backend.domain.rating.error import InvalidScoreError
from src.backend.domain.rating.value_objects.score import Score


class TestScoreValid:
    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5])
    def test_valid_score_created(self, value):
        score = Score(value)
        assert score.value == value

    def test_score_is_frozen(self):
        score = Score(3)
        with pytest.raises((AttributeError, TypeError)):
            score.value = 4  # type: ignore[misc]

    def test_equal_scores(self):
        assert Score(3) == Score(3)

    def test_different_scores_not_equal(self):
        assert Score(3) != Score(4)


class TestScoreInvalid:
    @pytest.mark.parametrize("value", [-1, -100])
    def test_negative_score_raises(self, value):
        with pytest.raises(InvalidScoreError):
            Score(value)

    @pytest.mark.parametrize("value", [7, 10, 100])
    def test_too_large_score_raises(self, value):
        with pytest.raises(InvalidScoreError):
            Score(value)

    def test_invalid_score_is_domain_error(self):
        from src.backend.domain.shared.errors import DomainError
        with pytest.raises(DomainError):
            Score(-1)

    def test_zero_score_is_invalid(self):
        with pytest.raises(InvalidScoreError):
            Score(0)

    def test_six_score_is_invalid(self):
        with pytest.raises(InvalidScoreError):
            Score(6)
