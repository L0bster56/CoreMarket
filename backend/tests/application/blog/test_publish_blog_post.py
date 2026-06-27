import pytest

from src.backend.application.blog.dtos.publish_blog_post import PublishBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.publish_blog_post import PublishBlogPostUseCase
from src.backend.application.shared.errors import BadRequestError
from src.backend.domain.blog.enums import BlogPostStatus


class TestPublishBlogPostUseCase:
    async def test_publishes_valid_post(self, mock_uow, mock_blog_post_repo, publishable_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = publishable_blog_post
        uc = PublishBlogPostUseCase(uow=mock_uow)

        await uc.execute(PublishBlogPostCommand(slug="publishable-post"))

        assert publishable_blog_post.status == BlogPostStatus.published
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = PublishBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(PublishBlogPostCommand(slug="missing"))

    async def test_raises_bad_request_when_no_category(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        sample_blog_post.set_content("Some content")
        sample_blog_post.category_id = None
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = PublishBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BadRequestError):
            await uc.execute(PublishBlogPostCommand(slug="sample-post"))

    async def test_raises_bad_request_when_no_content(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        from uuid import uuid4
        sample_blog_post.set_category(uuid4())
        sample_blog_post.content = None
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = PublishBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BadRequestError):
            await uc.execute(PublishBlogPostCommand(slug="sample-post"))

    async def test_raises_bad_request_when_already_published(
        self, mock_uow, mock_blog_post_repo, published_blog_post
    ):
        mock_blog_post_repo.get_by_slug.return_value = published_blog_post
        uc = PublishBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BadRequestError):
            await uc.execute(PublishBlogPostCommand(slug="publishable-post"))

    async def test_commit_not_called_on_not_found(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = PublishBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(PublishBlogPostCommand(slug="missing"))

        mock_uow.commit.assert_not_called()
