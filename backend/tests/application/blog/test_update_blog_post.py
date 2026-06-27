import pytest

from src.backend.application.blog.dtos.update_blog_post import UpdateBlogPostCommand
from src.backend.application.blog.errors import BlogPostNotFoundError, BlogSlugAlreadyExistsError
from src.backend.application.blog.use_cases.update_blog_post import UpdateBlogPostUseCase


class TestUpdateBlogPostUseCase:
    async def test_updates_title(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.slug_exists.return_value = False
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="sample-post", title="Updated Title")

        await uc.execute(cmd)

        assert sample_blog_post.title == "Updated Title"
        mock_blog_post_repo.update.assert_called_once_with(sample_blog_post)
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_post(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="missing")

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(cmd)

    async def test_raises_conflict_when_new_slug_taken(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.slug_exists.return_value = True
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="sample-post", new_slug="taken-slug")

        with pytest.raises(BlogSlugAlreadyExistsError):
            await uc.execute(cmd)

    async def test_updates_slug_when_available(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        mock_blog_post_repo.slug_exists.return_value = False
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="sample-post", new_slug="new-slug")

        await uc.execute(cmd)

        assert str(sample_blog_post.slug) == "new-slug"

    async def test_skips_slug_check_when_slug_unchanged(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="sample-post", new_slug="sample-post")

        await uc.execute(cmd)

        mock_blog_post_repo.slug_exists.assert_not_called()

    async def test_updates_content(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.get_by_slug.return_value = sample_blog_post
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="sample-post", content="# New Content")

        await uc.execute(cmd)

        assert sample_blog_post.content == "# New Content"

    async def test_commit_not_called_on_not_found(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.get_by_slug.return_value = None
        uc = UpdateBlogPostUseCase(uow=mock_uow)
        cmd = UpdateBlogPostCommand(slug="missing")

        with pytest.raises(BlogPostNotFoundError):
            await uc.execute(cmd)

        mock_uow.commit.assert_not_called()
