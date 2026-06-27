from typing import Protocol

from src.backend.application.blog.repository import BlogPostRepository, BlogTagRepository
from src.backend.application.category.repository import CategoryRepository
from src.backend.application.comment.repository import CommentRepository
from src.backend.application.item.repository import CharacteristicRepository, GalleryRepository, ItemRepository
from src.backend.application.rating.repository import RatingRepository
from src.backend.application.tag.repository import TagRepository
from src.backend.application.user.repository import UserRepository


class UnitOfWork(Protocol):
    users: UserRepository
    categories: CategoryRepository
    tags: TagRepository
    comments: CommentRepository
    ratings: RatingRepository
    items: ItemRepository
    characteristics: CharacteristicRepository
    gallery: GalleryRepository
    blog_posts: BlogPostRepository
    blog_tags: BlogTagRepository

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self): ...

    async def __aexit__(self, exc_type, exc_val, exc_tb): ...
