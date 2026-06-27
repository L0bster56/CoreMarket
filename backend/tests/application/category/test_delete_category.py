import pytest

from src.backend.application.category.dtos.delete_category import DeleteCategoryCommand
from src.backend.application.category.errors import CategoryNotFoundError
from src.backend.application.category.use_cases.delete_category import DeleteCategoryUseCase


class TestDeleteCategoryUseCase:

    async def test_deletes_category_successfully(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = DeleteCategoryUseCase(uow=mock_uow)
        cmd = DeleteCategoryCommand(category_id=sample_category.id)

        await use_case.execute(cmd)

        mock_category_repo.delete.assert_called_once_with(sample_category)

    async def test_commit_called_on_success(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = DeleteCategoryUseCase(uow=mock_uow)
        cmd = DeleteCategoryCommand(category_id=sample_category.id)

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_raises_not_found_when_missing(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = None
        use_case = DeleteCategoryUseCase(uow=mock_uow)
        cmd = DeleteCategoryCommand(category_id=sample_category.id)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(cmd)

    async def test_delete_not_called_when_not_found(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = None
        use_case = DeleteCategoryUseCase(uow=mock_uow)
        cmd = DeleteCategoryCommand(category_id=sample_category.id)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(cmd)

        mock_category_repo.delete.assert_not_called()

    async def test_commit_not_called_when_not_found(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = None
        use_case = DeleteCategoryUseCase(uow=mock_uow)
        cmd = DeleteCategoryCommand(category_id=sample_category.id)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_calls_get_by_id_with_correct_id(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = DeleteCategoryUseCase(uow=mock_uow)
        cmd = DeleteCategoryCommand(category_id=sample_category.id)

        await use_case.execute(cmd)

        mock_category_repo.get_by_id.assert_called_once_with(sample_category.id)
