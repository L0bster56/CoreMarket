import time
import uuid
from datetime import timezone

import pytest

from src.backend.domain.blog.entity import BlogPost
from src.backend.domain.blog.enums import BlogPostStatus
from src.backend.domain.blog.errors import (
    BlogPostAlreadyPublishedError,
    BlogPostNoCategoryError,
    BlogPostNoContentError,
)
from src.backend.domain.category.value_objects.slug.error import InvalidSlugError


class TestBlogPostCreate:
    def test_create_required_fields(self):
        post = BlogPost.create(title="Hello World", slug="hello-world")
        assert post.title == "Hello World"
        assert str(post.slug) == "hello-world"
        assert post.status == BlogPostStatus.draft
        assert post.short_description is None
        assert post.content is None
        assert post.cover_image_url is None
        assert post.category_id is None
        assert post.seo_title is None
        assert post.seo_description is None

    def test_create_with_short_description(self):
        post = BlogPost.create(title="Hello", slug="hello", short_description="A brief intro")
        assert post.short_description == "A brief intro"

    def test_create_generates_unique_ids(self):
        p1 = BlogPost.create("Post One", "post-one")
        p2 = BlogPost.create("Post Two", "post-two")
        assert p1.id != p2.id

    def test_create_with_invalid_slug_raises(self):
        with pytest.raises(InvalidSlugError):
            BlogPost.create(title="Hello", slug="Hello World")

    def test_create_sets_draft_status(self):
        post = BlogPost.create("Title", "title")
        assert post.status == BlogPostStatus.draft

    def test_timestamps_are_utc_on_create(self):
        post = BlogPost.create("Title", "title")
        assert post.created_at.tzinfo == timezone.utc
        assert post.updated_at.tzinfo == timezone.utc


class TestBlogPostChangeTitle:
    def test_change_title_updates_field(self):
        post = BlogPost.create("Old Title", "old-title")
        post.change_title("New Title")
        assert post.title == "New Title"

    def test_change_title_calls_touch(self):
        post = BlogPost.create("Old Title", "old-title")
        before = post.updated_at
        time.sleep(0.005)
        post.change_title("New Title")
        assert post.updated_at > before


class TestBlogPostChangeSlug:
    def test_change_slug_updates_field(self):
        post = BlogPost.create("Title", "old-slug")
        post.change_slug("new-slug")
        assert str(post.slug) == "new-slug"

    def test_change_slug_with_invalid_raises(self):
        post = BlogPost.create("Title", "title")
        with pytest.raises(InvalidSlugError):
            post.change_slug("Invalid Slug!")

    def test_change_slug_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.change_slug("new-title")
        assert post.updated_at > before


class TestBlogPostSetContent:
    def test_set_content_updates_field(self):
        post = BlogPost.create("Title", "title")
        post.set_content("# Hello World")
        assert post.content == "# Hello World"

    def test_set_content_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.set_content("Content here")
        assert post.updated_at > before


class TestBlogPostSetCoverImage:
    def test_set_cover_image_updates_field(self):
        post = BlogPost.create("Title", "title")
        post.set_cover_image("blog/cover.jpg")
        assert post.cover_image_url == "blog/cover.jpg"

    def test_set_cover_image_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.set_cover_image("blog/cover.jpg")
        assert post.updated_at > before


class TestBlogPostSetCategory:
    def test_set_category_updates_field(self):
        post = BlogPost.create("Title", "title")
        cat_id = uuid.uuid4()
        post.set_category(cat_id)
        assert post.category_id == cat_id

    def test_set_category_to_none(self):
        post = BlogPost.create("Title", "title")
        post.set_category(uuid.uuid4())
        post.set_category(None)
        assert post.category_id is None

    def test_set_category_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.set_category(uuid.uuid4())
        assert post.updated_at > before


class TestBlogPostSetSeo:
    def test_set_seo_updates_both_fields(self):
        post = BlogPost.create("Title", "title")
        post.set_seo(seo_title="SEO Title", seo_description="SEO Desc")
        assert post.seo_title == "SEO Title"
        assert post.seo_description == "SEO Desc"

    def test_set_seo_to_none_clears_fields(self):
        post = BlogPost.create("Title", "title")
        post.set_seo(seo_title=None, seo_description=None)
        assert post.seo_title is None
        assert post.seo_description is None

    def test_set_seo_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.set_seo("SEO", "Desc")
        assert post.updated_at > before


class TestBlogPostPublish:
    def _publishable_post(self) -> BlogPost:
        post = BlogPost.create("Title", "title")
        post.set_category(uuid.uuid4())
        post.set_content("Some content")
        return post

    def test_publish_sets_status_published(self):
        post = self._publishable_post()
        post.publish()
        assert post.status == BlogPostStatus.published

    def test_publish_without_category_raises(self):
        post = BlogPost.create("Title", "title")
        post.set_content("Content")
        with pytest.raises(BlogPostNoCategoryError):
            post.publish()

    def test_publish_without_content_raises(self):
        post = BlogPost.create("Title", "title")
        post.set_category(uuid.uuid4())
        with pytest.raises(BlogPostNoContentError):
            post.publish()

    def test_publish_already_published_raises(self):
        post = self._publishable_post()
        post.publish()
        with pytest.raises(BlogPostAlreadyPublishedError):
            post.publish()

    def test_publish_calls_touch(self):
        post = self._publishable_post()
        before = post.updated_at
        time.sleep(0.005)
        post.publish()
        assert post.updated_at > before


class TestBlogPostUnpublish:
    def test_unpublish_sets_status_draft(self):
        post = BlogPost.create("Title", "title")
        post.set_category(uuid.uuid4())
        post.set_content("Content")
        post.publish()
        post.unpublish()
        assert post.status == BlogPostStatus.draft

    def test_unpublish_from_draft_stays_draft(self):
        post = BlogPost.create("Title", "title")
        post.unpublish()
        assert post.status == BlogPostStatus.draft

    def test_unpublish_from_archived_sets_draft(self):
        post = BlogPost.create("Title", "title")
        post.archive()
        post.unpublish()
        assert post.status == BlogPostStatus.draft

    def test_unpublish_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.unpublish()
        assert post.updated_at > before


class TestBlogPostArchive:
    def test_archive_sets_status_archived(self):
        post = BlogPost.create("Title", "title")
        post.archive()
        assert post.status == BlogPostStatus.archived

    def test_archive_from_published(self):
        post = BlogPost.create("Title", "title")
        post.set_category(uuid.uuid4())
        post.set_content("Content")
        post.publish()
        post.archive()
        assert post.status == BlogPostStatus.archived

    def test_archive_calls_touch(self):
        post = BlogPost.create("Title", "title")
        before = post.updated_at
        time.sleep(0.005)
        post.archive()
        assert post.updated_at > before


class TestBlogPostEquality:
    def test_same_id_equal(self):
        p1 = BlogPost.create("Title One", "title-one")
        p2 = BlogPost.create("Title Two", "title-two")
        p2.id = p1.id
        assert p1 == p2

    def test_different_id_not_equal(self):
        p1 = BlogPost.create("Title", "title-a")
        p2 = BlogPost.create("Title", "title-b")
        assert p1 != p2
