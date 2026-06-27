import time

import pytest

from src.backend.application.category.dtos.update_category import UpdateCategoryCommand
from src.backend.application.category.errors import CategoryNotFoundError
from src.backend.application.category.use_cases.update_category import UpdateCategoryUseCase


class TestUpdateCategoryUseCase:

    async def test_updates_name(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, name="Gadgets")

        await use_case.execute(cmd)

        assert str(sample_category.name) == "Gadgets"

    async def test_updates_description(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, description="New description")

        await use_case.execute(cmd)

        assert sample_category.description == "New description"

    async def test_updates_image_url(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, image_url="/new.jpg")

        await use_case.execute(cmd)

        assert sample_category.image_url == "/new.jpg"

    async def test_updates_multiple_fields_at_once(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(
            category_id=sample_category.id,
            name="Gadgets",
            description="All gadgets",
            image_url="/gadgets.jpg",
        )

        await use_case.execute(cmd)

        assert str(sample_category.name) == "Gadgets"
        assert sample_category.description == "All gadgets"
        assert sample_category.image_url == "/gadgets.jpg"

    async def test_skips_none_fields(self, mock_uow, mock_category_repo, sample_category):
        original_name = str(sample_category.name)
        original_description = sample_category.description
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, image_url="/new.jpg")

        await use_case.execute(cmd)

        assert str(sample_category.name) == original_name
        assert sample_category.description == original_description

    async def test_raises_not_found_when_missing(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = None
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, name="Gadgets")

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, name="Gadgets")

        await use_case.execute(cmd)

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_not_found(self, mock_uow, mock_category_repo, sample_category):
        mock_category_repo.get_by_id.return_value = None
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, name="Gadgets")

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(cmd)

        mock_uow.commit.assert_not_called()

    async def test_update_touches_updated_at(self, mock_uow, mock_category_repo, sample_category):
        before = sample_category.updated_at
        mock_category_repo.get_by_id.return_value = sample_category
        use_case = UpdateCategoryUseCase(uow=mock_uow)
        cmd = UpdateCategoryCommand(category_id=sample_category.id, name="Gadgets")
        time.sleep(0.005)

        await use_case.execute(cmd)

        assert sample_category.updated_at > before
