from dataclasses import dataclass

from src.backend.application.item.dtos.delete_gallery_image import DeleteGalleryImageCommand
from src.backend.application.item.errors import GalleryImageNotFoundError, ItemEditForbiddenError
from src.backend.application.shared.interfaces.uow import UnitOfWork
from src.backend.domain.user.entity import User, UserRole


@dataclass
class DeleteGalleryImageUseCase:
    uow: UnitOfWork
    user: User

    async def execute(self, cmd: DeleteGalleryImageCommand) -> None:
        if self.user.role != UserRole.admin:
            raise ItemEditForbiddenError("only admin can manage gallery")

        async with self.uow:
            image = await self.uow.gallery.get_by_id(cmd.gallery_id)
            if image is None:
                raise GalleryImageNotFoundError("gallery image not found")

            await self.uow.gallery.delete(image)
            await self.uow.commit()
