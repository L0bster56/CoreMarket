from dataclasses import dataclass

from src.backend.domain.shared.value_objects.name.value_object import Name


@dataclass(frozen=True)
class MarketplaceLink:
    name: Name
    url: str
    price: str | None

