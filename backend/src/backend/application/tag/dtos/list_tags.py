from dataclasses import dataclass
from uuid import UUID


@dataclass
class ListTagsCommand:
    pass


@dataclass
class TagSummary:
    id: UUID
    name: str
    slug: str


@dataclass
class ListTagsResult:
    items: list[TagSummary]
