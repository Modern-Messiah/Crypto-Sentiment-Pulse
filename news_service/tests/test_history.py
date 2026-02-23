import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from collections import deque
from app.services.telegram.history import HistoryFetcher

@pytest.mark.asyncio
async def test_history_fetcher():
    mock_client = AsyncMock()
    
    mock_msg1 = MagicMock(id=1, text="history 1", date=None, views=10, forwards=2, photo=None, video=None, document=None, poll=None, venue=None, geo=None)
    mock_msg2 = MagicMock(id=2, text="history 2", date=None, views=5, forwards=0, photo=None, video=None, document=None, poll=None, venue=None, geo=None)
    
    mock_client.get_messages.return_value = [mock_msg1, mock_msg2]
    
    mock_publisher = MagicMock()
    messages = deque(maxlen=10)
    channels = {"test_chan": {"id": 1234, "title": "Test Title"}}
    
    fetcher = HistoryFetcher(mock_client, messages, channels, mock_publisher)
    
    await fetcher.fetch()
    
    mock_client.get_messages.assert_called_once_with(1234, limit=3)
    assert len(messages) == 2
    
    assert messages[1]["id"] == 1
    assert messages[0]["id"] == 2
    
    assert mock_publisher.send_to_celery.call_count == 2
