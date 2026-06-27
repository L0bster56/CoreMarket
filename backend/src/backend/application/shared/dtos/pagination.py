from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class PageRequest:
    limit: int = 20
    offset: int = 0


@dataclass
class PaginatedResponse(Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
