from dataclasses import dataclass

from src.backend.application.blog.dtos.blog_tags import CreateBlogTagCommand, CreateBlogTagResult
from src.backend.application.blog.errors import BlogSlugAlreadyExistsError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.blog.entity import BlogTag


@dataclass
class CreateBlogTagUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: CreateBlogTagCommand) -> CreateBlogTagResult:
        async with self.uow:
            if await self.uow.blog_tags.slug_exists(cmd.slug):
                raise BlogSlugAlreadyExistsError("slug already exists")
            tag = BlogTag.create(name=cmd.name, slug=cmd.slug)
            created = await self.uow.blog_tags.create(tag)
            await self.uow.commit()
            return CreateBlogTagResult(
                id=created.id,
                name=str(created.name),
                slug=str(created.slug),
            )
