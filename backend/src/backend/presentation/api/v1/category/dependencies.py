from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.application.category.use_cases.create_category import CreateCategoryUseCase
from src.backend.application.category.use_cases.delete_category import DeleteCategoryUseCase
from src.backend.application.category.use_cases.list_categories import ListCategoriesUseCase
from src.backend.application.category.use_cases.update_category import UpdateCategoryUseCase
from src.backend.domain.category.entity import Category
from src.backend.infrastructure.db.sqlalchemy.category.repository import SqlAlchemyCategoryRepository
from src.backend.presentation.api.v1.core.dependencies import UoWDep, get_db


async def get_category_repo(session: AsyncSession = Depends(get_db)) -> SqlAlchemyCategoryRepository:
    return SqlAlchemyCategoryRepository(session=session)


CategoryRepoDep = Annotated[SqlAlchemyCategoryRepository, Depends(get_category_repo)]


async def get_current_category(category_id: UUID, repo: CategoryRepoDep) -> Category:
    category = await repo.get_by_id(category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


CurrentCategoryDep = Annotated[Category, Depends(get_current_category)]


def get_list_categories_use_case(uow: UoWDep) -> ListCategoriesUseCase:
    return ListCategoriesUseCase(uow=uow)


ListCategoriesDep = Annotated[ListCategoriesUseCase, Depends(get_list_categories_use_case)]


def get_create_category_use_case(uow: UoWDep) -> CreateCategoryUseCase:
    return CreateCategoryUseCase(uow=uow)


CreateCategoryDep = Annotated[CreateCategoryUseCase, Depends(get_create_category_use_case)]


def get_update_category_use_case(uow: UoWDep) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(uow=uow)


UpdateCategoryDep = Annotated[UpdateCategoryUseCase, Depends(get_update_category_use_case)]


def get_delete_category_use_case(uow: UoWDep) -> DeleteCategoryUseCase:
    return DeleteCategoryUseCase(uow=uow)


DeleteCategoryDep = Annotated[DeleteCategoryUseCase, Depends(get_delete_category_use_case)]
