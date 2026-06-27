from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateTagCommand:
    name: str
    slug: str


@dataclass
class CreateTagResult:
    id: UUID
    name: str
    slug: str
