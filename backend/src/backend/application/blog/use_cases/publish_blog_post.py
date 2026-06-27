from dataclasses import dataclass

from src.backend.application.blog.dtos.publish_blog_post import PublishBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.shared.errors import BadRequestError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.blog.errors import BlogPostAlreadyPublishedError, BlogPostNoCategoryError, BlogPostNoContentError


@dataclass
class PublishBlogPostUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: PublishBlogPostCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")
            try:
                post.publish()
            except BlogPostNoCategoryError:
                raise BadRequestError("Post must have a category before publishing")
            except BlogPostNoContentError:
                raise BadRequestError("Post must have content before publishing")
            except BlogPostAlreadyPublishedError:
                raise BadRequestError("Post is already published")
            await self.uow.blog_posts.update(post)
            await self.uow.commit()
