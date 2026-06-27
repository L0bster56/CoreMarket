from dataclasses import dataclass

from src.backend.application.item.dtos.get_item import (
    CharacteristicItem,
    GalleryItem,
    GetItemCommand,
    GetItemResult,
    MarketplaceLinkItem,
    TagItem,
)
from src.backend.application.item.errors import ItemNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class GetItemUseCase:
    """
    UseCase: получение полной карточки объекта.

    Ответственность:
        - Проверка существования объекта
        - Загрузка характеристик, галереи и тегов
        - Сборка полного ответа
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetItemCommand) -> GetItemResult:
        """
        Args:
            cmd (GetItemCommand): ID объекта

        Returns:
            GetItemResult: полная карточка с характеристиками, галереей и тегами

        Raises:
            ItemNotFoundError: если объект не найден
        """
        async with self.uow:
            item = await self.uow.items.get_by_id(cmd.item_id)
            if item is None:
                raise ItemNotFoundError("item not found")

            await self.uow.items.increment_view_count(cmd.item_id)
            await self.uow.commit()

            characteristics = await self.uow.characteristics.list_by_item(cmd.item_id)
            gallery = await self.uow.gallery.list_by_item(cmd.item_id)
            tags = await self.uow.items.get_tags(cmd.item_id)

            return GetItemResult(
                id=item.id,
                title=str(item.name),
                short_description=item.short_description,
                description=item.description,
                category_id=item.category_id,
                youtube_url=item.youtube_url,
                marketplace_links=[
                    MarketplaceLinkItem(name=str(link.name), url=link.url, price=link.price)
                    for link in item.marketplace_links
                ],
                is_published=item.is_published,
                view_count=item.view_count + 1,
                characteristics=[
                    CharacteristicItem(id=c.id, name=c.name, value=c.value, group=c.group)
                    for c in characteristics
                ],
                gallery=[
                    GalleryItem(id=g.id, image_url=g.image_url)
                    for g in gallery
                ],
                tags=[
                    TagItem(id=t.id, name=str(t.name), slug=str(t.slug))
                    for t in tags
                ],
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
