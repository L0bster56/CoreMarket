from dataclasses import dataclass

from src.backend.application.blog.dtos.add_blog_post_tag import AddBlogPostTagCommand
from src.backend.application.blog.errors import BlogPostNotFoundError, BlogTagNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class AddBlogPostTagUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: AddBlogPostTagCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            tag = await self.uow.blog_tags.get_by_id(cmd.tag_id)
            if tag is None:
                raise BlogTagNotFoundError("blog tag not found")
            await self.uow.blog_posts.add_tag(post.id, tag.id)
            await self.uow.commit()
