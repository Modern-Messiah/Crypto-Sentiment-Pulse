import logging
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

class HistoryFetcher:
    def __init__(self, client, messages_buffer: deque, channels: dict, publisher):
        self.client = client
        self.messages = messages_buffer
        self.channels = channels
        self.publisher = publisher

    async def fetch(self):
        """Fetches initial message history for all subscribed channels."""
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

                    # Persist history messages to database immediately
                    self.publisher.send_to_celery(parsed_msg)
            except Exception as e:
                logger.error(f"Could not fetch history for {username}: {e}")
