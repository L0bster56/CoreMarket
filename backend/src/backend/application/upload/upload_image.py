from dataclasses import dataclass

from src.backend.application.shared.errors import BadRequestError
from src.backend.application.upload.interfaces.storage import FileStorage

_MIME_ALIASES = {"image/jpg": "image/jpeg"}
_ALLOWED_MIMES = frozenset({"image/jpeg", "image/png", "image/webp"})
_MAX_SIZE = 5 * 1024 * 1024
_MIME_TO_EXT = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@dataclass
class UploadImageCommand:
    data: bytes
    content_type: str
    section: str


@dataclass
class UploadImageUseCase:
    storage: FileStorage

    async def execute(self, cmd: UploadImageCommand) -> str:
        content_type = _MIME_ALIASES.get(cmd.content_type, cmd.content_type)
        if content_type not in _ALLOWED_MIMES:
            raise BadRequestError(f"Unsupported media type: {cmd.content_type}")
        if len(cmd.data) > _MAX_SIZE:
            raise BadRequestError("File size exceeds 5MB limit")
        ext = _MIME_TO_EXT[content_type]
        return await self.storage.save(cmd.data, cmd.section, ext)
