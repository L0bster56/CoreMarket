import pytest
from uuid import uuid4

from src.backend.application.item.dtos.update_item import UpdateItemCommand
from src.backend.application.item.errors import ItemEditForbiddenError, ItemNotFoundError, InvalidViewCountError
from src.backend.application.item.use_cases.update_item import UpdateItemUseCase


class TestUpdateItemUseCase:

    async def test_admin_updates_item(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(UpdateItemCommand(item_id=sample_item.id, title="Updated Title"))

        assert str(sample_item.name) == "Updated Title"
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user, item_id):
        uc = UpdateItemUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(UpdateItemCommand(item_id=item_id))

    async def test_raises_when_item_not_found(self, mock_uow, admin_user, item_id):
        mock_uow.items.get_by_id.return_value = None
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(UpdateItemCommand(item_id=item_id, title="New"))

    async def test_commit_not_called_when_not_found(self, mock_uow, admin_user, item_id):
        mock_uow.items.get_by_id.return_value = None
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(UpdateItemCommand(item_id=item_id))

        mock_uow.commit.assert_not_called()

    async def test_update_called_with_item(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(UpdateItemCommand(item_id=sample_item.id, is_published=True))

        mock_uow.items.update.assert_called_once_with(sample_item)

    async def test_skips_none_fields(self, mock_uow, admin_user, sample_item):
        original_description = sample_item.short_description
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(UpdateItemCommand(item_id=sample_item.id, title="New Title"))

        assert sample_item.short_description == original_description

    async def test_updates_view_count(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(UpdateItemCommand(item_id=sample_item.id, view_count=500))

        assert sample_item.view_count == 500
        mock_uow.commit.assert_called_once()

    async def test_view_count_none_is_skipped(self, mock_uow, admin_user, sample_item):
        original = sample_item.view_count
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(UpdateItemCommand(item_id=sample_item.id, title="New Title"))

        assert sample_item.view_count == original

    async def test_invalid_view_count_zero_raises(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(InvalidViewCountError):
            await uc.execute(UpdateItemCommand(item_id=sample_item.id, view_count=0))

    async def test_invalid_view_count_negative_raises(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        uc = UpdateItemUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(InvalidViewCountError):
            await uc.execute(UpdateItemCommand(item_id=sample_item.id, view_count=-10))
