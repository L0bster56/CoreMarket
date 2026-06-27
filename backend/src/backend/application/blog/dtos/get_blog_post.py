from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class GetBlogPostCommand:
    slug: str


@dataclass
class BlogTagResult:
    id: UUID
    name: str
    slug: str


@dataclass
class BlogProductLinkResult:
    id: UUID
    product_id: UUID
    display_order: int


@dataclass
class BlogCategoryResult:
    id: UUID
    name: str
    slug: str


@dataclass
class GetBlogPostResult:
    id: UUID
    title: str
    slug: str
    short_description: str | None
    content: str | None
    content_html: str | None
    cover_image_url: str | None
    category_id: UUID | None
    category: BlogCategoryResult | None
    status: str
    seo_title: str | None
    seo_description: str | None
    tags: list[BlogTagResult]
    product_links: list[BlogProductLinkResult]
    created_at: datetime
    updated_at: datetime
