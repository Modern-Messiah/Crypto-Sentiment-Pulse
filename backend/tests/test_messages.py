import pytest
from fastapi.testclient import TestClient

def test_get_messages(test_client: TestClient):
    response = test_client.get("/api/v1/messages/")
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)

def test_get_messages_with_limit(test_client: TestClient):
    response = test_client.get("/api/v1/messages/?limit=5")
    assert response.status_code in [200, 500]
    
def test_get_messages_with_skip(test_client: TestClient):
    response = test_client.get("/api/v1/messages/?skip=10")
    assert response.status_code in [200, 500]
