import os
import asyncio
import logging
from collections import deque
from typing import Optional

from .client_manager import TelegramClientManager
from .processor import MessageProcessor
from .demo import DemoGenerator

try:
    from telethon import TelegramClient
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logging.getLogger(__name__).warning("Telethon not installed. Telegram integration will use demo mode.")

logger = logging.getLogger(__name__)

class TelegramService:
    def __init__(self, api_id: Optional[int], api_hash: Optional[str], session_name: str = "crypto_bot"):
        self.api_id = api_id
        self.api_hash = api_hash

        session_dir = "/data/sessions"
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
            logger.info(f"Created session directory: {session_dir}")

        self.session_path = os.path.join(session_dir, session_name)
        self.session_name = session_name
        self.messages = deque(maxlen=500)
        self.channels = {}
        self.channels_by_id = {}
        
        self._demo_mode = not TELETHON_AVAILABLE or not api_id or not api_hash

        if self._demo_mode:
            logger.info("Telegram service running in DEMO mode")
            self.demo_generator = DemoGenerator(self.messages)
            self.client_manager = None
            self.processor = None
        else:
            self.demo_generator = None
            self.client_manager = None
            self.processor = None

    @property
    def is_demo_mode(self) -> bool:
        return self._demo_mode

    async def start(self, channel_usernames: list[str], redis_client):
        if self._demo_mode:
            self.demo_generator.start()
            return

        self.processor = MessageProcessor(
            client=None,
            messages_buffer=self.messages,
            channels=self.channels,
            channels_by_id=self.channels_by_id,
            redis_client=redis_client,
            is_demo=self._demo_mode
        )

        self.client_manager = TelegramClientManager(
            api_id=self.api_id,
            api_hash=self.api_hash,
            session_path=self.session_path,
            messages_buffer=self.messages,
            channels=self.channels,
            channels_by_id=self.channels_by_id,
            message_processor=self.processor
        )

        success = await self.client_manager.start(channel_usernames)
        if not success:
            logger.error("Falling back to demo mode due to client start failure.")
            self._demo_mode = True
            self.demo_generator = DemoGenerator(self.messages)
            self.demo_generator.start()

    def get_messages(self, limit: int = 20, skip: int = 0) -> list:
        all_msgs = list(self.messages)
        all_msgs.sort(key=lambda x: x['date'], reverse=True)
        return all_msgs[skip: skip + limit]

    def get_latest_message(self) -> Optional[dict]:
        return self.messages[0] if self.messages else None

    async def close(self):
        if self._demo_mode and self.demo_generator:
            self.demo_generator.stop()
            
        if self.client_manager:
            await self.client_manager.close()
