import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class MessageParser:
    @staticmethod
    def parse(msg_or_event, username: str, title: str, is_edit: bool = False) -> dict:
        text_content = getattr(msg_or_event, 'text', '') or getattr(msg_or_event, 'message', '') or ''

        if not text_content:
            if getattr(msg_or_event, 'photo', None) or getattr(msg_or_event, 'video', None) or getattr(msg_or_event, 'document', None):
                text_content = "[Media Content]"
            elif getattr(msg_or_event, 'poll', None):
                text_content = f"[Poll: {msg_or_event.poll.poll.question}]"
            elif getattr(msg_or_event, 'venue', None) or getattr(msg_or_event, 'geo', None):
                text_content = "[Location/Venue]"
            else:
                return None

        grouped_id = getattr(msg_or_event, 'grouped_id', None)

        parsed_msg = {
            'id': msg_or_event.id,
            'channel_username': username,
            'channel_title': title,
            'text': str(text_content),
            'views': getattr(msg_or_event, 'views', 0) or 0,
            'forwards': getattr(msg_or_event, 'forwards', 0) or 0,
            'date': msg_or_event.date.isoformat() if hasattr(msg_or_event, 'date') and msg_or_event.date else datetime.utcnow().isoformat() + "Z",
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'is_edit': is_edit,
            'grouped_id': grouped_id,
            'has_media': False,
            'media_type': None,
            'media_path': None,
            'media_list': []
        }

        return parsed_msg
