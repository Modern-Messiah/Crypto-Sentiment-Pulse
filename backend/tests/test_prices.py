import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import json

def test_get_prices_endpoint(test_client: TestClient):
    with patch("app.api.api_v1.endpoints.prices.aioredis.from_url") as mock_redis:
        mock_client = AsyncMock()
        mock_client.get.return_value = json.dumps({"prices": {"BTCUSDT": {"price": 50000.0, "change_24h": 5.0}}})
        mock_redis.return_value = mock_client
        
        response = test_client.get("/api/v1/prices/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "BTCUSDT" in data["data"]
        assert data["data"]["BTCUSDT"]["price"] == 50000.0

def test_get_prices_endpoint_empty(test_client: TestClient):
    with patch("app.api.api_v1.endpoints.prices.aioredis.from_url") as mock_redis:
        mock_client = AsyncMock()
        mock_client.get.return_value = None
        mock_redis.return_value = mock_client
        
        response = test_client.get("/api/v1/prices/")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert data["data"] == {}
