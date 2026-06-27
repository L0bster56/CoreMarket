from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.backend.domain.category.entity import Category


class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    image_url: str | None
    created_at: datetime

    @classmethod
    def from_entity(cls, category: Category) -> "CategoryResponse":
        return cls(
            id=category.id,
            name=str(category.name),
            slug=str(category.slug),
            description=category.description,
            image_url=category.image_url,
            created_at=category.created_at,
        )


class CreateCategoryRequest(BaseModel):
    name: str
    slug: str
    description: str | None = None
    image_url: str | None = None


class UpdateCategoryRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
