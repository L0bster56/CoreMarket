from pydantic import BaseModel, Field


class PresignedUrlsRequest(BaseModel):
    keys: list[str] = Field(..., max_length=100)
    expires_in: int = Field(default=3600, ge=60, le=86400)


class PresignedUrlsResponse(BaseModel):
    urls: dict[str, str]
