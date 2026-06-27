from dataclasses import dataclass

from src.backend.application.item.dtos.get_item import MarketplaceLinkItem
from src.backend.application.item.dtos.list_items import (
    ItemListEntry,
    ListItemsCommand,
    ListItemsResult,
)
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class ListItemsUseCase:
    """
    UseCase: получение списка объектов с фильтрацией и пагинацией.

    Ответственность:
        - Применение фильтров: поиск, категория, тег, минимальный рейтинг, статус публикации
        - Пагинация через limit/offset
        - Возврат общего количества для построения пагинации на фронте
    """

    uow: UnitOfWork

    async def execute(self, cmd: ListItemsCommand) -> ListItemsResult:
        """
        Args:
            cmd (ListItemsCommand): фильтры и параметры пагинации

        Returns:
            ListItemsResult: страница объектов и общее количество
        """
        async with self.uow:
            items = await self.uow.items.list(cmd.filters)
            total = await self.uow.items.count(cmd.filters)
            preview_keys = await self.uow.gallery.get_preview_keys([item.id for item in items])
            return ListItemsResult(
                items=[
                    ItemListEntry(
                        id=item.id,
                        title=str(item.name),
                        short_description=item.short_description,
                        category_id=item.category_id,
                        youtube_url=item.youtube_url,
                        is_published=item.is_published,
                        view_count=item.view_count,
                        created_at=item.created_at,
                        updated_at=item.updated_at,
                        preview_image=preview_keys.get(item.id),
                    )
                    for item in items
                ],
                total=total,
            )
