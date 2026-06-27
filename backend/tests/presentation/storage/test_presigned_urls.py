from __future__ import annotations

from src.backend.application.storage.dtos.get_presigned_urls import GetPresignedUrlsCommand

ENDPOINT = "/api/v1/storage/presigned-urls"


async def test_presigned_urls_200_valid_keys(anon_client, mock_storage_uc):
    response = await anon_client.post(ENDPOINT, json={"keys": ["items/test.jpg"]})

    assert response.status_code == 200
    data = response.json()
    assert "urls" in data
    assert data["urls"]["items/test.jpg"] == "http://localhost:9000/coremarket/items/test.jpg?sig=abc123"


async def test_presigned_urls_200_custom_expires_in(anon_client, mock_storage_uc):
    response = await anon_client.post(ENDPOINT, json={"keys": ["items/a.jpg"], "expires_in": 7200})

    assert response.status_code == 200
    cmd: GetPresignedUrlsCommand = mock_storage_uc.execute.call_args[0][0]
    assert cmd.expires_in == 7200


async def test_presigned_urls_200_default_expires_in(anon_client, mock_storage_uc):
    response = await anon_client.post(ENDPOINT, json={"keys": ["items/a.jpg"]})

    assert response.status_code == 200
    cmd: GetPresignedUrlsCommand = mock_storage_uc.execute.call_args[0][0]
    assert cmd.expires_in == 3600


async def test_presigned_urls_200_empty_keys(anon_client, mock_storage_uc):
    mock_storage_uc.execute.return_value.__class__  # keep fixture alive
    from src.backend.application.storage.dtos.get_presigned_urls import GetPresignedUrlsResult
    mock_storage_uc.execute.return_value = GetPresignedUrlsResult(urls={})

    response = await anon_client.post(ENDPOINT, json={"keys": []})

    assert response.status_code == 200
    assert response.json()["urls"] == {}


async def test_presigned_urls_422_keys_exceed_100(anon_client):
    response = await anon_client.post(ENDPOINT, json={"keys": ["k"] * 101})

    assert response.status_code == 422


async def test_presigned_urls_422_expires_in_too_low(anon_client):
    response = await anon_client.post(ENDPOINT, json={"keys": ["items/a.jpg"], "expires_in": 30})

    assert response.status_code == 422


async def test_presigned_urls_422_expires_in_too_high(anon_client):
    response = await anon_client.post(ENDPOINT, json={"keys": ["items/a.jpg"], "expires_in": 90000})

    assert response.status_code == 422


async def test_presigned_urls_422_missing_keys_field(anon_client):
    response = await anon_client.post(ENDPOINT, json={"expires_in": 3600})

    assert response.status_code == 422


async def test_presigned_urls_accessible_without_auth(anon_client, mock_storage_uc):
    """Endpoint публичный — авторизация не нужна."""
    response = await anon_client.post(ENDPOINT, json={"keys": ["items/test.jpg"]})

    assert response.status_code == 200
