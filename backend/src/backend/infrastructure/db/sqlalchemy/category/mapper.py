from src.backend.domain.category.entity import Category
from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.value_objects.name.value_object import Name
from src.backend.infrastructure.db.sqlalchemy.category.model import CategoryModel


def to_model(category: Category) -> CategoryModel:
    return CategoryModel(
        id=category.id,
        name=str(category.name),
        slug=str(category.slug),
        description=category.description,
        image_url=category.image_url,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


def to_entity(model: CategoryModel) -> Category:
    return Category(
        id=model.id,
        name=Name(model.name),
        slug=Slug(model.slug),
        description=model.description,
        image_url=model.image_url,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
