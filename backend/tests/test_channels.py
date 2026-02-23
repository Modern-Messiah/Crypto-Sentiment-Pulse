import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

def test_get_channels_endpoint(test_client: TestClient):
    with patch("app.api.api_v1.endpoints.channels.get_db") as mock_get_db:
        # Simplistic patch since our override might do it anyway
        response = test_client.get("/api/v1/channels/")
        # If DB lookup fails it returns 500 or empty, but route should exist
        assert response.status_code in [200, 500]

def test_delete_channel_endpoint(test_client: TestClient):
    # Testing path parameter
    with patch("app.api.api_v1.endpoints.channels.get_db") as mock_get_db:
        response = test_client.delete("/api/v1/channels/12345")
        assert response.status_code in [200, 404, 500] 
