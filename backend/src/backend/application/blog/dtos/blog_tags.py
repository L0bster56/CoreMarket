from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateBlogTagCommand:
    name: str
    slug: str


@dataclass
class CreateBlogTagResult:
    id: UUID
    name: str
    slug: str


@dataclass
class UpdateBlogTagCommand:
    tag_id: UUID
    name: str | None = None
    slug: str | None = None


@dataclass
class DeleteBlogTagCommand:
    tag_id: UUID


@dataclass
class ListBlogTagsCommand:
    pass


@dataclass
class BlogTagItem:
    id: UUID
    name: str
    slug: str


@dataclass
class ListBlogTagsResult:
    items: list[BlogTagItem]
