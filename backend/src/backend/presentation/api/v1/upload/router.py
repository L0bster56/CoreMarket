from fastapi import APIRouter, Query, UploadFile, status

from src.backend.application.upload.upload_image import UploadImageCommand, UploadImageUseCase
from src.backend.infrastructure.storage.minio.storage import MinIOFileStorage
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.upload.schemas import UploadResponse

_ALLOWED_SECTIONS = frozenset({"items", "categories", "users"})

router = APIRouter(
    prefix="/upload",
    tags=["upload"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UploadResponse)
async def upload_image(
    file: UploadFile,
    _: AdminUserDep,
    section: str = Query(...),
) -> UploadResponse:
    if section not in _ALLOWED_SECTIONS:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"section must be one of: {', '.join(sorted(_ALLOWED_SECTIONS))}",
        )
    data = await file.read()
    uc = UploadImageUseCase(storage=MinIOFileStorage())
    key = await uc.execute(
        UploadImageCommand(data=data, content_type=file.content_type or "", section=section)
    )

    from src.backend.application.tasks.images import generate_thumbnail
    generate_thumbnail.delay(key)

    return UploadResponse(key=key)
