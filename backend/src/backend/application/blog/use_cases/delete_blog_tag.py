from dataclasses import dataclass

from src.backend.application.blog.dtos.blog_tags import DeleteBlogTagCommand
from src.backend.application.blog.errors import BlogTagNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class DeleteBlogTagUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: DeleteBlogTagCommand) -> None:
        async with self.uow:
            tag = await self.uow.blog_tags.get_by_id(cmd.tag_id)
            if tag is None:
                raise BlogTagNotFoundError("blog tag not found")
            await self.uow.blog_tags.delete(tag)
            await self.uow.commit()
