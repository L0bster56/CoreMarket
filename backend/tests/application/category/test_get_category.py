import pytest

from src.backend.application.category.dtos.get_category import GetCategoryCommand
from src.backend.application.category.errors import CategoryNotFoundError
from src.backend.application.category.use_cases.get_category import GetCategoryUseCase


class TestGetCategoryUseCase:

    async def test_returns_category_when_found(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = GetCategoryUseCase(uow=mock_uow)

        result = await use_case.execute(GetCategoryCommand(category_id=sample_category.id))

        assert result.id == sample_category.id
        assert result.name == str(sample_category.name)
        assert result.slug == str(sample_category.slug)
        assert result.description == sample_category.description
        assert result.image_url == sample_category.image_url

    async def test_result_has_timestamps(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = GetCategoryUseCase(uow=mock_uow)

        result = await use_case.execute(GetCategoryCommand(category_id=sample_category.id))

        assert result.created_at == sample_category.created_at
        assert result.updated_at == sample_category.updated_at

    async def test_raises_not_found_when_missing(self, mock_uow, mock_category_repo):
        mock_category_repo.get_by_id.return_value = None
        use_case = GetCategoryUseCase(uow=mock_uow)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(GetCategoryCommand(category_id=mock_category_repo.id))

    async def test_not_found_is_category_error(self, mock_uow, mock_category_repo):
        from src.backend.application.category.errors import CategoryError
        mock_category_repo.get_by_id.return_value = None
        use_case = GetCategoryUseCase(uow=mock_uow)

        with pytest.raises(CategoryError):
            await use_case.execute(GetCategoryCommand(category_id=mock_category_repo.id))

    async def test_calls_get_by_id_with_correct_id(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = GetCategoryUseCase(uow=mock_uow)
        cmd = GetCategoryCommand(category_id=sample_category.id)

        await use_case.execute(cmd)

        mock_category_repo.get_by_id.assert_called_once_with(sample_category.id)
