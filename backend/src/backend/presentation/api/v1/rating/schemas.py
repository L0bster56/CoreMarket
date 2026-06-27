from pydantic import BaseModel, Field


class RatingResponse(BaseModel):
    average: float | None
    count: int
    user_score: int | None


class CreateRatingRequest(BaseModel):
    score: int = Field(ge=1, le=5)


class UpdateRatingRequest(BaseModel):
    score: int = Field(ge=1, le=5)
