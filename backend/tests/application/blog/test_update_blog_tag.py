from uuid import uuid4

import pytest

from src.backend.application.blog.dtos.blog_tags import UpdateBlogTagCommand
from src.backend.application.blog.errors import BlogSlugAlreadyExistsError, BlogTagNotFoundError
from src.backend.application.blog.use_cases.update_blog_tag import UpdateBlogTagUseCase


class TestUpdateBlogTagUseCase:
    async def test_updates_name(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.get_by_id.return_value = sample_blog_tag
        uc = UpdateBlogTagUseCase(uow=mock_uow)

        await uc.execute(UpdateBlogTagCommand(tag_id=sample_blog_tag.id, name="Science"))

        assert str(sample_blog_tag.name) == "Science"
        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_for_missing_tag(self, mock_uow, mock_blog_tag_repo):
        mock_blog_tag_repo.get_by_id.return_value = None
        uc = UpdateBlogTagUseCase(uow=mock_uow)

        with pytest.raises(BlogTagNotFoundError):
            await uc.execute(UpdateBlogTagCommand(tag_id=uuid4()))

    async def test_raises_conflict_when_slug_taken(
        self, mock_uow, mock_blog_tag_repo, sample_blog_tag
    ):
        mock_blog_tag_repo.get_by_id.return_value = sample_blog_tag
        mock_blog_tag_repo.slug_exists.return_value = True
        uc = UpdateBlogTagUseCase(uow=mock_uow)

        with pytest.raises(BlogSlugAlreadyExistsError):
            await uc.execute(
                UpdateBlogTagCommand(tag_id=sample_blog_tag.id, slug="taken-slug")
            )

    async def test_updates_slug_when_available(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.get_by_id.return_value = sample_blog_tag
        mock_blog_tag_repo.slug_exists.return_value = False
        uc = UpdateBlogTagUseCase(uow=mock_uow)

        await uc.execute(UpdateBlogTagCommand(tag_id=sample_blog_tag.id, slug="new-slug"))

        assert str(sample_blog_tag.slug) == "new-slug"
