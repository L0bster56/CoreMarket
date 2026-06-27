import uuid

from src.backend.domain.blog.product_link import BlogProductLink


class TestBlogProductLinkCreate:
    def test_create_sets_fields(self):
        post_id = uuid.uuid4()
        product_id = uuid.uuid4()
        link = BlogProductLink(blog_post_id=post_id, product_id=product_id)
        assert link.blog_post_id == post_id
        assert link.product_id == product_id

    def test_display_order_defaults_to_zero(self):
        link = BlogProductLink(blog_post_id=uuid.uuid4(), product_id=uuid.uuid4())
        assert link.display_order == 0

    def test_custom_display_order(self):
        link = BlogProductLink(blog_post_id=uuid.uuid4(), product_id=uuid.uuid4(), display_order=5)
        assert link.display_order == 5

    def test_id_is_uuid(self):
        link = BlogProductLink(blog_post_id=uuid.uuid4(), product_id=uuid.uuid4())
        assert isinstance(link.id, uuid.UUID)

    def test_gives_unique_ids(self):
        l1 = BlogProductLink(blog_post_id=uuid.uuid4(), product_id=uuid.uuid4())
        l2 = BlogProductLink(blog_post_id=uuid.uuid4(), product_id=uuid.uuid4())
        assert l1.id != l2.id
