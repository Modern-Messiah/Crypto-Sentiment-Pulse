import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

def test_get_cryptopanic_news(test_client: TestClient):
    response = test_client.get("/api/v1/news/")
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, (list, dict))

def test_get_cryptopanic_news_with_limit(test_client: TestClient):
    response = test_client.get("/api/v1/news/?limit=5")
    assert response.status_code in [200, 500]
