from dataclasses import dataclass

from src.backend.application.blog.dtos.get_blog_post import (
    BlogCategoryResult,
    BlogProductLinkResult,
    BlogTagResult,
    GetBlogPostCommand,
    GetBlogPostResult,
)
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.interfaces import MarkdownRenderer
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class GetBlogPostUseCase:
    uow: UnitOfWork
    renderer: MarkdownRenderer

    async def execute(self, cmd: GetBlogPostCommand) -> GetBlogPostResult:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")

            tags = await self.uow.blog_posts.get_tags(post.id)
            product_links = await self.uow.blog_posts.get_product_links(post.id)

            category = None
            if post.category_id:
                cat = await self.uow.categories.get_by_id(post.category_id)
                if cat:
                    category = BlogCategoryResult(
                        id=cat.id,
                        name=str(cat.name),
                        slug=str(cat.slug),
                    )

            content_html = self.renderer.render(post.content) if post.content else None

            return GetBlogPostResult(
                id=post.id,
                title=post.title,
                slug=str(post.slug),
                short_description=post.short_description,
                content=post.content,
                content_html=content_html,
                cover_image_url=post.cover_image_url,
                category_id=post.category_id,
                category=category,
                status=post.status.value,
                seo_title=post.seo_title,
                seo_description=post.seo_description,
                tags=[BlogTagResult(id=t.id, name=str(t.name), slug=str(t.slug)) for t in tags],
                product_links=[
                    BlogProductLinkResult(id=l.id, product_id=l.product_id, display_order=l.display_order)
                    for l in product_links
                ],
                created_at=post.created_at,
                updated_at=post.updated_at,
            )
