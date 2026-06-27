from dataclasses import dataclass
from uuid import UUID

from src.backend.domain.item.value_objects.marketplace_link import MarketplaceLink
from src.backend.domain.shared.entity import BaseEntity
from src.backend.domain.shared.mixins import TimeActionMixin
from src.backend.domain.shared.value_objects.name.value_object import Name


@dataclass(eq=False)
class Item(BaseEntity, TimeActionMixin):
    name: Name
    short_description: str
    description: str
    category_id: UUID
    youtube_url: str | None
    marketplace_links: list[MarketplaceLink]
    is_published: bool = False
    view_count: int = 0

    @classmethod
    def create(
            cls,
            name: str,
            short_description: str,
            description: str,
            category_id: UUID,
            youtube_url: str | None,
            marketplace_links: list[MarketplaceLink],
    ) -> "Item":
        return cls(
            name=Name(name),
            short_description=short_description,
            description=description,
            category_id=category_id,
            youtube_url=youtube_url,
            marketplace_links=marketplace_links,
        )

    def change_name(self, name: str) -> None:
        self.name = Name(name)
        self.touch()

    def change_short_description(self, short_description: str) -> None:
        self.short_description = short_description
        self.touch()

    def change_description(self, description: str) -> None:
        self.description = description
        self.touch()

    def change_category_id(self, category_id: UUID) -> None:
        self.category_id = category_id
        self.touch()

    def change_youtube_url(self, youtube_url: str) -> None:
        self.youtube_url = youtube_url
        self.touch()

    def change_marketplace_links(self, marketplace_links: list[MarketplaceLink]) -> None:
        self.marketplace_links = marketplace_links
        self.touch()

    def change_is_published(self, is_published: bool) -> None:
        self.is_published = is_published
        self.touch()

    def increment_view_count(self) -> None:
        self.view_count += 1

    def set_view_count(self, count: int) -> None:
        if not isinstance(count, int) or isinstance(count, bool):
            raise ValueError(f"view_count must be an integer, got {type(count).__name__}")
        if count < 1:
            raise ValueError(f"view_count must be >= 1, got {count}")
        self.view_count = count
        self.touch()
