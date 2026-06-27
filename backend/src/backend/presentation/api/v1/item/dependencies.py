from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.application.item.use_cases.add_characteristic import AddCharacteristicUseCase
from src.backend.application.item.use_cases.add_gallery_image import AddGalleryImageUseCase
from src.backend.application.item.use_cases.add_item_tag import AddItemTagUseCase
from src.backend.application.item.use_cases.create_item import CreateItemUseCase
from src.backend.application.item.use_cases.delete_characteristic import DeleteCharacteristicUseCase
from src.backend.application.item.use_cases.delete_gallery_image import DeleteGalleryImageUseCase
from src.backend.application.item.use_cases.delete_item import DeleteItemUseCase
from src.backend.application.item.use_cases.get_item import GetItemUseCase
from src.backend.application.item.use_cases.list_items import ListItemsUseCase
from src.backend.application.item.use_cases.remove_item_tag import RemoveItemTagUseCase
from src.backend.application.item.use_cases.update_characteristic import UpdateCharacteristicUseCase
from src.backend.application.item.use_cases.update_item import UpdateItemUseCase
from src.backend.domain.item.entity import Item
from src.backend.infrastructure.db.sqlalchemy.item.repository import SqlAlchemyItemRepository
from src.backend.presentation.api.v1.auth.dependencies import CurrentUserDep
from src.backend.presentation.api.v1.core.dependencies import UoWDep, get_db


async def get_item_repo(session: AsyncSession = Depends(get_db)) -> SqlAlchemyItemRepository:
    return SqlAlchemyItemRepository(session=session)


ItemRepoDep = Annotated[SqlAlchemyItemRepository, Depends(get_item_repo)]


async def get_current_item(item_id: UUID, repo: ItemRepoDep) -> Item:
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


CurrentItemDep = Annotated[Item, Depends(get_current_item)]


def get_list_items_use_case(uow: UoWDep) -> ListItemsUseCase:
    return ListItemsUseCase(uow=uow)


ListItemsDep = Annotated[ListItemsUseCase, Depends(get_list_items_use_case)]


def get_get_item_use_case(uow: UoWDep) -> GetItemUseCase:
    return GetItemUseCase(uow=uow)


GetItemDep = Annotated[GetItemUseCase, Depends(get_get_item_use_case)]


def get_create_item_use_case(uow: UoWDep, user: CurrentUserDep) -> CreateItemUseCase:
    return CreateItemUseCase(uow=uow, user=user)


CreateItemDep = Annotated[CreateItemUseCase, Depends(get_create_item_use_case)]


def get_update_item_use_case(uow: UoWDep, user: CurrentUserDep) -> UpdateItemUseCase:
    return UpdateItemUseCase(uow=uow, user=user)


UpdateItemDep = Annotated[UpdateItemUseCase, Depends(get_update_item_use_case)]


def get_delete_item_use_case(uow: UoWDep, user: CurrentUserDep) -> DeleteItemUseCase:
    return DeleteItemUseCase(uow=uow, user=user)


DeleteItemDep = Annotated[DeleteItemUseCase, Depends(get_delete_item_use_case)]


def get_add_item_tag_use_case(uow: UoWDep, user: CurrentUserDep) -> AddItemTagUseCase:
    return AddItemTagUseCase(uow=uow, user=user)


AddItemTagDep = Annotated[AddItemTagUseCase, Depends(get_add_item_tag_use_case)]


def get_remove_item_tag_use_case(uow: UoWDep, user: CurrentUserDep) -> RemoveItemTagUseCase:
    return RemoveItemTagUseCase(uow=uow, user=user)


RemoveItemTagDep = Annotated[RemoveItemTagUseCase, Depends(get_remove_item_tag_use_case)]


def get_add_characteristic_use_case(uow: UoWDep, user: CurrentUserDep) -> AddCharacteristicUseCase:
    return AddCharacteristicUseCase(uow=uow, user=user)


AddCharacteristicDep = Annotated[AddCharacteristicUseCase, Depends(get_add_characteristic_use_case)]


def get_update_characteristic_use_case(uow: UoWDep, user: CurrentUserDep) -> UpdateCharacteristicUseCase:
    return UpdateCharacteristicUseCase(uow=uow, user=user)


UpdateCharacteristicDep = Annotated[UpdateCharacteristicUseCase, Depends(get_update_characteristic_use_case)]


def get_delete_characteristic_use_case(uow: UoWDep, user: CurrentUserDep) -> DeleteCharacteristicUseCase:
    return DeleteCharacteristicUseCase(uow=uow, user=user)


DeleteCharacteristicDep = Annotated[DeleteCharacteristicUseCase, Depends(get_delete_characteristic_use_case)]


def get_add_gallery_image_use_case(uow: UoWDep, user: CurrentUserDep) -> AddGalleryImageUseCase:
    return AddGalleryImageUseCase(uow=uow, user=user)


AddGalleryImageDep = Annotated[AddGalleryImageUseCase, Depends(get_add_gallery_image_use_case)]


def get_delete_gallery_image_use_case(uow: UoWDep, user: CurrentUserDep) -> DeleteGalleryImageUseCase:
    return DeleteGalleryImageUseCase(uow=uow, user=user)


DeleteGalleryImageDep = Annotated[DeleteGalleryImageUseCase, Depends(get_delete_gallery_image_use_case)]
