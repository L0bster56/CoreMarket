from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, status

from src.backend.application.tag.dtos.create_tag import CreateTagCommand
from src.backend.application.tag.dtos.delete_tag import DeleteTagCommand
from src.backend.application.tag.dtos.list_tags import ListTagsCommand
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.tag.dependencies import CreateTagDep, DeleteTagDep, ListTagsDep
from src.backend.presentation.api.v1.tag.schemas import CreateTagRequest, TagResponse

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


@router.get("", status_code=status.HTTP_200_OK, response_model=list[TagResponse])
async def list_tags(uc: ListTagsDep) -> list[TagResponse]:
    result = await uc.execute(ListTagsCommand())
    return [TagResponse(id=t.id, name=t.name, slug=t.slug) for t in result.items]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TagResponse)
async def create_tag(
    body: CreateTagRequest,
    uc: CreateTagDep,
    _: AdminUserDep,
) -> TagResponse:
    result = await uc.execute(CreateTagCommand(name=body.name, slug=body.slug))
    return TagResponse(id=result.id, name=result.name, slug=result.slug)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: UUID, uc: DeleteTagDep, _: AdminUserDep) -> None:
    await uc.execute(DeleteTagCommand(tag_id=tag_id))
