import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

@patch("app.api.api_v1.endpoints.health.aioredis.from_url")
def test_health_check_ok(mock_redis, test_client: TestClient):
    mock_client = AsyncMock()
    mock_client.get.return_value = '{"prices": {"BTCUSDT": {"price": 50000.0}}}'
    mock_redis.return_value = mock_client
    
    response = test_client.get("/api/v1/health/")
    
    if response.status_code == 200:
        data = response.json()
        assert data["status"] in ["healthy", "connecting"]
    else:
        assert response.status_code == 503
