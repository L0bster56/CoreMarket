from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from src.backend.application.comment.dtos.list_comments import CommentResult, ListCommentsResult

ENDPOINT = "/api/v1/items/{item_id}/comments"


def _url(item_id=None):
    return ENDPOINT.format(item_id=item_id or uuid4())


async def test_list_comments_200(anon_client, mock_list_uc):
    response = await anon_client.get(_url())
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    comment = data[0]
    assert comment["body"] == "Great product!"
    assert comment["is_deleted"] is False
    assert "id" in comment
    assert "user_id" in comment
    assert "children" in comment


async def test_list_comments_200_empty(anon_client, mock_list_uc):
    mock_list_uc.execute.return_value = ListCommentsResult(items=[])
    response = await anon_client.get(_url())
    assert response.status_code == 200
    assert response.json() == []


async def test_list_comments_200_nested(anon_client, mock_list_uc):
    now = datetime.now(timezone.utc)
    child = CommentResult(
        id=uuid4(),
        item_id=uuid4(),
        user_id=uuid4(),
        parent_id=uuid4(),
        body="Reply comment",
        is_deleted=False,
        created_at=now,
        updated_at=now,
        children=[],
    )
    parent = CommentResult(
        id=uuid4(),
        item_id=uuid4(),
        user_id=uuid4(),
        parent_id=None,
        body="Parent comment",
        is_deleted=False,
        created_at=now,
        updated_at=now,
        children=[child],
    )
    mock_list_uc.execute.return_value = ListCommentsResult(items=[parent])
    response = await anon_client.get(_url())
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert len(data[0]["children"]) == 1
    assert data[0]["children"][0]["body"] == "Reply comment"


async def test_list_comments_422_invalid_item_uuid(anon_client, mock_list_uc):
    response = await anon_client.get(ENDPOINT.format(item_id="not-a-uuid"))
    assert response.status_code == 422
