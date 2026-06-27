import pytest

from src.backend.application.item.dtos.delete_item import DeleteItemCommand
from src.backend.application.item.errors import ItemEditForbiddenError, ItemNotFoundError
from src.backend.application.item.use_cases.delete_item import DeleteItemUseCase


class TestDeleteItemUseCase:

    async def test_admin_deletes_item(self, mock_uow, admin_user, sample_item):
        mock_uow.items.get_by_id.return_value = sample_item
        uc = DeleteItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(DeleteItemCommand(item_id=sample_item.id))

        mock_uow.items.delete.assert_called_once_with(sample_item)
        mock_uow.commit.assert_called_once()

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user, item_id):
        uc = DeleteItemUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(DeleteItemCommand(item_id=item_id))

    async def test_raises_when_item_not_found(self, mock_uow, admin_user, item_id):
        mock_uow.items.get_by_id.return_value = None
        uc = DeleteItemUseCase(uow=mock_uow, user=admin_user)

        with pytest.raises(ItemNotFoundError):
            await uc.execute(DeleteItemCommand(item_id=item_id))

    async def test_commit_not_called_when_forbidden(self, mock_uow, regular_user, item_id):
        uc = DeleteItemUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(DeleteItemCommand(item_id=item_id))

        mock_uow.commit.assert_not_called()
