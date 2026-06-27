from dataclasses import dataclass

from src.backend.domain.rating.error import InvalidScoreError


@dataclass(frozen=True)
class Score:
    value: int

    def __post_init__(self):
        if not self._is_valid():
            raise InvalidScoreError()

    def _is_valid(self) -> bool:
        return 1 <= self.value <= 5

    def __str__(self) -> str:
        return str(self.value)
