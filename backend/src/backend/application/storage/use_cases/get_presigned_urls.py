from dataclasses import dataclass

from src.backend.application.shared.errors import BadRequestError
from src.backend.application.storage.dtos.get_presigned_urls import (
    GetPresignedUrlsCommand,
    GetPresignedUrlsResult,
)
from src.backend.application.upload.interfaces.storage import FileStorage

_MAX_KEYS = 100


@dataclass
class GetPresignedUrlsUseCase:
    storage: FileStorage

    async def execute(self, cmd: GetPresignedUrlsCommand) -> GetPresignedUrlsResult:
        if len(cmd.keys) > _MAX_KEYS:
            raise BadRequestError(f"Too many keys: max {_MAX_KEYS} per request")

        urls = await self.storage.get_presigned_urls(cmd.keys, cmd.expires_in)
        return GetPresignedUrlsResult(urls=urls)
