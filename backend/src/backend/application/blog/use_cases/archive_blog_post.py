from dataclasses import dataclass

from src.backend.application.blog.dtos.publish_blog_post import ArchiveBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class ArchiveBlogPostUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: ArchiveBlogPostCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            post.archive()
            await self.uow.blog_posts.update(post)
            await self.uow.commit()
