from dataclasses import dataclass

from src.backend.application.blog.dtos.blog_tags import BlogTagItem, ListBlogTagsCommand, ListBlogTagsResult
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class ListBlogTagsUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: ListBlogTagsCommand) -> ListBlogTagsResult:
        async with self.uow:
            tags = await self.uow.blog_tags.list()
            return ListBlogTagsResult(
                items=[BlogTagItem(id=t.id, name=str(t.name), slug=str(t.slug)) for t in tags]
            )
