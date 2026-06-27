from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteGalleryImageCommand:
    gallery_id: UUID
