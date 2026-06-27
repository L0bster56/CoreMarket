from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.list_blog_posts import (
    ListBlogPostsCommand,
    ListBlogPostsFilters,
)
from src.backend.application.blog.use_cases.list_blog_posts import ListBlogPostsUseCase
from src.backend.domain.blog.entity import BlogPost
from src.backend.domain.blog.enums import BlogPostStatus


def make_post(title: str, slug: str, status: BlogPostStatus = BlogPostStatus.draft) -> BlogPost:
    post = BlogPost.create(title=title, slug=slug)
    if status == BlogPostStatus.published:
        post.set_category(uuid4())
        post.set_content("Content")
        post.publish()
    elif status == BlogPostStatus.archived:
        post.archive()
    return post


class TestListBlogPostsUseCase:
    async def test_returns_all_posts(self, mock_uow, mock_blog_post_repo):
        posts = [make_post("Post 1", "post-1"), make_post("Post 2", "post-2")]
        mock_blog_post_repo.list.return_value = posts
        mock_blog_post_repo.count.return_value = 2
        uc = ListBlogPostsUseCase(uow=mock_uow)

        result = await uc.execute(ListBlogPostsCommand())

        assert result.total == 2
        assert len(result.items) == 2

    async def test_returns_empty_list(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.list.return_value = []
        mock_blog_post_repo.count.return_value = 0
        uc = ListBlogPostsUseCase(uow=mock_uow)

        result = await uc.execute(ListBlogPostsCommand())

        assert result.total == 0
        assert result.items == []

    async def test_passes_filters_to_repository(self, mock_uow, mock_blog_post_repo):
        cat_id = uuid4()
        mock_blog_post_repo.list.return_value = []
        mock_blog_post_repo.count.return_value = 0
        uc = ListBlogPostsUseCase(uow=mock_uow)
        filters = ListBlogPostsFilters(
            status="published",
            category_id=cat_id,
            tag_slug="python",
            search="hello",
            offset=0,
            limit=10,
        )

        await uc.execute(ListBlogPostsCommand(filters=filters))

        called_filters = mock_blog_post_repo.list.call_args[0][0]
        assert called_filters.status == "published"
        assert called_filters.category_id == cat_id
        assert called_filters.tag_slug == "python"
        assert called_filters.search == "hello"

    async def test_filters_by_status(self, mock_uow, mock_blog_post_repo):
        published = make_post("Pub", "pub", BlogPostStatus.published)
        mock_blog_post_repo.list.return_value = [published]
        mock_blog_post_repo.count.return_value = 1
        uc = ListBlogPostsUseCase(uow=mock_uow)
        filters = ListBlogPostsFilters(status="published")

        result = await uc.execute(ListBlogPostsCommand(filters=filters))

        assert result.items[0].status == "published"

    async def test_pagination_params_passed_to_repository(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.list.return_value = []
        mock_blog_post_repo.count.return_value = 100
        uc = ListBlogPostsUseCase(uow=mock_uow)
        filters = ListBlogPostsFilters(offset=20, limit=5)

        await uc.execute(ListBlogPostsCommand(filters=filters))

        called_filters = mock_blog_post_repo.list.call_args[0][0]
        assert called_filters.offset == 20
        assert called_filters.limit == 5

    async def test_maps_post_fields_to_entries(self, mock_uow, mock_blog_post_repo):
        post = make_post("My Post", "my-post")
        post.cover_image_url = "blog/cover.jpg"
        mock_blog_post_repo.list.return_value = [post]
        mock_blog_post_repo.count.return_value = 1
        uc = ListBlogPostsUseCase(uow=mock_uow)

        result = await uc.execute(ListBlogPostsCommand())

        entry = result.items[0]
        assert entry.id == post.id
        assert entry.title == "My Post"
        assert entry.slug == "my-post"
        assert entry.cover_image_url == "blog/cover.jpg"

    async def test_count_and_list_both_called(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.list.return_value = []
        mock_blog_post_repo.count.return_value = 0
        uc = ListBlogPostsUseCase(uow=mock_uow)

        await uc.execute(ListBlogPostsCommand())

        mock_blog_post_repo.list.assert_called_once()
        mock_blog_post_repo.count.assert_called_once()
