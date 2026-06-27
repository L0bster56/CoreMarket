from uuid import UUID

from fastapi import APIRouter, Query, UploadFile, status

from src.backend.application.blog.dtos.add_blog_post_tag import AddBlogPostTagCommand, RemoveBlogPostTagCommand
from src.backend.application.blog.dtos.blog_tags import (
    CreateBlogTagCommand,
    DeleteBlogTagCommand,
    ListBlogTagsCommand,
    UpdateBlogTagCommand,
)
from src.backend.application.blog.dtos.create_blog_post import CreateBlogPostCommand
from src.backend.application.blog.dtos.delete_blog_post import DeleteBlogPostCommand
from src.backend.application.blog.dtos.get_blog_post import GetBlogPostCommand
from src.backend.application.blog.dtos.link_product import LinkProductCommand, UnlinkProductCommand
from src.backend.application.blog.dtos.list_blog_posts import ListBlogPostsCommand, ListBlogPostsFilters
from src.backend.application.blog.dtos.publish_blog_post import (
    ArchiveBlogPostCommand,
    PublishBlogPostCommand,
    UnpublishBlogPostCommand,
)
from src.backend.application.blog.dtos.update_blog_post import UpdateBlogPostCommand
from src.backend.application.upload.upload_image import UploadImageCommand, UploadImageUseCase
from src.backend.infrastructure.storage.minio.storage import MinIOFileStorage
from src.backend.presentation.api.v1.auth.dependencies import AdminUserDep
from src.backend.presentation.api.v1.blog.dependencies import (
    AddBlogPostTagDep,
    ArchiveBlogPostDep,
    CreateBlogPostDep,
    CreateBlogTagDep,
    DeleteBlogPostDep,
    DeleteBlogTagDep,
    GetBlogPostDep,
    LinkProductDep,
    ListBlogPostsDep,
    ListBlogTagsDep,
    PublishBlogPostDep,
    RemoveBlogPostTagDep,
    UnlinkProductDep,
    UnpublishBlogPostDep,
    UpdateBlogPostDep,
    UpdateBlogTagDep,
)
from src.backend.presentation.api.v1.blog.schemas import (
    AddTagRequest,
    BlogPostListEntry,
    BlogPostListResponse,
    BlogPostResponse,
    BlogProductLinkSchema,
    BlogTagSchema,
    CreateBlogPostRequest,
    CreateBlogTagRequest,
    LinkProductRequest,
    UpdateBlogPostRequest,
    UpdateBlogTagRequest,
)
from src.backend.presentation.api.v1.core.schemas import ExceptionSchema
from src.backend.presentation.api.v1.upload.schemas import UploadResponse

router = APIRouter(
    prefix="/blog",
    tags=["blog"],
    responses={
        401: {"model": ExceptionSchema},
        403: {"model": ExceptionSchema},
    },
)


# ── Posts ─────────────────────────────────────────────────────────────────────

@router.get("/posts", status_code=status.HTTP_200_OK, response_model=BlogPostListResponse)
async def list_blog_posts(
    uc: ListBlogPostsDep,
    search: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    tag_slug: str | None = Query(default=None),
    post_status: str | None = Query(default=None),
    limit: int = Query(default=20),
    offset: int = Query(default=0),
) -> BlogPostListResponse:
    result = await uc.execute(
        ListBlogPostsCommand(
            filters=ListBlogPostsFilters(
                search=search,
                category_id=category_id,
                tag_slug=tag_slug,
                status=post_status,
                limit=limit,
                offset=offset,
            )
        )
    )
    return BlogPostListResponse(
        items=[
            BlogPostListEntry(
                id=e.id,
                title=e.title,
                slug=e.slug,
                short_description=e.short_description,
                cover_image_url=e.cover_image_url,
                category_id=e.category_id,
                status=e.status,
                created_at=e.created_at,
                updated_at=e.updated_at,
            )
            for e in result.items
        ],
        total=result.total,
    )


@router.get("/posts/{slug}", status_code=status.HTTP_200_OK, response_model=BlogPostResponse)
async def get_blog_post(slug: str, uc: GetBlogPostDep) -> BlogPostResponse:
    result = await uc.execute(GetBlogPostCommand(slug=slug))
    return BlogPostResponse.from_result(result)


@router.post("/posts", status_code=status.HTTP_201_CREATED, response_model=BlogPostResponse)
async def create_blog_post(
    body: CreateBlogPostRequest,
    uc: CreateBlogPostDep,
    get_uc: GetBlogPostDep,
    _: AdminUserDep,
) -> BlogPostResponse:
    created = await uc.execute(
        CreateBlogPostCommand(
            title=body.title,
            slug=body.slug,
            short_description=body.short_description,
        )
    )
    result = await get_uc.execute(GetBlogPostCommand(slug=created.slug))
    return BlogPostResponse.from_result(result)


@router.patch("/posts/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog_post(
    slug: str,
    body: UpdateBlogPostRequest,
    uc: UpdateBlogPostDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(
        UpdateBlogPostCommand(
            slug=slug,
            title=body.title,
            new_slug=body.new_slug,
            short_description=body.short_description,
            content=body.content,
            cover_image_url=body.cover_image_url,
            category_id=body.category_id,
            seo_title=body.seo_title,
            seo_description=body.seo_description,
        )
    )


@router.delete("/posts/{slug}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(slug: str, uc: DeleteBlogPostDep, _: AdminUserDep) -> None:
    await uc.execute(DeleteBlogPostCommand(slug=slug))


@router.post("/posts/{slug}/publish", status_code=status.HTTP_204_NO_CONTENT)
async def publish_blog_post(slug: str, uc: PublishBlogPostDep, _: AdminUserDep) -> None:
    await uc.execute(PublishBlogPostCommand(slug=slug))


@router.post("/posts/{slug}/unpublish", status_code=status.HTTP_204_NO_CONTENT)
async def unpublish_blog_post(slug: str, uc: UnpublishBlogPostDep, _: AdminUserDep) -> None:
    await uc.execute(UnpublishBlogPostCommand(slug=slug))


@router.post("/posts/{slug}/archive", status_code=status.HTTP_204_NO_CONTENT)
async def archive_blog_post(slug: str, uc: ArchiveBlogPostDep, _: AdminUserDep) -> None:
    await uc.execute(ArchiveBlogPostCommand(slug=slug))


@router.post("/posts/{slug}/tags", status_code=status.HTTP_204_NO_CONTENT)
async def add_blog_post_tag(
    slug: str,
    body: AddTagRequest,
    uc: AddBlogPostTagDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(AddBlogPostTagCommand(slug=slug, tag_id=body.tag_id))


@router.delete("/posts/{slug}/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_blog_post_tag(
    slug: str,
    tag_id: UUID,
    uc: RemoveBlogPostTagDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(RemoveBlogPostTagCommand(slug=slug, tag_id=tag_id))


@router.post(
    "/posts/{slug}/products",
    status_code=status.HTTP_201_CREATED,
    response_model=BlogProductLinkSchema,
)
async def link_product(
    slug: str,
    body: LinkProductRequest,
    uc: LinkProductDep,
    _: AdminUserDep,
) -> BlogProductLinkSchema:
    result = await uc.execute(
        LinkProductCommand(slug=slug, product_id=body.product_id, display_order=body.display_order)
    )
    return BlogProductLinkSchema(id=result.id, product_id=result.product_id, display_order=result.display_order)


@router.delete("/posts/{slug}/products/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_product(
    slug: str,
    link_id: UUID,
    uc: UnlinkProductDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(UnlinkProductCommand(slug=slug, link_id=link_id))


@router.post(
    "/posts/{slug}/cover",
    status_code=status.HTTP_200_OK,
    response_model=UploadResponse,
)
async def upload_blog_cover(
    slug: str,
    file: UploadFile,
    update_uc: UpdateBlogPostDep,
    _: AdminUserDep,
) -> UploadResponse:
    data = await file.read()
    storage_uc = UploadImageUseCase(storage=MinIOFileStorage())
    key = await storage_uc.execute(
        UploadImageCommand(data=data, content_type=file.content_type or "", section="blog")
    )
    await update_uc.execute(UpdateBlogPostCommand(slug=slug, cover_image_url=key))
    return UploadResponse(key=key)


# ── Tags ──────────────────────────────────────────────────────────────────────

@router.get("/tags", status_code=status.HTTP_200_OK, response_model=list[BlogTagSchema])
async def list_blog_tags(uc: ListBlogTagsDep) -> list[BlogTagSchema]:
    result = await uc.execute(ListBlogTagsCommand())
    return [BlogTagSchema(id=t.id, name=t.name, slug=t.slug) for t in result.items]


@router.post("/tags", status_code=status.HTTP_201_CREATED, response_model=BlogTagSchema)
async def create_blog_tag(
    body: CreateBlogTagRequest,
    uc: CreateBlogTagDep,
    _: AdminUserDep,
) -> BlogTagSchema:
    result = await uc.execute(CreateBlogTagCommand(name=body.name, slug=body.slug))
    return BlogTagSchema(id=result.id, name=result.name, slug=result.slug)


@router.patch("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_blog_tag(
    tag_id: UUID,
    body: UpdateBlogTagRequest,
    uc: UpdateBlogTagDep,
    _: AdminUserDep,
) -> None:
    await uc.execute(UpdateBlogTagCommand(tag_id=tag_id, name=body.name, slug=body.slug))


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_tag(tag_id: UUID, uc: DeleteBlogTagDep, _: AdminUserDep) -> None:
    await uc.execute(DeleteBlogTagCommand(tag_id=tag_id))
