import pytest

from src.backend.application.blog.dtos.delete_blog_post import DeleteBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError
from src.backend.application.blog.use_cases.delete_blog_post import DeleteBlogPostUseCase


class TestDeleteBlogPostUseCase:
    async def test_deletes_existing_post(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = DeleteBlogPostUseCase(uow=mock_uow)

        await uc.execute(DeleteBlogPostCommand(slug="sample-post"))

        mock_blog_post_repo.delete.assert_called_once_with(sample_blog_post)
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = DeleteBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(DeleteBlogPostCommand(slug="missing"))

    async def test_commit_not_called_on_not_found(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = DeleteBlogPostUseCase(uow=mock_uow)

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(DeleteBlogPostCommand(slug="missing"))

        mock_uow.commit.assert_not_called()
