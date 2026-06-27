from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.blog.enums import BlogPostStatus
from src.backend.domain.blog.errors import (
    BlogPostAlreadyPublishedError,
    BlogPostNoCategoryError,
    BlogPostNoContentError,
)
from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.mixins import TimeActionMixin
from src.backend.domain.shared.value_objects.name.value_object import Name


@dataclass(eq=False)
class BlogTag(BaseEntity):
    name: Name
    slug: Slug

    @classmethod
    def create(cls, name: str, slug: str) -> "BlogTag":
        return cls(name=Name(name), slug=Slug(slug))

    def change_name(self, name: str) -> None:
        self.name = Name(name)


@dataclass(eq=False)
class BlogPost(BaseEntity, TimeActionMixin):
    title: str
    slug: Slug
    short_description: str | None
    content: str | None
    cover_image_url: str | None
    category_id: UUID | None
    status: BlogPostStatus
    seo_title: str | None
    seo_description: str | None

    @classmethod
    def create(
        cls,
        title: str,
        slug: str,
        short_description: str | None = None,
    ) -> "BlogPost":
        return cls(
            title=title,
            slug=Slug(slug),
            short_description=short_description,
            content=None,
            cover_image_url=None,
            category_id=None,
            status=BlogPostStatus.draft,
            seo_title=None,
            seo_description=None,
        )

    def change_title(self, title: str) -> None:
        self.title = title
        self.touch()

    def change_slug(self, slug: str) -> None:
        self.slug = Slug(slug)
        self.touch()

    def set_content(self, content: str) -> None:
        self.content = content
        self.touch()

    def set_cover_image(self, url: str) -> None:
        self.cover_image_url = url
        self.touch()

    def set_category(self, category_id: UUID | None) -> None:
        self.category_id = category_id
        self.touch()

    def set_seo(self, seo_title: str | None, seo_description: str | None) -> None:
        self.seo_title = seo_title
        self.seo_description = seo_description
        self.touch()

    def publish(self) -> None:
        if not self.category_id:
            raise BlogPostNoCategoryError()
        if not self.content:
            raise BlogPostNoContentError()
        if self.status == BlogPostStatus.published:
            raise BlogPostAlreadyPublishedError()
        self.status = BlogPostStatus.published
        self.touch()

    def unpublish(self) -> None:
        self.status = BlogPostStatus.draft
        self.touch()

    def archive(self) -> None:
        self.status = BlogPostStatus.archived
        self.touch()
