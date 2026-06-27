import pytest

from src.backend.application.tag.dtos.get_tag import GetTagCommand
from src.backend.application.tag.errors import TagNotFoundError
from src.backend.application.tag.use_cases.get_tag import GetTagUseCase


class TestGetTagUseCase:

    async def test_returns_tag_when_found(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.get_by_id.return_value = sample_tag
        use_case = GetTagUseCase(uow=mock_uow)

        result = await use_case.execute(GetTagCommand(tag_id=sample_tag.id))

        assert result.id == sample_tag.id
        assert result.name == str(sample_tag.name)
        assert result.slug == str(sample_tag.slug)

    async def test_raises_not_found_when_missing(self, mock_uow, mock_tag_repo):
        import uuid
        mock_tag_repo.get_by_id.return_value = None
        use_case = GetTagUseCase(uow=mock_uow)

        with pytest.raises(TagNotFoundError):
            await use_case.execute(GetTagCommand(tag_id=uuid.uuid4()))

    async def test_get_by_id_called_with_correct_id(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.get_by_id.return_value = sample_tag
        use_case = GetTagUseCase(uow=mock_uow)

        await use_case.execute(GetTagCommand(tag_id=sample_tag.id))

        mock_tag_repo.get_by_id.assert_called_once_with(sample_tag.id)
