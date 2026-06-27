import pytest
from uuid import uuid4

from src.backend.application.item.dtos.create_item import CreateItemCommand
from src.backend.application.item.errors import ItemEditForbiddenError
from src.backend.application.item.use_cases.create_item import CreateItemUseCase


class TestCreateItemUseCase:

    async def test_admin_creates_item_successfully(self, mock_uow, admin_user, sample_item):
        mock_uow.items.create.return_value = sample_item
        uc = CreateItemUseCase(uow=mock_uow, user=admin_user)
        cmd = CreateItemCommand(
            title="Test Item",
            short_description="Short",
            description="Full",
            category_id=uuid4(),
        )

        result = await uc.execute(cmd)

        assert result.id == sample_item.id
        assert result.title == str(sample_item.name)

    async def test_non_admin_raises_forbidden(self, mock_uow, regular_user):
        uc = CreateItemUseCase(uow=mock_uow, user=regular_user)
        cmd = CreateItemCommand(
            title="Test",
            short_description="Short",
            description="Full",
            category_id=uuid4(),
        )

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(cmd)

    async def test_commit_called_on_success(self, mock_uow, admin_user, sample_item):
        mock_uow.items.create.return_value = sample_item
        uc = CreateItemUseCase(uow=mock_uow, user=admin_user)

        await uc.execute(CreateItemCommand(
            title="Test Item", short_description="Short", description="Full desc", category_id=uuid4()
        ))

        mock_uow.commit.assert_called_once()

    async def test_commit_not_called_when_forbidden(self, mock_uow, regular_user):
        uc = CreateItemUseCase(uow=mock_uow, user=regular_user)

        with pytest.raises(ItemEditForbiddenError):
            await uc.execute(CreateItemCommand(
                title="T", short_description="S", description="D", category_id=uuid4()
            ))

        mock_uow.commit.assert_not_called()

    async def test_result_has_correct_fields(self, mock_uow, admin_user, sample_item):
        mock_uow.items.create.return_value = sample_item
        uc = CreateItemUseCase(uow=mock_uow, user=admin_user)

        result = await uc.execute(CreateItemCommand(
            title="Test Item", short_description="Short", description="Full", category_id=sample_item.category_id
        ))

        assert result.short_description == sample_item.short_description
        assert result.category_id == sample_item.category_id
        assert result.is_published == sample_item.is_published
