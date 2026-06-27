import pytest

from src.backend.application.blog.dtos.create_blog_post import CreateBlogPostCommand
from src.backend.application.blog.errors import BlogSlugAlreadyExistsError
from src.backend.application.blog.use_cases.create_blog_post import CreateBlogPostUseCase
from src.backend.domain.blog.entity import BlogPost


class TestCreateBlogPostUseCase:
    async def test_creates_post_successfully(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.slug_exists.return_value = False
        mock_blog_post_repo.create.return_value = sample_blog_post
        uc = CreateBlogPostUseCase(uow=mock_uow)
        cmd = CreateBlogPostCommand(title="Sample Post", slug="sample-post")

        result = await uc.execute(cmd)

        assert result.id == sample_blog_post.id
        assert result.title == "Sample Post"
        assert result.slug == "sample-post"
        assert result.status == "draft"

    async def test_raises_conflict_when_slug_exists(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.slug_exists.return_value = True
        uc = CreateBlogPostUseCase(uow=mock_uow)
        cmd = CreateBlogPostCommand(title="Duplicate", slug="duplicate-slug")

        with pytest.raises(BlogSlugAlreadyExistsError):
            await uc.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.slug_exists.return_value = False
        mock_blog_post_repo.create.return_value = sample_blog_post
        uc = CreateBlogPostUseCase(uow=mock_uow)
        cmd = CreateBlogPostCommand(title="Sample Post", slug="sample-post")

        await uc.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_on_conflict(self, mock_uow, mock_blog_post_repo):
        mock_blog_post_repo.slug_exists.return_value = True
        uc = CreateBlogPostUseCase(uow=mock_uow)
        cmd = CreateBlogPostCommand(title="Post", slug="post")

        with pytest.raises(BlogSlugAlreadyExistsError):
            await uc.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_create_called_with_blog_post_entity(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.slug_exists.return_value = False
        mock_blog_post_repo.create.return_value = sample_blog_post
        uc = CreateBlogPostUseCase(uow=mock_uow)
        cmd = CreateBlogPostCommand(title="Sample Post", slug="sample-post", short_description="Desc")

        await uc.execute(cmd)

        created_arg = mock_blog_post_repo.create.call_args[0][0]
        assert isinstance(created_arg, BlogPost)
        assert created_arg.title == "Sample Post"
        assert str(created_arg.slug) == "sample-post"
        assert created_arg.short_description == "Desc"

    async def test_result_includes_created_at(self, mock_uow, mock_blog_post_repo, sample_blog_post):
        mock_blog_post_repo.slug_exists.return_value = False
        mock_blog_post_repo.create.return_value = sample_blog_post
        uc = CreateBlogPostUseCase(uow=mock_uow)
        cmd = CreateBlogPostCommand(title="Sample Post", slug="sample-post")

        result = await uc.execute(cmd)

        assert result.created_at is not None
        assert result.updated_at is not None
