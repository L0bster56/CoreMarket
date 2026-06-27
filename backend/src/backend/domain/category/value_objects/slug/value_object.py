import re
from dataclasses import dataclass

from src.backend.domain.category.value_objects.slug.error import InvalidSlugError


@dataclass(frozen=True)
class Slug:
    value: str

    def __post_init__(self):
        if not self._is_valid():
            raise InvalidSlugError()

    def _is_valid(self) -> bool:
        pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
        return re.fullmatch(pattern, self.value) is not None

    def __str__(self) -> str:
        return self.value