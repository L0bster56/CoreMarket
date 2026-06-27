from dataclasses import dataclass

from src.backend.application.blog.dtos.create_blog_post import CreateBlogPostCommand, CreateBlogPostResult
from src.backend.application.blog.errors import BlogSlugAlreadyExistsError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.blog.entity import BlogPost


@dataclass
class CreateBlogPostUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: CreateBlogPostCommand) -> CreateBlogPostResult:
        async with self.uow:
            if await self.uow.blog_posts.slug_exists(cmd.slug):
                raise BlogSlugAlreadyExistsError("slug already exists")

            post = BlogPost.create(
                title=cmd.title,
                slug=cmd.slug,
                short_description=cmd.short_description,
            )
            created = await self.uow.blog_posts.create(post)
            await self.uow.commit()

            return CreateBlogPostResult(
                id=created.id,
                title=created.title,
                slug=str(created.slug),
                short_description=created.short_description,
                status=created.status.value,
                created_at=created.created_at,
                updated_at=created.updated_at,
            )
