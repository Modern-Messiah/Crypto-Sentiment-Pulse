import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from collections import deque
from app.services.telegram.heartbeat import HeartbeatMonitor
import asyncio

@pytest.mark.asyncio
async def test_heartbeat_monitor_loop():
    mock_client = AsyncMock()
    mock_client.is_user_authorized.return_value = True
    mock_client.is_connected = MagicMock(return_value=True)
    mock_client.get_me.return_value = MagicMock(username="testuser")
    
    mock_msg = MagicMock(id=1, text="test heartbeat")
    mock_msg.date = datetime.now(timezone.utc)
    mock_client.get_messages.return_value = [mock_msg]
    
    mock_processor = AsyncMock()
    
    messages = deque(maxlen=10)
    channels = {"test_chan": {"id": 1234, "title": "Test Title"}}
    
    monitor = HeartbeatMonitor(mock_client, messages, channels, mock_processor)
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        async def stop_loop(*args, **kwargs):
            monitor._running = False
            return None
        mock_sleep.side_effect = stop_loop
        
        monitor._running = True
        await monitor._heartbeat()
        
        mock_client.get_messages.assert_called_once_with(1234, limit=1)
        mock_processor.process_raw_message.assert_called_once_with(mock_msg, "test_chan", "Test Title")
