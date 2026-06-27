from pydantic import BaseModel


class ExceptionSchema(BaseModel):
    detail: str | dict
    status_code: int
