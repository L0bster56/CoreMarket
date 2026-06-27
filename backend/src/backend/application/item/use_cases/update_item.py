from dataclasses import dataclass

from src.backend.application.item.dtos.update_item import UpdateItemCommand
from src.backend.application.item.errors import ItemNotFoundError, ItemEditForbiddenError, InvalidViewCountError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.item.value_objects.marketplace_link import MarketplaceLink
from src.backend.domain.shared.value_objects.name.value_object import Name
from src.backend.domain.user.entity import User, UserRole


@dataclass
class UpdateItemUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: UpdateItemCommand) -> None:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can update items")

        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            if cmd.title is not None:
                item.change_name(cmd.title)

            if cmd.short_description is not None:
                item.change_short_description(cmd.short_description)

            if cmd.description is not None:
                item.change_description(cmd.description)

            if cmd.category_id is not None:
                item.change_category_id(cmd.category_id)

            if cmd.youtube_url is not None:
                item.change_youtube_url(cmd.youtube_url)

            if cmd.marketplace_links is not None:
                links = [
                    MarketplaceLink(name=Name(link.name), url=link.url, price=link.price)
                    for link in cmd.marketplace_links
                ]
                item.change_marketplace_links(links)

            if cmd.is_published is not None:
                item.change_is_published(cmd.is_published)

            if cmd.view_count is not None:
                try:
                    item.set_view_count(cmd.view_count)
                except ValueError as exc:
                    raise InvalidViewCountError(str(exc)) from exc

            await self.uow.items.update(item)
            await self.uow.commit()
