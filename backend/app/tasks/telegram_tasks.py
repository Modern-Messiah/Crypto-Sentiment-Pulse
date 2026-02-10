from datetime import datetime
import logging
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.message import Message
from app.models.channel import Channel

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.telegram_tasks.persist_telegram_message")
def persist_telegram_message(message_data: dict):
    """
    Persist a telegram message and its media to the database.
    Supports albums via grouped_id.
    """
    from app.models.message import MessageMedia
    db = SessionLocal()
    try:
        username = message_data.get('channel_username', '').strip('@')
        channel = db.query(Channel).filter(Channel.username == username).first()
        
        if not channel:
            channel = Channel(
                username=username,
                title=message_data.get('channel_title', username),
                is_active=True
            )
            db.add(channel)
            db.flush()
            
        tg_msg_id = message_data.get('id')
        grouped_id = message_data.get('grouped_id')
        
        existing = None
        # 1. Check if it's part of an album
        if grouped_id:
            # Look for an existing message in the same channel with same grouped_id
            existing = db.query(Message).filter(
                Message.channel_id == channel.id,
                Message.grouped_id == grouped_id
            ).first()

        # 2. If not an album or not found, check by telegram_message_id
        if not existing:
            existing = db.query(Message).filter(
                Message.channel_id == channel.id,
                Message.telegram_message_id == tg_msg_id
            ).first()

        if not existing:
            # Create new message
            new_msg = Message(
                channel_id=channel.id,
                telegram_message_id=tg_msg_id,
                grouped_id=grouped_id,
                text=message_data.get('text'),
                views=message_data.get('views', 0),
                forwards=message_data.get('forwards', 0),
                has_media=1 if message_data.get('has_media') else 0,
                media_type=message_data.get('media_type'), # Still keep for legacy
                media_path=message_data.get('media_path'),   # Still keep for legacy
                telegram_date=datetime.fromisoformat(message_data.get('date')) if message_data.get('date') else datetime.utcnow()
            )
            db.add(new_msg)
            db.flush()
            existing = new_msg
            logger.info(f"Persisted new message {tg_msg_id} from @{username}")
        else:
            # Update stats
            existing.views = message_data.get('views', existing.views)
            existing.forwards = message_data.get('forwards', existing.forwards)
            # If the new part has text but existing doesn't, update it (common in albums)
            if not existing.text and message_data.get('text'):
                existing.text = message_data.get('text')
            db.flush()

        # 3. Handle Media
        if message_data.get('has_media') and message_data.get('media_path'):
            # Check if this specific media is already attached
            media_exists = db.query(MessageMedia).filter(
                MessageMedia.message_id == existing.id,
                MessageMedia.media_path == message_data.get('media_path')
            ).first()
            
            if not media_exists:
                new_media = MessageMedia(
                    message_id=existing.id,
                    media_type=message_data.get('media_type'),
                    media_path=message_data.get('media_path')
                )
                db.add(new_media)
                # Also update legacy fields if they are empty
                if not existing.media_path:
                    existing.has_media = 1
                    existing.media_type = new_media.media_type
                    existing.media_path = new_media.media_path
        
        db.commit()
    except Exception as e:
        logger.error(f"Error persisting telegram message: {e}")
        db.rollback()
    finally:
        db.close()
