from dataclasses import dataclass

from src.backend.application.blog.dtos.publish_blog_post import UnpublishBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class UnpublishBlogPostUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: UnpublishBlogPostCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            post.unpublish()
            await self.uow.blog_posts.update(post)
            await self.uow.commit()
