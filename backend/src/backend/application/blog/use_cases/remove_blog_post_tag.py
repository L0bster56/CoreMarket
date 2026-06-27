from dataclasses import dataclass

from src.backend.application.blog.dtos.add_blog_post_tag import RemoveBlogPostTagCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class RemoveBlogPostTagUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: RemoveBlogPostTagCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            await self.uow.blog_posts.remove_tag(post.id, cmd.tag_id)
            await self.uow.commit()
