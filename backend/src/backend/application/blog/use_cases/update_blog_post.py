from dataclasses import dataclass

from src.backend.application.blog.dtos.update_blog_post import UpdateBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError, BlogSlugAlreadyExistsError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class UpdateBlogPostUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: UpdateBlogPostCommand) -> None:
        async with self.uow:
            post = await self.uow.blog_posts.get_by_slug(cmd.slug)
            if post is None:
                raise BlogPostNotFoundError("blog post not found")

            if cmd.new_slug is not None and cmd.new_slug != cmd.slug:
                if await self.uow.blog_posts.slug_exists(cmd.new_slug, exclude_id=post.id):
                    raise BlogSlugAlreadyExistsError("slug already exists")
                post.change_slug(cmd.new_slug)

            if cmd.title is not None:
                post.change_title(cmd.title)
            if cmd.short_description is not None:
                post.short_description = cmd.short_description
                post.touch()
            if cmd.content is not None:
                post.set_content(cmd.content)
            if cmd.cover_image_url is not None:
                post.set_cover_image(cmd.cover_image_url)
            if cmd.category_id is not None:
                post.set_category(cmd.category_id)
            if cmd.seo_title is not None or cmd.seo_description is not None:
                post.set_seo(
                    seo_title=cmd.seo_title if cmd.seo_title is not None else post.seo_title,
                    seo_description=cmd.seo_description if cmd.seo_description is not None else post.seo_description,
                )

            await self.uow.blog_posts.update(post)
            await self.uow.commit()
