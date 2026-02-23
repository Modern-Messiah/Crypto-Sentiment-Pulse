import logging
from collections import deque

from .media import MediaDownloader
from .parser import MessageParser
from .publisher import MessagePublisher

logger = logging.getLogger(__name__)

class MessageProcessor:
    def __init__(self, client, messages_buffer: deque, channels: dict, channels_by_id: dict, redis_client, is_demo: bool):
        self.client = client
        self.messages = messages_buffer
        self.channels = channels
        self.channels_by_id = channels_by_id
        self.processing_ids = set()
        self.media_downloader = MediaDownloader()
        self.publisher = MessagePublisher(redis_client)
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
            parsed_msg = MessageParser.parse(msg_or_event, username, title, is_edit)
            if not parsed_msg:
                logger.debug(f"Skipping empty/service update from @{username}")
                return

            text_content = parsed_msg['text']
            grouped_id = parsed_msg['grouped_id']

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
                has_media = False
                media_type = None
                media_path = None

                if not self._demo_mode and self.client:
                    has_media, media_type, media_path = await self.media_downloader.download(self.client, msg_or_event, username)

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

                    await self.publisher.publish_to_redis(existing_in_buffer)
                    self.publisher.send_to_celery(existing_in_buffer)
                else:
                    parsed_msg['has_media'] = has_media
                    parsed_msg['media_type'] = media_type
                    parsed_msg['media_path'] = media_path
                    
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

                    await self.publisher.publish_to_redis(parsed_msg)
                    self.publisher.send_to_celery(parsed_msg)

                logger.info(f"Processed {'edit' if is_edit else 'msg'} from @{username}: {text_content[:50]}...")
            finally:
                self.processing_ids.discard(msg_key)

        except Exception as e:
            logger.error(f"Error processing raw message: {e}", exc_info=True)
