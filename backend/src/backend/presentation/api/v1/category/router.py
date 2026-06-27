from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from src.backend.application.category.dtos.create_category import CreateCategoryCommand
from src.backend.application.category.dtos.delete_category import DeleteCategoryCommand
from src.backend.application.category.dtos.list_categories import ListCategoriesCommand
from src.backend.application.category.dtos.update_category import UpdateCategoryCommand
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.category.dependencies import (
    CreateCategoryDep,
    CurrentCategoryDep,
    DeleteCategoryDep,
    ListCategoriesDep,
    UpdateCategoryDep,
)
from src.backend.presentation.api.v1.category.schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


@router.get("", status_code=status.HTTP_200_OK, response_model=list[CategoryResponse])
async def list_categories(uc: ListCategoriesDep) -> list[CategoryResponse]:
    result = await uc.execute(ListCategoriesCommand())
    return [
        CategoryResponse(
            id=c.id,
            name=c.name,
            slug=c.slug,
            description=c.description,
            image_url=c.image_url,
            created_at=c.created_at,
        )
        for c in result.items
    ]


@router.get("/{category_id}", status_code=status.HTTP_200_OK, response_model=CategoryResponse)
async def get_category(category: CurrentCategoryDep) -> CategoryResponse:
    return CategoryResponse.from_entity(category)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CategoryResponse)
async def create_category(
    body: CreateCategoryRequest,
    uc: CreateCategoryDep,
    _: AdminUserDep,
) -> CategoryResponse:
    result = await uc.execute(
        CreateCategoryCommand(
            name=body.name,
            slug=body.slug,
            description=body.description,
            image_url=body.image_url,
        )
    )
    return CategoryResponse(
        id=result.id,
        name=result.name,
        slug=result.slug,
        description=result.description,
        image_url=result.image_url,
        created_at=result.created_at,
    )


@router.patch("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_category(
    category_id: UUID,
    body: UpdateCategoryRequest,
    uc: UpdateCategoryDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(
        UpdateCategoryCommand(
            category_id=category_id,
            name=body.name,
            description=body.description,
            image_url=body.image_url,
        )
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    uc: DeleteCategoryDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(DeleteCategoryCommand(category_id=category_id))
