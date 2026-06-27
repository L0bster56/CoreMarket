from dataclasses import dataclass

from src.backend.application.item.dtos.add_item_tag import AddItemTagCommand
from src.backend.application.item.errors import (
    ItemNotFoundError,
    ItemTagAlreadyAttachedError,
    ItemTagNotFoundError,
    ItemEditForbiddenError,
)
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class AddItemTagUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: AddItemTagCommand) -> None:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage item tags")

        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            tag = await self.uow.tags.get_by_id(cmd.tag_id)
            if tag is None:
                raise ItemTagNotFoundError("tag not found")

            existing_tags = await self.uow.items.get_tags(cmd.item_id)
            if any(t.id == cmd.tag_id for t in existing_tags):
                raise ItemTagAlreadyAttachedError("tag already attached to this item")

            await self.uow.items.add_tag(cmd.item_id, cmd.tag_id)
            await self.uow.commit()
