import re
from dataclasses import dataclass

from src.backend.domain.shared.value_objects.name.error import InvalidNameError


@dataclass(frozen=True)
class Name:
    value: str

    def __post_init__(self):
        if not self._is_valid():
            raise InvalidNameError()

    def _is_valid(self) -> bool:
        pattern = r"^[A-Za-zА-ЯЁа-яё0-9 \-'\"«»&.,;:()/+%#@!?]{2,200}$"
        return re.match(pattern, self.value) is not None

    def __str__(self):
        return self.value