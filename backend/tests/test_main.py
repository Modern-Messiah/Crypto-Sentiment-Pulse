import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_root_endpoint(test_client: TestClient):
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "tracked_symbols" in data
    assert "telegram_channels" in data

def test_media_static_mount(test_client: TestClient):
    response = test_client.get("/media/")
    assert response.status_code in [200, 404]
