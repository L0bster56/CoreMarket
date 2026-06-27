from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetTagCommand:
    tag_id: UUID


@dataclass
class GetTagResult:
    id: UUID
    name: str
    slug: str
