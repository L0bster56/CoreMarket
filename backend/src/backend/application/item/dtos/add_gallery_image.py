from dataclasses import dataclass
from uuid import UUID


@dataclass
class AddGalleryImageCommand:
    item_id: UUID
    image_url: str


@dataclass
class AddGalleryImageResult:
    id: UUID
    item_id: UUID
    image_url: str
