from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.add_blog_post_tag import AddBlogPostTagCommand
from src.backend.application.blog.errors import BlogPostNotFoundError, BlogTagNotFoundError
from src.backend.application.blog.use_cases.add_blog_post_tag import AddBlogPostTagUseCase


class TestAddBlogPostTagUseCase:
    async def test_adds_tag_to_post(
        self, mock_uow, mock_blog_post_repo, mock_blog_tag_repo, sample_blog_post, sample_blog_tag
    ):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_tag_repo.get_by_id.return_value = sample_blog_tag
        uc = AddBlogPostTagUseCase(uow=mock_uow)

        await uc.execute(AddBlogPostTagCommand(slug="sample-post", tag_id=sample_blog_tag.id))

        mock_blog_post_repo.add_tag.assert_called_once_with(sample_blog_post.id, sample_blog_tag.id)
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(
        self, mock_uow, mock_blog_post_repo
    ):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = AddBlogPostTagUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(AddBlogPostTagCommand(slug="missing", tag_id=uuid4()))

    async def test_raises_not_found_for_missing_tag(
        self, mock_uow, mock_blog_post_repo, mock_blog_tag_repo, sample_blog_post
    ):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_tag_repo.get_by_id.return_value = None
        uc = AddBlogPostTagUseCase(uow=mock_uow)

        with pytest.raises(BlogTagNotFoundError):
            await uc.execute(AddBlogPostTagCommand(slug="sample-post", tag_id=uuid4()))

    async def test_commit_not_called_on_missing_tag(
        self, mock_uow, mock_blog_post_repo, mock_blog_tag_repo, sample_blog_post
    ):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_tag_repo.get_by_id.return_value = None
        uc = AddBlogPostTagUseCase(uow=mock_uow)

        with pytest.raises(BlogTagNotFoundError):
            await uc.execute(AddBlogPostTagCommand(slug="sample-post", tag_id=uuid4()))

        mock_uow.commit.assert_not_called()
