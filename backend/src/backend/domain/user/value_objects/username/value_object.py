import re
from dataclasses import dataclass

from src.backend.domain.user.error import InvalidUsernameError


@dataclass(frozen=True)
class Username:
    value: str

    def __post_init__(self):
        if not self._is_valid():
            raise InvalidUsernameError()

    def _is_valid(self) -> bool:
        pattern = r"^[a-zA-Z0-9](?:[a-zA-Z0-9_]{1,28}[a-zA-Z0-9])?$"
        return re.match(pattern, self.value) is not None

    def __str__(self):
        return self.value