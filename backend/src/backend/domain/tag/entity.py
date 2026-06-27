from dataclasses import dataclass

from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.value_objects.name.value_object import Name


@dataclass(eq=False)
class Tag(BaseEntity):
    name: Name
    slug: Slug

    @classmethod
    def create(cls, name: str, slug: "str | Slug") -> "Tag":
        return cls(name=Name(name), slug=slug if isinstance(slug, Slug) else Slug(slug))
