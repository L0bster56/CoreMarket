from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete, func, or_, select

from src.backend.application.blog.dtos.list_blog_posts import ListBlogPostsFilters
from src.backend.domain.blog.entity import BlogPost, BlogTag
from src.backend.domain.blog.product_link import BlogProductLink
from src.backend.infrastructure.db.sqlalchemy.blog.mapper import (
    blog_post_to_entity,
    blog_post_to_model,
    blog_product_link_to_entity,
    blog_product_link_to_model,
    blog_tag_to_entity,
    blog_tag_to_model,
)
from src.backend.infrastructure.db.sqlalchemy.blog.model import (
    BlogPostModel,
    BlogProductLinkModel,
    BlogTagModel,
    blog_post_tags,
)
from src.backend.infrastructure.db.sqlalchemy.core.repository import SqlAlchemyRepository


class SqlAlchemyBlogPostRepository(SqlAlchemyRepository):

    def _apply_filters(self, stmt, filters: ListBlogPostsFilters):
        if filters.search:
            stmt = stmt.where(or_(
                BlogPostModel.title.ilike(f'%{filters.search}%'),
                BlogPostModel.short_description.ilike(f'%{filters.search}%'),
            ))
        if filters.category_id:
            stmt = stmt.where(BlogPostModel.category_id == filters.category_id)
        if filters.tag_slug:
            stmt = (
                stmt
                .join(blog_post_tags, BlogPostModel.id == blog_post_tags.c.blog_post_id)
                .join(BlogTagModel, BlogTagModel.id == blog_post_tags.c.blog_tag_id)
                .where(BlogTagModel.slug == filters.tag_slug)
            )
        if filters.status:
            stmt = stmt.where(BlogPostModel.status == filters.status)
        return stmt

    async def get_by_id(self, post_id: UUID) -> BlogPost | None:
        stmt = select(BlogPostModel).where(BlogPostModel.id == post_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return blog_post_to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> BlogPost | None:
        stmt = select(BlogPostModel).where(BlogPostModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return blog_post_to_entity(model) if model else None

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(BlogPostModel.id).where(BlogPostModel.slug == slug)
        if exclude_id:
            stmt = stmt.where(BlogPostModel.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list(self, filters: ListBlogPostsFilters) -> list[BlogPost]:
        stmt = select(BlogPostModel).distinct()
        stmt = self._apply_filters(stmt, filters)
        stmt = stmt.offset(filters.offset).limit(filters.limit)
        result = await self.session.execute(stmt)
        return [blog_post_to_entity(m) for m in result.scalars().all()]

    async def count(self, filters: ListBlogPostsFilters) -> int:
        inner = self._apply_filters(select(BlogPostModel.id).distinct(), filters).subquery()
        stmt = select(func.count()).select_from(inner)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def create(self, post: BlogPost) -> BlogPost:
        model = blog_post_to_model(post)
        self.session.add(model)
        await self.session.flush()
        return blog_post_to_entity(model)

    async def update(self, post: BlogPost) -> None:
        model = blog_post_to_model(post)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, post: BlogPost) -> None:
        stmt = delete(BlogPostModel).where(BlogPostModel.id == post.id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_tags(self, post_id: UUID) -> list[BlogTag]:
        stmt = (
            select(BlogTagModel)
            .join(blog_post_tags, BlogTagModel.id == blog_post_tags.c.blog_tag_id)
            .where(blog_post_tags.c.blog_post_id == post_id)
        )
        result = await self.session.execute(stmt)
        return [blog_tag_to_entity(m) for m in result.scalars().all()]

    async def add_tag(self, post_id: UUID, tag_id: UUID) -> None:
        stmt = blog_post_tags.insert().values(blog_post_id=post_id, blog_tag_id=tag_id)
        await self.session.execute(stmt)
        await self.session.flush()

    async def remove_tag(self, post_id: UUID, tag_id: UUID) -> None:
        stmt = delete(blog_post_tags).where(
            blog_post_tags.c.blog_post_id == post_id,
            blog_post_tags.c.blog_tag_id == tag_id,
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_product_links(self, post_id: UUID) -> list[BlogProductLink]:
        stmt = (
            select(BlogProductLinkModel)
            .where(BlogProductLinkModel.blog_post_id == post_id)
            .order_by(BlogProductLinkModel.display_order)
        )
        result = await self.session.execute(stmt)
        return [blog_product_link_to_entity(m) for m in result.scalars().all()]

    async def add_product_link(self, link: BlogProductLink) -> BlogProductLink:
        model = blog_product_link_to_model(link)
        self.session.add(model)
        await self.session.flush()
        return blog_product_link_to_entity(model)

    async def remove_product_link(self, link_id: UUID) -> None:
        stmt = delete(BlogProductLinkModel).where(BlogProductLinkModel.id == link_id)
        await self.session.execute(stmt)
        await self.session.flush()


class SqlAlchemyBlogTagRepository(SqlAlchemyRepository):

    async def get_by_id(self, tag_id: UUID) -> BlogTag | None:
        stmt = select(BlogTagModel).where(BlogTagModel.id == tag_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return blog_tag_to_entity(model) if model else None

    async def get_by_slug(self, slug: str) -> BlogTag | None:
        stmt = select(BlogTagModel).where(BlogTagModel.slug == slug)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return blog_tag_to_entity(model) if model else None

    async def slug_exists(self, slug: str, exclude_id: UUID | None = None) -> bool:
        stmt = select(BlogTagModel.id).where(BlogTagModel.slug == slug)
        if exclude_id:
            stmt = stmt.where(BlogTagModel.id != exclude_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list(self) -> list[BlogTag]:
        stmt = select(BlogTagModel).order_by(BlogTagModel.name)
        result = await self.session.execute(stmt)
        return [blog_tag_to_entity(m) for m in result.scalars().all()]

    async def create(self, tag: BlogTag) -> BlogTag:
        model = blog_tag_to_model(tag)
        self.session.add(model)
        await self.session.flush()
        return blog_tag_to_entity(model)

    async def update(self, tag: BlogTag) -> None:
        model = blog_tag_to_model(tag)
        await self.session.merge(model)
        await self.session.flush()

    async def delete(self, tag: BlogTag) -> None:
        stmt = delete(BlogTagModel).where(BlogTagModel.id == tag.id)
        await self.session.execute(stmt)
        await self.session.flush()
