from __future__ import annotations


async def test_health(anon_client):
    """App boots and responds (404 on unknown route, not 500)."""
    response = await anon_client.get("/api/v1/nonexistent")
    assert response.status_code == 404
