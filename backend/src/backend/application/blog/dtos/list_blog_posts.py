from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class ListBlogPostsFilters:
    search: str | None = None
    category_id: UUID | None = None
    tag_slug: str | None = None
    status: str | None = None
    offset: int = 0
    limit: int = 20


@dataclass
class ListBlogPostsCommand:
    filters: ListBlogPostsFilters = field(default_factory=ListBlogPostsFilters)


@dataclass
class BlogPostListEntry:
    id: UUID
    title: str
    slug: str
    short_description: str | None
    cover_image_url: str | None
    category_id: UUID | None
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass
class ListBlogPostsResult:
    items: list[BlogPostListEntry]
    total: int
