from dataclasses import dataclass

from src.backend.application.category.dtos.delete_category import DeleteCategoryCommand
from src.backend.application.category.errors import CategoryNotFoundError
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class DeleteCategoryUseCase:
    """
    UseCase: удаление категории.

    Ответственность:
        - Проверка существования категории
        - Удаление категории из базы данных
    """

    uow: UnitOfWork

    async def execute(self, cmd: DeleteCategoryCommand) -> None:
        """
        Удаляет категорию по ID.

        Args:
            cmd (DeleteCategoryCommand): идентификатор категории

        Raises:
            CategoryNotFoundError: если категория не найдена
        """
        async with self.uow:
            category = await self.uow.categories.get_by_id(cmd.category_id)

            if category is None:
                raise CategoryNotFoundError("category not found")

            await self.uow.categories.delete(category)
            await self.uow.commit()
