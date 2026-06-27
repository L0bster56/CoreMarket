import pytest

from src.backend.application.tag.dtos.create_tag import CreateTagCommand
from src.backend.application.tag.errors import TagSlugAlreadyExistsError
from src.backend.application.tag.use_cases.create_tag import CreateTagUseCase
from src.backend.domain.tag.entity import Tag


class TestCreateTagUseCase:

    async def test_creates_tag_successfully(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.exists_slug.return_value = False
        mock_tag_repo.create.return_value = sample_tag
        use_case = CreateTagUseCase(uow=mock_uow)
        cmd = CreateTagCommand(name="Python", slug="python")

        result = await use_case.execute(cmd)

        assert result.id == sample_tag.id
        assert result.name == str(sample_tag.name)
        assert result.slug == str(sample_tag.slug)

    async def test_raises_conflict_when_slug_exists(self, mock_uow, mock_tag_repo):
        mock_tag_repo.exists_slug.return_value = True
        use_case = CreateTagUseCase(uow=mock_uow)
        cmd = CreateTagCommand(name="Python", slug="python")

        with pytest.raises(TagSlugAlreadyExistsError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.exists_slug.return_value = False
        mock_tag_repo.create.return_value = sample_tag
        use_case = CreateTagUseCase(uow=mock_uow)
        cmd = CreateTagCommand(name="Python", slug="python")

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_on_conflict(self, mock_uow, mock_tag_repo):
        mock_tag_repo.exists_slug.return_value = True
        use_case = CreateTagUseCase(uow=mock_uow)
        cmd = CreateTagCommand(name="Python", slug="python")

        with pytest.raises(TagSlugAlreadyExistsError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_create_called_with_tag_entity(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.exists_slug.return_value = False
        mock_tag_repo.create.return_value = sample_tag
        use_case = CreateTagUseCase(uow=mock_uow)
        cmd = CreateTagCommand(name="Python", slug="python")

        await use_case.execute(cmd)

        created_arg = mock_tag_repo.create.call_args[0][0]
        assert isinstance(created_arg, Tag)
        assert str(created_arg.name) == "Python"
        assert str(created_arg.slug) == "python"
