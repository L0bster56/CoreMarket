from dataclasses import dataclass

from src.backend.application.category.dtos.list_categories import (
    ListCategoriesCommand,
    ListCategoriesResult,
    CategoryItem,
)
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class ListCategoriesUseCase:
    """
    UseCase: получение списка всех категорий.

    Ответственность:
        - Возврат всех категорий из базы данных
    """

    uow: UnitOfWork

    async def execute(self, cmd: ListCategoriesCommand) -> ListCategoriesResult:
        """
        Возвращает список всех категорий.

        Args:
            cmd (ListCategoriesCommand): команда без параметров

        Returns:
            ListCategoriesResult: список категорий
        """
        async with self.uow:
            all_categories = await self.uow.categories.list_all()
            return ListCategoriesResult(
                items=[
                    CategoryItem(
                        id=c.id,
                        name=str(c.name),
                        slug=str(c.slug),
                        description=c.description,
                        image_url=c.image_url,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                    )
                    for c in all_categories
                ]
            )
