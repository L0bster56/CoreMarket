from dataclasses import dataclass
from uuid import UUID


@dataclass
class UpdateBlogPostCommand:
    slug: str
    title: str | None = None
    new_slug: str | None = None
    short_description: str | None = None
    content: str | None = None
    cover_image_url: str | None = None
    category_id: UUID | None = None
    seo_title: str | None = None
    seo_description: str | None = None
