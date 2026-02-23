import asyncio
import logging
from collections import deque

logger = logging.getLogger(__name__)

class HeartbeatMonitor:
    def __init__(self, client, messages_buffer: deque, channels: dict, processor):
        self.client = client
        self.messages = messages_buffer
        self.channels = channels
        self.processor = processor
        self._running = False

    def start(self):
        self._running = True
        asyncio.create_task(self._heartbeat())

    def stop(self):
        self._running = False

    async def _heartbeat(self):
        while self._running:
            try:
                if self.client and await self.client.is_user_authorized():
                    me = await self.client.get_me()
                    isConnected = self.client.is_connected()

                    for username, info in self.channels.items():
                        try:
                            msgs = await self.client.get_messages(info['id'], limit=1)
                            if msgs:
                                m = msgs[0]
                                if not any(msg['id'] == m.id and msg['channel_username'] == username for msg in self.messages):
                                    logger.info(f"POLL: Found new message from @{username}")
                                    await self.processor.process_raw_message(m, username, info['title'])
                        except Exception as poll_e:
                            logger.error(f"Poll error for {username}: {poll_e}")

                    logger.info(f"Telegram heartbeat: Connected={isConnected}, User={me.username}, Buffer={len(self.messages)}")
                else:
                    logger.warning("Telegram heartbeat: Client not authorized")
            except Exception as e:
                logger.error(f"Telegram heartbeat error: {e}")
            await asyncio.sleep(10)
