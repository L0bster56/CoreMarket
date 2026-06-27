from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

BASE = "/api/v1/blog/posts"


async def test_link_product_201(admin_client, mock_link_product_uc):
    product_id = uuid4()
    response = await admin_client.post(
        f"{BASE}/test-post/products",
        json={"product_id": str(product_id), "display_order": 1},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "product_id" in data
    assert "display_order" in data


async def test_link_product_401_anon(anon_client, mock_link_product_uc):
    response = await anon_client.post(
        f"{BASE}/test-post/products",
        json={"product_id": str(uuid4())},
    )
    assert response.status_code == 401


async def test_link_product_403_user(user_client, mock_link_product_uc):
    response = await user_client.post(
        f"{BASE}/test-post/products",
        json={"product_id": str(uuid4())},
    )
    assert response.status_code == 403


async def test_link_product_404_post_not_found(admin_client, mock_link_product_uc):
    mock_link_product_uc.execute.side_effect = NotFoundError("not found")
    response = await admin_client.post(
        f"{BASE}/missing/products",
        json={"product_id": str(uuid4())},
    )
    assert response.status_code == 404


async def test_link_product_passes_fields_to_use_case(admin_client, mock_link_product_uc):
    product_id = uuid4()
    await admin_client.post(
        f"{BASE}/my-slug/products",
        json={"product_id": str(product_id), "display_order": 3},
    )
    cmd = mock_link_product_uc.execute.call_args[0][0]
    assert cmd.slug == "my-slug"
    assert cmd.product_id == product_id
    assert cmd.display_order == 3


async def test_unlink_product_204(admin_client, mock_unlink_product_uc):
    response = await admin_client.delete(f"{BASE}/test-post/products/{uuid4()}")
    assert response.status_code == 204


async def test_unlink_product_401_anon(anon_client, mock_unlink_product_uc):
    response = await anon_client.delete(f"{BASE}/test-post/products/{uuid4()}")
    assert response.status_code == 401


async def test_unlink_product_403_user(user_client, mock_unlink_product_uc):
    response = await user_client.delete(f"{BASE}/test-post/products/{uuid4()}")
    assert response.status_code == 403


async def test_unlink_product_404(admin_client, mock_unlink_product_uc):
    mock_unlink_product_uc.execute.side_effect = NotFoundError("not found")
    response = await admin_client.delete(f"{BASE}/missing/products/{uuid4()}")
    assert response.status_code == 404
