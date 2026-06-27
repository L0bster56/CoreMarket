from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError

from src.backend.application.shared.errors import (
    BadRequestError,
    ConflictError,
    NotAuthorizedError,
    NotFoundError,
)


async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "status_code": status.HTTP_404_NOT_FOUND},
    )


async def conflict_exception_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "status_code": status.HTTP_409_CONFLICT},
    )


async def bad_request_exception_handler(request: Request, exc: BadRequestError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc), "status_code": status.HTTP_400_BAD_REQUEST},
    )


async def not_authorized_exception_handler(
    request: Request, exc: NotAuthorizedError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": str(exc), "status_code": status.HTTP_401_UNAUTHORIZED},
    )


async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid credentials", "status_code": status.HTTP_401_UNAUTHORIZED},
    )
