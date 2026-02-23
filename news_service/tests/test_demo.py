import pytest
import asyncio
from collections import deque
from app.services.telegram.demo import DemoGenerator

@pytest.mark.asyncio
async def test_demo_generator_starts_and_stops():
    messages = deque(maxlen=10)
    demo = DemoGenerator(messages)
    
    demo.start()
    assert demo._running is True
    
    demo.stop()
    assert demo._running is False

@pytest.mark.asyncio
async def test_demo_generator_creates_messages():
    messages = deque(maxlen=10)
    demo = DemoGenerator(messages)
    
    import unittest.mock as mock
    
    with mock.patch("asyncio.sleep", new_callable=mock.AsyncMock) as mock_sleep:
        demo._running = True
        
        async def mock_sleep_side_effect(*args, **kwargs):
            demo._running = False
            return None
            
        mock_sleep.side_effect = mock_sleep_side_effect
        
        await demo._generate_demo_messages()
        
        assert len(messages) == 1
        msg = messages[0]
        assert "channel_username" in msg
        assert "text" in msg
        assert msg["is_demo"] is True
