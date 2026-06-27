from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.backend.application.blog.dtos.get_blog_post import GetBlogPostResult


class BlogTagSchema(BaseModel):
    id: UUID
    name: str
    slug: str


class BlogCategorySchema(BaseModel):
    id: UUID
    name: str
    slug: str


class BlogProductLinkSchema(BaseModel):
    id: UUID
    product_id: UUID
    display_order: int


class BlogPostListEntry(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: str | None
    cover_image_url: str | None
    category_id: UUID | None
    status: str
    created_at: datetime
    updated_at: datetime


class BlogPostListResponse(BaseModel):
    items: list[BlogPostListEntry]
    total: int


class BlogPostResponse(BaseModel):
    id: UUID
    title: str
    slug: str
    short_description: str | None
    content: str | None
    content_html: str | None
    cover_image_url: str | None
    category_id: UUID | None
    category: BlogCategorySchema | None
    status: str
    seo_title: str | None
    seo_description: str | None
    tags: list[BlogTagSchema]
    product_links: list[BlogProductLinkSchema]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_result(cls, r: GetBlogPostResult) -> "BlogPostResponse":
        return cls(
            id=r.id,
            title=r.title,
            slug=r.slug,
            short_description=r.short_description,
            content=r.content,
            content_html=r.content_html,
            cover_image_url=r.cover_image_url,
            category_id=r.category_id,
            category=BlogCategorySchema(
                id=r.category.id,
                name=r.category.name,
                slug=r.category.slug,
            ) if r.category else None,
            status=r.status,
            seo_title=r.seo_title,
            seo_description=r.seo_description,
            tags=[BlogTagSchema(id=t.id, name=t.name, slug=t.slug) for t in r.tags],
            product_links=[
                BlogProductLinkSchema(id=l.id, product_id=l.product_id, display_order=l.display_order)
                for l in r.product_links
            ],
            created_at=r.created_at,
            updated_at=r.updated_at,
        )


class CreateBlogPostRequest(BaseModel):
    title: str
    slug: str
    short_description: str | None = None


class UpdateBlogPostRequest(BaseModel):
    title: str | None = None
    new_slug: str | None = None
    short_description: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    category_id: UUID | None = None
    seo_title: str | None = None
    seo_description: str | None = None


class AddTagRequest(BaseModel):
    tag_id: UUID


class LinkProductRequest(BaseModel):
    product_id: UUID
    display_order: int = 0


class CreateBlogTagRequest(BaseModel):
    name: str
    slug: str


class UpdateBlogTagRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
