from src.backend.application.blog.dtos.blog_tags import ListBlogTagsCommand
from src.backend.application.blog.use_cases.list_blog_tags import ListBlogTagsUseCase
from src.backend.domain.blog.entity import BlogTag


class TestListBlogTagsUseCase:
    async def test_returns_all_tags(self, mock_uow, mock_blog_tag_repo):
        tags = [
            BlogTag.create(name="Python", slug="python"),
            BlogTag.create(name="Django", slug="django"),
        ]
        mock_blog_tag_repo.list.return_value = tags
        uc = ListBlogTagsUseCase(uow=mock_uow)

        result = await uc.execute(ListBlogTagsCommand())

        assert len(result.items) == 2
        assert result.items[0].slug == "python"
        assert result.items[1].slug == "django"

    async def test_returns_empty_list(self, mock_uow, mock_blog_tag_repo):
        mock_blog_tag_repo.list.return_value = []
        uc = ListBlogTagsUseCase(uow=mock_uow)

        result = await uc.execute(ListBlogTagsCommand())

        assert result.items == []

    async def test_maps_tag_fields_correctly(self, mock_uow, mock_blog_tag_repo, sample_blog_tag):
        mock_blog_tag_repo.list.return_value = [sample_blog_tag]
        uc = ListBlogTagsUseCase(uow=mock_uow)

        result = await uc.execute(ListBlogTagsCommand())

        item = result.items[0]
        assert item.id == sample_blog_tag.id
        assert item.name == "Technology"
        assert item.slug == "technology"
