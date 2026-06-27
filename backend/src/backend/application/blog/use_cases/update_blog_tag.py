from dataclasses import dataclass

from src.backend.application.blog.dtos.blog_tags import UpdateBlogTagCommand
from src.backend.application.blog.errors import BlogSlugAlreadyExistsError, BlogTagNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class UpdateBlogTagUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: UpdateBlogTagCommand) -> None:
        async with self.uow:
            tag = await self.uow.blog_tags.get_by_id(cmd.tag_id)
            if tag is None:
                raise BlogTagNotFoundError("blog tag not found")
            if cmd.slug is not None and cmd.slug != str(tag.slug):
                if await self.uow.blog_tags.slug_exists(cmd.slug, exclude_id=tag.id):
                    raise BlogSlugAlreadyExistsError("slug already exists")
                from src.backend.domain.category.value_objects.slug.value_object import Slug
                tag.slug = Slug(cmd.slug)
            if cmd.name is not None:
                tag.change_name(cmd.name)
            await self.uow.blog_tags.update(tag)
            await self.uow.commit()
