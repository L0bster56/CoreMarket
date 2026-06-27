from dataclasses import dataclass

from src.backend.application.blog.dtos.list_blog_posts import (
    BlogPostListEntry,
    ListBlogPostsCommand,
    ListBlogPostsResult,
)
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class ListBlogPostsUseCase:
    uow: UnitOfWork

    async def execute(self, cmd: ListBlogPostsCommand) -> ListBlogPostsResult:
        async with self.uow:
            posts = await self.uow.blog_posts.list(cmd.filters)
            total = await self.uow.blog_posts.count(cmd.filters)
            return ListBlogPostsResult(
                items=[
                    BlogPostListEntry(
                        id=p.id,
                        title=p.title,
                        slug=str(p.slug),
                        short_description=p.short_description,
                        cover_image_url=p.cover_image_url,
                        category_id=p.category_id,
                        status=p.status.value,
                        created_at=p.created_at,
                        updated_at=p.updated_at,
                    )
                    for p in posts
                ],
                total=total,
            )
