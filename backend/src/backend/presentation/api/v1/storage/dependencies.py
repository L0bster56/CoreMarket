from typing import Annotated

from fastapi import Depends

from src.backend.application.storage.use_cases.get_presigned_urls import GetPresignedUrlsUseCase
from src.backend.infrastructure.storage.minio.storage import MinIOFileStorage


def get_presigned_urls_uc() -> GetPresignedUrlsUseCase:
    return GetPresignedUrlsUseCase(storage=MinIOFileStorage())


GetPresignedUrlsDep = Annotated[GetPresignedUrlsUseCase, Depends(get_presigned_urls_uc)]
