from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.value_objects.name.value_object import Name
from src.backend.domain.tag.entity import Tag
from src.backend.infrastructure.db.sqlalchemy.tag.model import TagModel


def to_model(tag: Tag) -> TagModel:
    return TagModel(
        id=tag.id,
        name=str(tag.name),
        slug=str(tag.slug),
    )


def to_entity(model: TagModel) -> Tag:
    return Tag(
        id=model.id,
        name=Name(model.name),
        slug=Slug(model.slug),
    )
