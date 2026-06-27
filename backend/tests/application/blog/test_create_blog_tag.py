import pytest

from src.backend.application.blog.dtos.blog_tags import CreateBlogTagCommand
from src.backend.application.blog.errors import BlogSlugAlreadyExistsError
from src.backend.application.blog.use_cases.create_blog_tag import CreateBlogTagUseCase
from src.backend.domain.blog.entity import BlogTag


class TestCreateBlogTagUseCase:
    async def test_creates_tag_successfully(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.slug_exists.return_value = False
        mock_blog_tag_repo.create.return_value = sample_blog_tag
        uc = CreateBlogTagUseCase(uow=mock_uow)

        result = await uc.execute(CreateBlogTagCommand(name="Technology", slug="technology"))

        assert result.id == sample_blog_tag.id
        assert result.name == "Technology"
        assert result.slug == "technology"

    async def test_raises_conflict_when_slug_exists(self, mock_uow, mock_blog_tag_repo):
        mock_blog_tag_repo.slug_exists.return_value = True
        uc = CreateBlogTagUseCase(uow=mock_uow)

        with pytest.raises(BlogSlugAlreadyExistsError):
            await uc.execute(CreateBlogTagCommand(name="Technology", slug="technology"))

    async def test_commit_called_on_success(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.slug_exists.return_value = False
        mock_blog_tag_repo.create.return_value = sample_blog_tag
        uc = CreateBlogTagUseCase(uow=mock_uow)

        await uc.execute(CreateBlogTagCommand(name="Technology", slug="technology"))

        mock_uow.commit.assert_called_once()

    async def test_create_called_with_blog_tag_entity(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.slug_exists.return_value = False
        mock_blog_tag_repo.create.return_value = sample_blog_tag
        uc = CreateBlogTagUseCase(uow=mock_uow)

        await uc.execute(CreateBlogTagCommand(name="Technology", slug="technology"))

        created_arg = mock_blog_tag_repo.create.call_args[0][0]
        assert isinstance(created_arg, BlogTag)
        assert str(created_arg.name) == "Technology"
        assert str(created_arg.slug) == "technology"
