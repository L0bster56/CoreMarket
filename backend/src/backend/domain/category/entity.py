from dataclasses import dataclass

from src.backend.domain.category.value_objects.slug.value_object import Slug
from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.mixins import TimeActionMixin
from src.backend.domain.shared.value_objects.name.value_object import Name


@dataclass(eq=False)
class Category(BaseEntity, TimeActionMixin):
    name: Name
    slug: Slug
    description: str | None
    image_url: str | None

    @classmethod
    def create(
            cls,
            name: str,
            slug: str,
            description: str | None = None,
            image_url: str | None = None,
    ) -> "Category":
        return cls(name=Name(name), slug=Slug(slug), description=description, image_url=image_url)

    def change_name(self, name: str) -> None:
        self.name = Name(name)
        self.touch()

    def change_description(self, description: str) -> None:
        self.description = description
        self.touch()

    def change_image_url(self, image_url: str) -> None:
        self.image_url = image_url
        self.touch()
