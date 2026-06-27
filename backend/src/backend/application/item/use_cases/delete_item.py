from dataclasses import dataclass

from src.backend.application.item.dtos.delete_item import DeleteItemCommand
from src.backend.application.item.errors import ItemNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class DeleteItemUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: DeleteItemCommand) -> None:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can delete items")

        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            await self.uow.items.delete(item)
            await self.uow.commit()
