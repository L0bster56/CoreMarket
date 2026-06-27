import pytest

from src.backend.application.category.dtos.create_category import CreateCategoryCommand
from src.backend.application.category.errors import CategorySlugAlreadyExistsError
from src.backend.application.category.use_cases.create_category import CreateCategoryUseCase
from src.backend.domain.category.entity import Category


class TestCreateCategoryUseCase:

    async def test_creates_category_successfully(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.exists_slug.return_value = False
        mock_category_repo.create.return_value = sample_category
        use_case = CreateCategoryUseCase(uow=mock_uow)
        cmd = CreateCategoryCommand(name="Electronics", slug="electronics")

        result = await use_case.execute(cmd)

        assert result.id == sample_category.id
        assert result.name == str(sample_category.name)
        assert result.slug == str(sample_category.slug)

    async def test_raises_conflict_when_slug_exists(self, mock_uow, mock_category_repo):
        mock_category_repo.exists_slug.return_value = True
        use_case = CreateCategoryUseCase(uow=mock_uow)
        cmd = CreateCategoryCommand(name="Electronics", slug="electronics")

        with pytest.raises(CategorySlugAlreadyExistsError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.exists_slug.return_value = False
        mock_category_repo.create.return_value = sample_category
        use_case = CreateCategoryUseCase(uow=mock_uow)
        cmd = CreateCategoryCommand(name="Electronics", slug="electronics")

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_slug_conflict(self, mock_uow, mock_category_repo):
        mock_category_repo.exists_slug.return_value = True
        use_case = CreateCategoryUseCase(uow=mock_uow)
        cmd = CreateCategoryCommand(name="Electronics", slug="electronics")

        with pytest.raises(CategorySlugAlreadyExistsError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_result_contains_optional_fields(self, mock_uow, mock_category_repo):
        category = Category.create(
            name="Electronics",
            slug="electronics",
            description="Best electronics",
            image_url="/media/categories/elec.jpg",
        )
        mock_category_repo.exists_slug.return_value = False
        mock_category_repo.create.return_value = category
        use_case = CreateCategoryUseCase(uow=mock_uow)
        cmd = CreateCategoryCommand(
            name="Electronics",
            slug="electronics",
            description="Best electronics",
            image_url="/media/categories/elec.jpg",
        )

        result = await use_case.execute(cmd)

        assert result.description == "Best electronics"
        assert result.image_url == "/media/categories/elec.jpg"

    async def test_create_called_with_category_entity(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.exists_slug.return_value = False
        mock_category_repo.create.return_value = sample_category
        use_case = CreateCategoryUseCase(uow=mock_uow)
        cmd = CreateCategoryCommand(name="Electronics", slug="electronics")

        await use_case.execute(cmd)

        created_arg = mock_category_repo.create.call_args[0][0]
        assert isinstance(created_arg, Category)
        assert str(created_arg.name) == "Electronics"
        assert str(created_arg.slug) == "electronics"
