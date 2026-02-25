import asyncio
import logging
from collections import deque

from .history import HistoryFetcher
from .heartbeat import HeartbeatMonitor

try:
    from telethon import TelegramClient, events
    from telethon.tl.functions.channels import GetFullChannelRequest
except ImportError:
    pass

logger = logging.getLogger(__name__)

class TelegramClientManager:
    def __init__(self, api_id: int, api_hash: str, session_path: str, messages_buffer: deque, channels: dict, channels_by_id: dict, message_processor):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session_path = session_path
        self.messages = messages_buffer
        self.channels = channels
        self.channels_by_id = channels_by_id
        self.processor = message_processor
        self.client = None
        self._running = False
        self.heartbeat_monitor = None

    async def start(self, channel_usernames: list[str]) -> bool:
        try:
            loop = asyncio.get_event_loop()
            self.client = TelegramClient(self.session_path, self.api_id, self.api_hash, loop=loop)
            self.processor.client = self.client
            
            self.history_fetcher = HistoryFetcher(self.client, self.messages, self.channels, self.processor.publisher)
            self.heartbeat_monitor = HeartbeatMonitor(self.client, self.messages, self.channels, self.processor)

            self.channels_by_id.update({info['id']: username for username, info in self.channels.items()})
            logger.info(f"Registering handlers for {len(self.channels)} channels.")

            self.client.add_event_handler(self._new_message_handler, events.NewMessage())
            self.client.add_event_handler(self._edit_message_handler, events.MessageEdited())
            self.client.add_event_handler(self._raw_update_handler, events.Raw())

            await self.client.connect()
            if not await self.client.is_user_authorized():
                raise RuntimeError(
                    "Telegram session not authorized. "
                    "Run auth script first: docker compose exec -it news-service python -c "
                    "\"from telethon.sync import TelegramClient; import os; "
                    "c = TelegramClient('/data/sessions/crypto_bot', "
                    "int(os.environ['TELEGRAM_API_ID']), os.environ['TELEGRAM_API_HASH']); "
                    "c.start(); c.disconnect()\""
                )
            logger.info("Connected and authorized in Telegram!")

            asyncio.create_task(self.client.run_until_disconnected())
            logger.info("Telethon background listener task started.")

            for username in channel_usernames:
                try:
                    await self._subscribe_channel(username)
                except Exception as e:
                    logger.error(f"Failed to subscribe to {username}: {e}")

            logger.info("Syncing dialogs to activate update stream...")
            await self.client.get_dialogs(limit=10)

            logger.info("Fetching initial history...")
            await self.history_fetcher.fetch()

            self._running = True
            logger.info(f"Telegram monitoring fully active.")

            self.heartbeat_monitor.start()
            return True

        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}", exc_info=True)
            return False

    async def _new_message_handler(self, event):
        chat_id = event.chat_id
        tg_id = chat_id
        if str(tg_id).startswith('-100'):
            tg_id = int(str(tg_id)[4:])

        if tg_id in self.channels_by_id:
            logger.info(f"EVENT: NewMessage from {self.channels_by_id[tg_id]} ({chat_id})")
            await self.processor.handle_message(event)

    async def _edit_message_handler(self, event):
        chat_id = event.chat_id
        tg_id = chat_id
        if str(tg_id).startswith('-100'):
            tg_id = int(str(tg_id)[4:])

        if tg_id in self.channels_by_id:
            logger.info(f"EVENT: MessageEdited from {self.channels_by_id[tg_id]} ({chat_id})")
            await self.processor.handle_message(event, is_edit=True)

    async def _raw_update_handler(self, event):
        try:
            update_type = type(event).__name__
            logger.debug(f"RAW_UPDATE: {update_type}")
        except:
            pass

    async def _subscribe_channel(self, username: str):
        try:
            entity = await self.client.get_entity(username)
            full = await self.client(GetFullChannelRequest(entity))

            self.channels[username] = {
                'id': entity.id,
                'entity': entity,
                'username': username,
                'title': entity.title,
                'subscribers': full.full_chat.participants_count or 0
            }

            self.channels_by_id[entity.id] = username

            logger.info(f"Subscribed to @{username} (ID: {entity.id}, {full.full_chat.participants_count} subscribers)")

        except Exception as e:
            logger.error(f"Error subscribing to {username}: {e}")
            raise

    async def close(self):
        self._running = False
        if self.heartbeat_monitor:
            self.heartbeat_monitor.stop()

        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")
