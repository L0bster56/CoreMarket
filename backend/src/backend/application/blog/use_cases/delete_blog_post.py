from dataclasses import dataclass

from src.backend.application.blog.dtos.delete_blog_post import DeleteBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class DeleteBlogPostUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: DeleteBlogPostCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            await self.uow.blog_posts.delete(post)
            await self.uow.commit()
