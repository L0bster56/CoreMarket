import pytest

from src.backend.application.category.dtos.list_categories import ListCategoriesCommand
from src.backend.application.category.use_cases.list_categories import ListCategoriesUseCase


class TestListCategoriesUseCase:

    async def test_returns_empty_list_when_no_categories(self, mock_uow, mock_category_repo):
        mock_category_repo.list_all.return_value = []
        use_case = ListCategoriesUseCase(uow=mock_uow)

        result = await use_case.execute(ListCategoriesCommand())

        assert result.items == []

    async def test_returns_all_categories(self, mock_uow, mock_category_repo, sample_category, another_category):
        mock_category_repo.list_all.return_value = [sample_category, another_category]
        use_case = ListCategoriesUseCase(uow=mock_uow)

        result = await use_case.execute(ListCategoriesCommand())

        assert len(result.items) == 2

    async def test_items_have_correct_fields(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.list_all.return_value = [sample_category]
        use_case = ListCategoriesUseCase(uow=mock_uow)

        result = await use_case.execute(ListCategoriesCommand())
        item = result.items[0]

        assert item.id == sample_category.id
        assert item.name == str(sample_category.name)
        assert item.slug == str(sample_category.slug)
        assert item.description == sample_category.description
        assert item.image_url == sample_category.image_url
        assert item.created_at == sample_category.created_at
        assert item.updated_at == sample_category.updated_at

    async def test_items_with_null_optional_fields(self, mock_uow, mock_category_repo, another_category):
        mock_category_repo.list_all.return_value = [another_category]
        use_case = ListCategoriesUseCase(uow=mock_uow)

        result = await use_case.execute(ListCategoriesCommand())
        item = result.items[0]

        assert item.description is None
        assert item.image_url is None

    async def test_calls_list_all_once(self, mock_uow, mock_category_repo):
        mock_category_repo.list_all.return_value = []
        use_case = ListCategoriesUseCase(uow=mock_uow)

        await use_case.execute(ListCategoriesCommand())

        mock_category_repo.list_all.assert_called_once()
