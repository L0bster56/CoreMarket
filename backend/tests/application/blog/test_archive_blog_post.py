import pytest

from src.backend.application.blog.dtos.publish_blog_post import ArchiveBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.archive_blog_post import ArchiveBlogPostUseCase
from src.backend.domain.blog.enums import BlogPostStatus


class TestArchiveBlogPostUseCase:
    async def test_archives_post(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = ArchiveBlogPostUseCase(uow=mock_uow)

        await uc.execute(ArchiveBlogPostCommand(slug="sample-post"))

        assert sample_blog_post.status == BlogPostStatus.archived
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = ArchiveBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(ArchiveBlogPostCommand(slug="missing"))

    async def test_archives_published_post(self, mock_uow, mock_blog_post_repo, published_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = published_blog_post
        uc = ArchiveBlogPostUseCase(uow=mock_uow)

        await uc.execute(ArchiveBlogPostCommand(slug="publishable-post"))

        assert published_blog_post.status == BlogPostStatus.archived
