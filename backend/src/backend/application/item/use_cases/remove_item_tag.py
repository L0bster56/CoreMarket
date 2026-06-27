from dataclasses import dataclass

from src.backend.application.item.dtos.remove_item_tag import RemoveItemTagCommand
from src.backend.application.item.errors import ItemNotFoundError, ItemTagNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class RemoveItemTagUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: RemoveItemTagCommand) -> None:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage item tags")

        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            existing_tags = await self.uow.items.get_tags(cmd.item_id)
            if not any(t.id == cmd.tag_id for t in existing_tags):
                raise ItemTagNotFoundError("tag is not attached to this item")

            await self.uow.items.remove_tag(cmd.item_id, cmd.tag_id)
            await self.uow.commit()
