from __future__ import annotations

from uuid import uuid4

from src.backend.application.shared.errors import NotFoundError

ENDPOINT = "/api/v1/items"


async def test_add_item_tag_204(admin_client, mock_add_tag_uc):
    body = {"tag_id": str(uuid4())}
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/tags", json=body)
    assert response.status_code == 204


async def test_add_item_tag_404(admin_client, mock_add_tag_uc):
    mock_add_tag_uc.execute.side_effect = NotFoundError("item not found")
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/tags", json={"tag_id": str(uuid4())})
    assert response.status_code == 404


async def test_add_item_tag_403_regular_user(user_client, mock_add_tag_uc):
    response = await user_client.post(f"{ENDPOINT}/{uuid4()}/tags", json={"tag_id": str(uuid4())})
    assert response.status_code == 403


async def test_add_item_tag_401_anon(anon_client, mock_add_tag_uc):
    response = await anon_client.post(f"{ENDPOINT}/{uuid4()}/tags", json={"tag_id": str(uuid4())})
    assert response.status_code == 401


async def test_add_item_tag_422_missing_tag_id(admin_client, mock_add_tag_uc):
    response = await admin_client.post(f"{ENDPOINT}/{uuid4()}/tags", json={})
    assert response.status_code == 422


async def test_remove_item_tag_204(admin_client, mock_remove_tag_uc):
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}/tags/{uuid4()}")
    assert response.status_code == 204


async def test_remove_item_tag_404(admin_client, mock_remove_tag_uc):
    mock_remove_tag_uc.execute.side_effect = NotFoundError("tag not found")
    response = await admin_client.delete(f"{ENDPOINT}/{uuid4()}/tags/{uuid4()}")
    assert response.status_code == 404


async def test_remove_item_tag_403_regular_user(user_client, mock_remove_tag_uc):
    response = await user_client.delete(f"{ENDPOINT}/{uuid4()}/tags/{uuid4()}")
    assert response.status_code == 403


async def test_remove_item_tag_401_anon(anon_client, mock_remove_tag_uc):
    response = await anon_client.delete(f"{ENDPOINT}/{uuid4()}/tags/{uuid4()}")
    assert response.status_code == 401
