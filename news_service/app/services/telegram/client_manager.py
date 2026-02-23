import asyncio
import logging
import os
from datetime import datetime
from collections import deque

from app.core.celery_app import celery_app

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

    async def start(self, channel_usernames: list[str]) -> bool:
        try:
            loop = asyncio.get_event_loop()
            self.client = TelegramClient(self.session_path, self.api_id, self.api_hash, loop=loop)
            self.processor.client = self.client # Assign client for media downloading

            self.channels_by_id.update({info['id']: username for username, info in self.channels.items()})
            logger.info(f"Registering handlers for {len(self.channels)} channels.")

            self.client.add_event_handler(self._new_message_handler, events.NewMessage())
            self.client.add_event_handler(self._edit_message_handler, events.MessageEdited())
            self.client.add_event_handler(self._raw_update_handler, events.Raw())

            await self.client.start()
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
            await self._fetch_initial_history()

            self._running = True
            logger.info(f"Telegram monitoring fully active.")

            asyncio.create_task(self._heartbeat())
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

    async def _fetch_initial_history(self):
        for username, info in self.channels.items():
            try:
                messages = await self.client.get_messages(info['id'], limit=3)
                for msg in messages:
                    text_content = msg.text or msg.message or ""
                    if not text_content:
                        if msg.photo or msg.video or msg.document:
                            text_content = "[Media Content]"
                        elif msg.poll:
                            text_content = f"[Poll: {msg.poll.poll.question}]"
                        elif msg.venue or msg.geo:
                            text_content = "[Location/Venue]"
                        else:
                            text_content = "[Message]"

                    parsed_msg = {
                        'id': msg.id,
                        'channel_username': username,
                        'channel_title': info['title'],
                        'text': text_content,
                        'views': getattr(msg, 'views', 0) or 0,
                        'forwards': getattr(msg, 'forwards', 0) or 0,
                        'date': msg.date.isoformat() if msg.date else datetime.utcnow().isoformat() + "Z",
                        'timestamp': datetime.utcnow().isoformat() + "Z"
                    }
                    self.messages.appendleft(parsed_msg)

                    # Send Celery task for DB persistence
                    celery_app.send_task(
                        "app.tasks.telegram_tasks.persist_telegram_message",
                        args=[parsed_msg]
                    )
            except Exception as e:
                logger.error(f"Could not fetch history for {username}: {e}")

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
            # Also update channels_by_id so that handlers map tg_id properly back to username
            self.channels_by_id[entity.id] = username

            logger.info(f"Subscribed to @{username} (ID: {entity.id}, {full.full_chat.participants_count} subscribers)")

        except Exception as e:
            logger.error(f"Error subscribing to {username}: {e}")
            raise

    async def close(self):
        self._running = False
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")
