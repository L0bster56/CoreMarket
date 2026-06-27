from dataclasses import dataclass

from src.backend.application.blog.dtos.link_product import LinkProductCommand, LinkProductResult, UnlinkProductCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.blog.product_link import BlogProductLink


@dataclass
class LinkProductUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: LinkProductCommand) -> LinkProductResult:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            link = BlogProductLink(
                blog_post_id=post.id,
                product_id=cmd.product_id,
                display_order=cmd.display_order,
            )
            created = await self.uow.blog_posts.add_product_link(link)
            await self.uow.commit()
            return LinkProductResult(
                id=created.id,
                product_id=created.product_id,
                display_order=created.display_order,
            )


@dataclass
class UnlinkProductUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: UnlinkProductCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            await self.uow.blog_posts.remove_product_link(cmd.link_id)
            await self.uow.commit()
