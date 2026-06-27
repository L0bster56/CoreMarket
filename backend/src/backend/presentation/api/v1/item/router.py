from uuid import UUID

from fastapi import APIRouter, Query, status

from src.backend.application.item.dtos.add_characteristic import AddCharacteristicCommand
from src.backend.application.item.dtos.add_gallery_image import AddGalleryImageCommand
from src.backend.application.item.dtos.add_item_tag import AddItemTagCommand
from src.backend.application.item.dtos.create_item import CreateItemCommand, MarketplaceLinkData
from src.backend.application.item.dtos.delete_characteristic import DeleteCharacteristicCommand
from src.backend.application.item.dtos.delete_gallery_image import DeleteGalleryImageCommand
from src.backend.application.item.dtos.delete_item import DeleteItemCommand
from src.backend.application.item.dtos.get_item import GetItemCommand
from src.backend.application.item.dtos.list_items import ListItemsCommand, ListItemsFilters
from src.backend.application.item.dtos.remove_item_tag import RemoveItemTagCommand
from src.backend.application.item.dtos.update_characteristic import UpdateCharacteristicCommand
from src.backend.application.item.dtos.update_item import UpdateItemCommand
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.item.dependencies import (
    AddCharacteristicDep,
    AddGalleryImageDep,
    AddItemTagDep,
    CreateItemDep,
    DeleteCharacteristicDep,
    DeleteGalleryImageDep,
    DeleteItemDep,
    GetItemDep,
    ListItemsDep,
    RemoveItemTagDep,
    UpdateCharacteristicDep,
    UpdateItemDep,
)
from src.backend.presentation.api.v1.item.schemas import (
    AddCharacteristicRequest,
    AddGalleryImageRequest,
    AddTagRequest,
    CharacteristicSchema,
    CreateItemRequest,
    GalleryImageSchema,
    ItemListEntry,
    ItemListResponse,
    ItemResponse,
    MarketplaceLinkSchema,
    UpdateCharacteristicRequest,
    UpdateItemRequest,
)

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


def _dispatch_index(item_id: str) -> None:
    try:
        from src.backend.config import get_settings
        if not get_settings().SEARCH_ENABLED:
            return
        from src.backend.application.tasks.search_sync import index_item_task
        index_item_task.delay(item_id)
    except Exception:
        pass


def _dispatch_delete(item_id: str) -> None:
    try:
        from src.backend.config import get_settings
        if not get_settings().SEARCH_ENABLED:
            return
        from src.backend.application.tasks.search_sync import delete_item_task
        delete_item_task.delay(item_id)
    except Exception:
        pass


@router.get("", status_code=status.HTTP_200_OK, response_model=ItemListResponse)
async def list_items(
    uc: ListItemsDep,
    search: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    tag: str | None = Query(default=None),
    min_rating: float | None = Query(default=None),
    is_published: bool | None = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
) -> ItemListResponse:
    result = await uc.execute(
        ListItemsCommand(
            filters=ListItemsFilters(
                search=search,
                category_id=category_id,
                tag=tag,
                min_rating=min_rating,
                is_published=is_published,
                limit=limit,
                offset=offset,
            )
        )
    )
    return ItemListResponse(
        items=[
            ItemListEntry(
                id=e.id,
                title=e.title,
                short_description=e.short_description,
                category_id=e.category_id,
                youtube_url=e.youtube_url,
                is_published=e.is_published,
                view_count=e.view_count,
                created_at=e.created_at,
                updated_at=e.updated_at,
                preview_image=e.preview_image,
            )
            for e in result.items
        ],
        total=result.total,
    )


@router.get("/zero_error")
async def zero_error() -> None:
    return 1 / 0  # type: ignore[return-value]


@router.get("/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemResponse)
async def get_item(item_id: UUID, uc: GetItemDep) -> ItemResponse:
    result = await uc.execute(GetItemCommand(item_id=item_id))
    return ItemResponse.from_result(result)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
async def create_item(
    body: CreateItemRequest,
    uc: CreateItemDep,
    _: AdminUserDep,
) -> ItemResponse:
    result = await uc.execute(
        CreateItemCommand(
            title=body.title,
            short_description=body.short_description,
            description=body.description,
            category_id=body.category_id,
            youtube_url=body.youtube_url,
            marketplace_links=[
                MarketplaceLinkData(name=m.name, url=m.url, price=m.price)
                for m in body.marketplace_links
            ],
        )
    )
    _dispatch_index(str(result.id))
    return ItemResponse(
        id=result.id,
        title=result.title,
        short_description=result.short_description,
        description=result.description,
        category_id=result.category_id,
        youtube_url=result.youtube_url,
        marketplace_links=[
            MarketplaceLinkSchema(name=m.name, url=m.url, price=m.price)
            for m in result.marketplace_links
        ],
        is_published=result.is_published,
        view_count=0,
        characteristics=[],
        gallery=[],
        tags=[],
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.patch("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_item(
    item_id: UUID,
    body: UpdateItemRequest,
    uc: UpdateItemDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(
        UpdateItemCommand(
            item_id=item_id,
            title=body.title,
            short_description=body.short_description,
            description=body.description,
            category_id=body.category_id,
            youtube_url=body.youtube_url,
            marketplace_links=[
                MarketplaceLinkData(name=m.name, url=m.url, price=m.price)
                for m in body.marketplace_links
            ] if body.marketplace_links is not None else None,
            is_published=body.is_published,
            view_count=body.view_count,
        )
    )
    _dispatch_index(str(item_id))


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: UUID, uc: DeleteItemDep, _: AdminUserDep) -> None:
    await uc.execute(DeleteItemCommand(item_id=item_id))
    _dispatch_delete(str(item_id))


@router.post("/{item_id}/tags", status_code=status.HTTP_204_NO_CONTENT)
async def add_item_tag(
    item_id: UUID,
    body: AddTagRequest,
    uc: AddItemTagDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(AddItemTagCommand(item_id=item_id, tag_id=body.tag_id))
    _dispatch_index(str(item_id))


@router.delete("/{item_id}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_tag(
    item_id: UUID,
    tag_id: UUID,
    uc: RemoveItemTagDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(RemoveItemTagCommand(item_id=item_id, tag_id=tag_id))
    _dispatch_index(str(item_id))


@router.post(
    "/{item_id}/characteristics",
    status_code=status.HTTP_201_CREATED,
    response_model=CharacteristicSchema,
)
async def add_characteristic(
    item_id: UUID,
    body: AddCharacteristicRequest,
    uc: AddCharacteristicDep,
    _: AdminUserDep,
) -> CharacteristicSchema:
    result = await uc.execute(
        AddCharacteristicCommand(item_id=item_id, name=body.name, value=body.value, group=body.group)
    )
    _dispatch_index(str(item_id))
    return CharacteristicSchema(id=result.id, group=result.group, name=result.name, value=result.value)


@router.patch("/{item_id}/characteristics/{char_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_characteristic(
    item_id: UUID,
    char_id: UUID,
    body: UpdateCharacteristicRequest,
    uc: UpdateCharacteristicDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(
        UpdateCharacteristicCommand(
            characteristic_id=char_id,
            name=body.name,
            value=body.value,
            group=body.group,
        )
    )
    _dispatch_index(str(item_id))


@router.delete("/{item_id}/characteristics/{char_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_characteristic(
    item_id: UUID,
    char_id: UUID,
    uc: DeleteCharacteristicDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(DeleteCharacteristicCommand(characteristic_id=char_id))
    _dispatch_index(str(item_id))


@router.post(
    "/{item_id}/gallery",
    status_code=status.HTTP_201_CREATED,
    response_model=GalleryImageSchema,
)
async def add_gallery_image(
    item_id: UUID,
    body: AddGalleryImageRequest,
    uc: AddGalleryImageDep,
    _: AdminUserDep,
) -> GalleryImageSchema:
    result = await uc.execute(
        AddGalleryImageCommand(item_id=item_id, image_url=body.image_url)
    )
    _dispatch_index(str(item_id))
    return GalleryImageSchema(id=result.id, image_url=result.image_url)


@router.delete("/{item_id}/gallery/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gallery_image(
    item_id: UUID,
    image_id: UUID,
    uc: DeleteGalleryImageDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(DeleteGalleryImageCommand(gallery_id=image_id))
    _dispatch_index(str(item_id))


@router.get(
    "/zero_error"
)
async def zero_error():
    return 1 / 0