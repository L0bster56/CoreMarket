import pytest

from src.backend.application.blog.dtos.publish_blog_post import UnpublishBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.unpublish_blog_post import UnpublishBlogPostUseCase
from src.backend.domain.blog.enums import BlogPostStatus


class TestUnpublishBlogPostUseCase:
    async def test_unpublishes_published_post(
        self, mock_uow, mock_blog_post_repo, published_blog_post
    ):
        mock_blog_post_repo.get_by_slug.return_value = published_blog_post
        uc = UnpublishBlogPostUseCase(uow=mock_uow)

        await uc.execute(UnpublishBlogPostCommand(slug="publishable-post"))

        assert published_blog_post.status == BlogPostStatus.draft
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = UnpublishBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(UnpublishBlogPostCommand(slug="missing"))

    async def test_update_called_with_post(self, mock_uow, mock_blog_post_repo, published_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = published_blog_post
        uc = UnpublishBlogPostUseCase(uow=mock_uow)

        await uc.execute(UnpublishBlogPostCommand(slug="publishable-post"))

        mock_blog_post_repo.update.assert_called_once_with(published_blog_post)
