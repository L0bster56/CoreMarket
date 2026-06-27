from dataclasses import dataclass

from src.backend.application.item.dtos.create_item import (
    CreateItemCommand,
    CreateItemResult,
    MarketplaceLinkData,
)
from src.backend.application.item.errors import ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.item.entity import Item
from src.backend.domain.item.value_objects.marketplace_link import MarketplaceLink
from src.backend.domain.shared.value_objects.name.value_object import Name
from src.backend.domain.user.entity import User, UserRole


@dataclass
class CreateItemUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: CreateItemCommand) -> CreateItemResult:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can create items")

        async with self.uow:
            marketplace_links = [
                MarketplaceLink(name=Name(link.name), url=link.url, price=link.price)
                for link in cmd.marketplace_links
            ]

            item = Item.create(
                name=cmd.title,
                short_description=cmd.short_description,
                description=cmd.description,
                category_id=cmd.category_id,
                youtube_url=cmd.youtube_url,
                marketplace_links=marketplace_links,
            )

            created = await self.uow.items.create(item)
            await self.uow.commit()

            return CreateItemResult(
                id=created.id,
                title=str(created.name),
                short_description=created.short_description,
                description=created.description,
                category_id=created.category_id,
                youtube_url=created.youtube_url,
                marketplace_links=[
                    MarketplaceLinkData(name=str(link.name), url=link.url, price=link.price)
                    for link in created.marketplace_links
                ],
                is_published=created.is_published,
                created_at=created.created_at,
                updated_at=created.updated_at,
            )
