import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.telegram.publisher import MessagePublisher
import json

@pytest.mark.asyncio
async def test_publish_to_redis_success():
    mock_redis = AsyncMock()
    publisher = MessagePublisher(redis_client=mock_redis)
    
    msg_data = {"id": 1, "text": "test redis"}
    await publisher.publish_to_redis(msg_data)
    
    mock_redis.publish.assert_called_once()
    args, kwargs = mock_redis.publish.call_args
    assert args[0] == "news:telegram"
    
    payload = json.loads(args[1])
    assert payload["type"] == "telegram_update"
    assert payload["data"]["id"] == 1

@pytest.mark.asyncio
async def test_publish_to_redis_no_client():
    publisher = MessagePublisher(redis_client=None)
    await publisher.publish_to_redis({"id": 1})

@patch("app.services.telegram.publisher.celery_app")
def test_send_to_celery_success(mock_celery_app):
    publisher = MessagePublisher(redis_client=None)
    msg_data = {"id": 1, "text": "test celery"}
    
    publisher.send_to_celery(msg_data)
    
    mock_celery_app.send_task.assert_called_once_with(
        "app.tasks.telegram_tasks.persist_telegram_message",
        args=[msg_data]
    )

@patch("app.services.telegram.publisher.celery_app")
def test_send_to_celery_exception(mock_celery_app):
    mock_celery_app.send_task.side_effect = Exception("Celery is down")
    publisher = MessagePublisher(redis_client=None)
    
    publisher.send_to_celery({"id": 1})
