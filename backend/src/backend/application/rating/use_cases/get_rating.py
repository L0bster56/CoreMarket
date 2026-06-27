from dataclasses import dataclass

from src.backend.application.rating.dtos.get_rating import GetRatingCommand, GetRatingResult
from src.backend.application.shared.interfaces.uow import UnitOfWork


@dataclass
class GetRatingUseCase:
    """
    UseCase: получение среднего рейтинга объекта.

    Ответственность:
        - Вычисление среднего балла по всем оценкам объекта
        - Подсчёт количества оценок
    """

    uow: UnitOfWork

    async def execute(self, cmd: GetRatingCommand) -> GetRatingResult:
        """
        Args:
            cmd (GetRatingCommand): ID объекта

        Returns:
            GetRatingResult: средний балл (None если нет оценок) и количество голосов
        """
        async with self.uow:
            avg = await self.uow.ratings.get_avg_by_item(cmd.item_id)
            count = await self.uow.ratings.count_by_item(cmd.item_id)
            return GetRatingResult(
                item_id=cmd.item_id,
                avg_score=avg,
                count=count,
            )
