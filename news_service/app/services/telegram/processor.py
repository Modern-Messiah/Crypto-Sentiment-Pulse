import json
import logging
from collections import deque
from datetime import datetime

from app.core.celery_app import celery_app
from app.core.config import settings
from .media import MediaDownloader

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self, client, messages_buffer: deque, channels: dict, channels_by_id: dict, redis_client, is_demo: bool):
        self.client = client
        self.messages = messages_buffer
        self.channels = channels
        self.channels_by_id = channels_by_id
        self._redis_client = redis_client
        self.processing_ids = set()
        self.media_downloader = MediaDownloader()
        self._demo_mode = is_demo

    async def handle_message(self, event, is_edit=False):
        try:
            chat_id = event.chat_id
            tg_id = chat_id
            if str(tg_id).startswith('-100'):
                tg_id = int(str(tg_id)[4:])

            username = self.channels_by_id.get(tg_id, "unknown")
            info = self.channels.get(username, {})
            title = info.get('title', 'Unknown')

            await self.process_raw_message(event, username, title, is_edit)

        except Exception as e:
            logger.error(f"Error handling message event: {e}", exc_info=True)

    async def process_raw_message(self, msg_or_event, username: str, title: str, is_edit: bool = False):
        try:
            text_content = getattr(msg_or_event, 'text', '') or getattr(msg_or_event, 'message', '') or ''

            if not text_content:
                if getattr(msg_or_event, 'photo', None) or getattr(msg_or_event, 'video', None) or getattr(msg_or_event, 'document', None):
                    text_content = "[Media Content]"
                elif getattr(msg_or_event, 'poll', None):
                    text_content = f"[Poll: {msg_or_event.poll.poll.question}]"
                elif getattr(msg_or_event, 'venue', None) or getattr(msg_or_event, 'geo', None):
                    text_content = "[Location/Venue]"
                else:
                    logger.debug(f"Skipping empty/service update from @{username}")
                    return

            grouped_id = getattr(msg_or_event, 'grouped_id', None)

            # De-duplication
            msg_key = (username, msg_or_event.id)
            if msg_key in self.processing_ids:
                logger.debug(f"Skipping: Message {msg_or_event.id} from @{username} is already being processed")
                return

            existing_in_buffer = None
            if grouped_id:
                for m in self.messages:
                    if m.get('grouped_id') == grouped_id and m.get('channel_username') == username:
                        existing_in_buffer = m
                        break

            if not existing_in_buffer and not is_edit:
                if any(m['id'] == msg_or_event.id and m['channel_username'] == username for m in self.messages):
                    logger.debug(f"Skipping: Message {msg_or_event.id} from @{username} already in buffer")
                    return

            self.processing_ids.add(msg_key)

            try:
                # Media handling
                has_media = False
                media_type = None
                media_path = None

                if not self._demo_mode and self.client:
                    has_media, media_type, media_path = await self.media_downloader.download(self.client, msg_or_event, username)

                parsed_msg = {
                    'id': msg_or_event.id,
                    'channel_username': username,
                    'channel_title': title,
                    'text': text_content,
                    'views': getattr(msg_or_event, 'views', 0) or 0,
                    'forwards': getattr(msg_or_event, 'forwards', 0) or 0,
                    'date': msg_or_event.date.isoformat() if hasattr(msg_or_event, 'date') and msg_or_event.date else datetime.utcnow().isoformat() + "Z",
                    'timestamp': datetime.utcnow().isoformat() + "Z",
                    'is_edit': is_edit,
                    'grouped_id': grouped_id,
                    'has_media': has_media,
                    'media_type': media_type,
                    'media_path': media_path,
                    'media_list': []
                }

                if existing_in_buffer:
                    if not existing_in_buffer.get('text') and text_content:
                        existing_in_buffer['text'] = text_content
                    if 'media_list' not in existing_in_buffer:
                        existing_in_buffer['media_list'] = []

                    if has_media and media_path:
                        if not any(item['path'] == media_path for item in existing_in_buffer['media_list']):
                            existing_in_buffer['media_list'].append({
                                'type': media_type,
                                'path': media_path,
                                'url': f"/media/{media_path}"
                            })

                    if not existing_in_buffer.get('media_path'):
                        existing_in_buffer['has_media'] = has_media
                        existing_in_buffer['media_type'] = media_type
                        existing_in_buffer['media_path'] = media_path

                    # Publish to Redis for backend WebSocket broadcast
                    await self._publish_telegram_update(existing_in_buffer)
                else:
                    if has_media and media_path:
                        parsed_msg['media_list'] = [{
                            'type': media_type,
                            'path': media_path,
                            'url': f"/media/{media_path}"
                        }]

                    if is_edit:
                        for i, m in enumerate(self.messages):
                            if m['id'] == parsed_msg['id']:
                                self.messages[i] = parsed_msg
                                break
                        else:
                            self.messages.appendleft(parsed_msg)
                    else:
                        self.messages.appendleft(parsed_msg)

                    # Publish to Redis for backend WebSocket broadcast
                    await self._publish_telegram_update(parsed_msg)

                # Send Celery task for DB persistence
                celery_app.send_task(
                    "app.tasks.telegram_tasks.persist_telegram_message",
                    args=[parsed_msg]
                )

                logger.info(f"Processed {'edit' if is_edit else 'msg'} from @{username}: {text_content[:50]}...")
            finally:
                self.processing_ids.discard(msg_key)

        except Exception as e:
            logger.error(f"Error processing raw message: {e}", exc_info=True)

    async def _publish_telegram_update(self, msg_data: dict):
        """Publish message to Redis for backend to broadcast via WebSocket."""
        if self._redis_client:
            try:
                payload = json.dumps({
                    "type": "telegram_update",
                    "data": msg_data
                }, default=str)
                await self._redis_client.publish(settings.REDIS_CHANNEL_TELEGRAM, payload)
            except Exception as e:
                logger.error(f"Error publishing to Redis: {e}")
