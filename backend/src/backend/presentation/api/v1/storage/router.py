from fastapi import APIRouter, status

from src.backend.application.storage.dtos.get_presigned_urls import GetPresignedUrlsCommand
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.storage.dependencies import GetPresignedUrlsDep
from src.backend.presentation.api.v1.storage.schemas import PresignedUrlsRequest, PresignedUrlsResponse

router = APIRouter(
    prefix="/storage",
    tags=["storage"],
    responses={
        400: {"model": ExceptionSchema},
    },
)


@router.post(
    "/presigned-urls",
    status_code=status.HTTP_200_OK,
    response_model=PresignedUrlsResponse,
)
async def get_presigned_urls(
    body: PresignedUrlsRequest,
    uc: GetPresignedUrlsDep,
) -> PresignedUrlsResponse:
    result = await uc.execute(
        GetPresignedUrlsCommand(keys=body.keys, expires_in=body.expires_in)
    )
    return PresignedUrlsResponse(urls=result.urls)
