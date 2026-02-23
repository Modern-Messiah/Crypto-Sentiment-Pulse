import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.cryptopanic import fetch_news, _do_fetch_and_publish

@pytest.mark.asyncio
@patch("app.services.cryptopanic.settings")
@patch("httpx.AsyncClient.get")
async def test_fetch_news_success(mock_get, mock_settings):
    mock_settings.CRYPTOPANIC_API_TOKEN = "valid_token"
    mock_response = MagicMock()
    mock_response.json.return_value = {"results": [{"id": 1, "title": "BTC up"}]}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    results = await fetch_news()
    
    assert len(results) == 1
    assert results[0]["id"] == 1
    mock_get.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.cryptopanic.settings")
async def test_fetch_news_no_token(mock_settings):
    mock_settings.CRYPTOPANIC_API_TOKEN = None
    results = await fetch_news()
    assert results == []

@pytest.mark.asyncio
@patch("app.services.cryptopanic.celery_app")
@patch("app.services.cryptopanic.fetch_news")
async def test_do_fetch_and_publish(mock_fetch, mock_celery):
    mock_fetch.return_value = [{"id": 1}]
    mock_redis = AsyncMock()
    
    await _do_fetch_and_publish(mock_redis)
    
    mock_celery.send_task.assert_called_once_with("app.tasks.cryptopanic_tasks.fetch_and_persist_news")
    mock_redis.publish.assert_called_once()
    
    args, _ = mock_redis.publish.call_args
    payload = json.loads(args[1])
    assert payload["type"] == "cryptopanic_update"
    assert payload["data"][0]["id"] == 1
