from typing import Annotated

from fastapi import Depends

from src.backend.application.tag.use_cases.create_tag import CreateTagUseCase
from src.backend.application.tag.use_cases.delete_tag import DeleteTagUseCase
from src.backend.application.tag.use_cases.list_tags import ListTagsUseCase
from src.backend.presentation.api.v1.core.dependencies import UoWDep


def get_list_tags_use_case(uow: UoWDep) -> ListTagsUseCase:
    return ListTagsUseCase(uow=uow)


ListTagsDep = Annotated[ListTagsUseCase, Depends(get_list_tags_use_case)]


def get_create_tag_use_case(uow: UoWDep) -> CreateTagUseCase:
    return CreateTagUseCase(uow=uow)


CreateTagDep = Annotated[CreateTagUseCase, Depends(get_create_tag_use_case)]


def get_delete_tag_use_case(uow: UoWDep) -> DeleteTagUseCase:
    return DeleteTagUseCase(uow=uow)


DeleteTagDep = Annotated[DeleteTagUseCase, Depends(get_delete_tag_use_case)]
