import uuid

import pytest

from src.backend.application.tag.dtos.delete_tag import DeleteTagCommand
from src.backend.application.tag.errors import TagNotFoundError
from src.backend.application.tag.use_cases.delete_tag import DeleteTagUseCase


class TestDeleteTagUseCase:

    async def test_deletes_tag_successfully(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.get_by_id.return_value = sample_tag
        use_case = DeleteTagUseCase(uow=mock_uow)
        cmd = DeleteTagCommand(tag_id=sample_tag.id)

        await use_case.execute(cmd)

        mock_tag_repo.delete.assert_called_once_with(sample_tag)

    async def test_raises_not_found_when_missing(self, mock_uow, mock_tag_repo):
        mock_tag_repo.get_by_id.return_value = None
        use_case = DeleteTagUseCase(uow=mock_uow)
        cmd = DeleteTagCommand(tag_id=uuid.uuid4())

        with pytest.raises(TagNotFoundError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_tag_repo, sample_tag):
        mock_tag_repo.get_by_id.return_value = sample_tag
        use_case = DeleteTagUseCase(uow=mock_uow)
        cmd = DeleteTagCommand(tag_id=sample_tag.id)

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_not_found(self, mock_uow, mock_tag_repo):
        mock_tag_repo.get_by_id.return_value = None
        use_case = DeleteTagUseCase(uow=mock_uow)
        cmd = DeleteTagCommand(tag_id=uuid.uuid4())

        with pytest.raises(TagNotFoundError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_delete_not_called_when_not_found(self, mock_uow, mock_tag_repo):
        mock_tag_repo.get_by_id.return_value = None
        use_case = DeleteTagUseCase(uow=mock_uow)
        cmd = DeleteTagCommand(tag_id=uuid.uuid4())

        with pytest.raises(TagNotFoundError):
            await use_case.execute(cmd)

        mock_tag_repo.delete.assert_not_called()
