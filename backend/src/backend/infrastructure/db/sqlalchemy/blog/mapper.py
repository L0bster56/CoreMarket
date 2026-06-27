from __future__ import annotations

from src.backend.domain.blog.entity import BlogPost, BlogTag
from src.backend.domain.blog.enums import BlogPostStatus
from src.backend.domain.blog.product_link import BlogProductLink
from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.value_objects.name.value_object import Name
from src.backend.infrastructure.db.sqlalchemy.blog.model import (
    BlogPostModel,
    BlogProductLinkModel,
    BlogTagModel,
)


def blog_tag_to_model(entity: BlogTag) -> BlogTagModel:
    return BlogTagModel(
        id=entity.id,
        name=str(entity.name),
        slug=str(entity.slug),
    )


def blog_tag_to_entity(model: BlogTagModel) -> BlogTag:
    return BlogTag(
        id=model.id,
        name=Name(model.name),
        slug=Slug(model.slug),
    )


def blog_product_link_to_model(entity: BlogProductLink) -> BlogProductLinkModel:
    return BlogProductLinkModel(
        id=entity.id,
        blog_post_id=entity.blog_post_id,
        product_id=entity.product_id,
        display_order=entity.display_order,
    )


def blog_product_link_to_entity(model: BlogProductLinkModel) -> BlogProductLink:
    return BlogProductLink(
        id=model.id,
        blog_post_id=model.blog_post_id,
        product_id=model.product_id,
        display_order=model.display_order,
    )


def blog_post_to_model(entity: BlogPost) -> BlogPostModel:
    return BlogPostModel(
        id=entity.id,
        title=entity.title,
        slug=str(entity.slug),
        short_description=entity.short_description,
        content=entity.content,
        cover_image_url=entity.cover_image_url,
        category_id=entity.category_id,
        status=entity.status.value,
        seo_title=entity.seo_title,
        seo_description=entity.seo_description,
        created_at=entity.created_at,
        updated_at=entity.updated_at,
    )


def blog_post_to_entity(model: BlogPostModel) -> BlogPost:
    return BlogPost(
        id=model.id,
        title=model.title,
        slug=Slug(model.slug),
        short_description=model.short_description,
        content=model.content,
        cover_image_url=model.cover_image_url,
        category_id=model.category_id,
        status=BlogPostStatus(model.status),
        seo_title=model.seo_title,
        seo_description=model.seo_description,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
