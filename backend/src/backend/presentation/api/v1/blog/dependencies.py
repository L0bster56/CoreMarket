from typing import Annotated

from fastapi import Depends

from src.backend.application.blog.use_cases.add_blog_post_tag import AddBlogPostTagUseCase
from src.backend.application.blog.use_cases.archive_blog_post import ArchiveBlogPostUseCase
from src.backend.application.blog.use_cases.create_blog_post import CreateBlogPostUseCase
from src.backend.application.blog.use_cases.create_blog_tag import CreateBlogTagUseCase
from src.backend.application.blog.use_cases.delete_blog_post import DeleteBlogPostUseCase
from src.backend.application.blog.use_cases.delete_blog_tag import DeleteBlogTagUseCase
from src.backend.application.blog.use_cases.get_blog_post import GetBlogPostUseCase
from src.backend.application.blog.use_cases.link_product import LinkProductUseCase, UnlinkProductUseCase
from src.backend.application.blog.use_cases.list_blog_posts import ListBlogPostsUseCase
from src.backend.application.blog.use_cases.list_blog_tags import ListBlogTagsUseCase
from src.backend.application.blog.use_cases.publish_blog_post import PublishBlogPostUseCase
from src.backend.application.blog.use_cases.remove_blog_post_tag import RemoveBlogPostTagUseCase
from src.backend.application.blog.use_cases.unpublish_blog_post import UnpublishBlogPostUseCase
from src.backend.application.blog.use_cases.update_blog_post import UpdateBlogPostUseCase
from src.backend.application.blog.use_cases.update_blog_tag import UpdateBlogTagUseCase
from src.backend.infrastructure.markdown.mistune_renderer import MistureRenderer
from src.backend.presentation.api.v1.core.dependencies import UoWDep


def get_markdown_renderer() -> MistureRenderer:
    return MistureRenderer()


MarkdownRendererDep = Annotated[MistureRenderer, Depends(get_markdown_renderer)]


def get_list_blog_posts_uc(uow: UoWDep) -> ListBlogPostsUseCase:
    return ListBlogPostsUseCase(uow=uow)


ListBlogPostsDep = Annotated[ListBlogPostsUseCase, Depends(get_list_blog_posts_uc)]


def get_get_blog_post_uc(uow: UoWDep, renderer: MarkdownRendererDep) -> GetBlogPostUseCase:
    return GetBlogPostUseCase(uow=uow, renderer=renderer)


GetBlogPostDep = Annotated[GetBlogPostUseCase, Depends(get_get_blog_post_uc)]


def get_create_blog_post_uc(uow: UoWDep) -> CreateBlogPostUseCase:
    return CreateBlogPostUseCase(uow=uow)


CreateBlogPostDep = Annotated[CreateBlogPostUseCase, Depends(get_create_blog_post_uc)]


def get_update_blog_post_uc(uow: UoWDep) -> UpdateBlogPostUseCase:
    return UpdateBlogPostUseCase(uow=uow)


UpdateBlogPostDep = Annotated[UpdateBlogPostUseCase, Depends(get_update_blog_post_uc)]


def get_delete_blog_post_uc(uow: UoWDep) -> DeleteBlogPostUseCase:
    return DeleteBlogPostUseCase(uow=uow)


DeleteBlogPostDep = Annotated[DeleteBlogPostUseCase, Depends(get_delete_blog_post_uc)]


def get_publish_blog_post_uc(uow: UoWDep) -> PublishBlogPostUseCase:
    return PublishBlogPostUseCase(uow=uow)


PublishBlogPostDep = Annotated[PublishBlogPostUseCase, Depends(get_publish_blog_post_uc)]


def get_unpublish_blog_post_uc(uow: UoWDep) -> UnpublishBlogPostUseCase:
    return UnpublishBlogPostUseCase(uow=uow)


UnpublishBlogPostDep = Annotated[UnpublishBlogPostUseCase, Depends(get_unpublish_blog_post_uc)]


def get_archive_blog_post_uc(uow: UoWDep) -> ArchiveBlogPostUseCase:
    return ArchiveBlogPostUseCase(uow=uow)


ArchiveBlogPostDep = Annotated[ArchiveBlogPostUseCase, Depends(get_archive_blog_post_uc)]


def get_add_blog_post_tag_uc(uow: UoWDep) -> AddBlogPostTagUseCase:
    return AddBlogPostTagUseCase(uow=uow)


AddBlogPostTagDep = Annotated[AddBlogPostTagUseCase, Depends(get_add_blog_post_tag_uc)]


def get_remove_blog_post_tag_uc(uow: UoWDep) -> RemoveBlogPostTagUseCase:
    return RemoveBlogPostTagUseCase(uow=uow)


RemoveBlogPostTagDep = Annotated[RemoveBlogPostTagUseCase, Depends(get_remove_blog_post_tag_uc)]


def get_link_product_uc(uow: UoWDep) -> LinkProductUseCase:
    return LinkProductUseCase(uow=uow)


LinkProductDep = Annotated[LinkProductUseCase, Depends(get_link_product_uc)]


def get_unlink_product_uc(uow: UoWDep) -> UnlinkProductUseCase:
    return UnlinkProductUseCase(uow=uow)


UnlinkProductDep = Annotated[UnlinkProductUseCase, Depends(get_unlink_product_uc)]


def get_list_blog_tags_uc(uow: UoWDep) -> ListBlogTagsUseCase:
    return ListBlogTagsUseCase(uow=uow)


ListBlogTagsDep = Annotated[ListBlogTagsUseCase, Depends(get_list_blog_tags_uc)]


def get_create_blog_tag_uc(uow: UoWDep) -> CreateBlogTagUseCase:
    return CreateBlogTagUseCase(uow=uow)


CreateBlogTagDep = Annotated[CreateBlogTagUseCase, Depends(get_create_blog_tag_uc)]


def get_update_blog_tag_uc(uow: UoWDep) -> UpdateBlogTagUseCase:
    return UpdateBlogTagUseCase(uow=uow)


UpdateBlogTagDep = Annotated[UpdateBlogTagUseCase, Depends(get_update_blog_tag_uc)]


def get_delete_blog_tag_uc(uow: UoWDep) -> DeleteBlogTagUseCase:
    return DeleteBlogTagUseCase(uow=uow)


DeleteBlogTagDep = Annotated[DeleteBlogTagUseCase, Depends(get_delete_blog_tag_uc)]
