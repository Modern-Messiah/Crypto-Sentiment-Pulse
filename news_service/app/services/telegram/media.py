import os
import logging

try:
    from telethon import events
except ImportError:
    pass

logger = logging.getLogger(__name__)

class MediaDownloader:
    def __init__(self, media_dir: str = "/data/media"):
        self.media_dir = media_dir
        if not os.path.exists(self.media_dir):
            os.makedirs(self.media_dir, exist_ok=True)

    async def download(self, client, msg_or_event, username: str) -> tuple[bool, str, str]:
        
        has_media = False
        media_type = None
        media_path = None

        try:
            if getattr(msg_or_event, 'photo', None):
                has_media = True
                media_type = 'photo'
            elif getattr(msg_or_event, 'video', None):
                has_media = True
                media_type = 'video'
            elif getattr(msg_or_event, 'document', None):
                doc = msg_or_event.document
                is_gif = any(isinstance(attr, (getattr(events, 'DocumentAttributeAnimated', object), object))
                             for attr in doc.attributes)
                if 'video' in doc.mime_type or is_gif:
                    has_media = True
                    media_type = 'gif' if is_gif else 'video'

            if has_media:
                ext = '.jpg' if media_type == 'photo' else '.mp4'
                filename = f"{username}_{msg_or_event.id}{ext}"
                full_path = os.path.join(self.media_dir, filename)

                if not os.path.exists(full_path):
                    logger.info(f"Downloading media for message {msg_or_event.id} from @{username}...")
                    await client.download_media(msg_or_event, file=full_path)

                media_path = filename
        except Exception as media_e:
            logger.error(f"Error downloading media: {media_e}")

        return has_media, media_type, media_path
