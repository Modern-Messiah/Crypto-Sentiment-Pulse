from datetime import datetime
import logging
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from sqlalchemy.dialects.postgresql import insert
from app.models.message import Message
from app.models.channel import Channel

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.telegram_tasks.persist_telegram_message")
def persist_telegram_message(message_data: dict):

    from app.models.message import MessageMedia
    db = SessionLocal()
    try:
        username = message_data.get('channel_username', '').strip('@')
        stmt = insert(Channel).values(
            username=username,
            title=message_data.get('channel_title', username),
            is_active=True
        ).on_conflict_do_nothing(index_elements=["username"])
        db.execute(stmt)
        db.flush()
        channel = db.query(Channel).filter(Channel.username == username).first()
        if not channel:
            raise Exception(f"Failed to get or create channel @{username}")
            
        tg_msg_id = message_data.get('id')
        grouped_id = message_data.get('grouped_id')
        
        existing = None
        if grouped_id:
            existing = db.query(Message).filter(
                Message.channel_id == channel.id,
                Message.grouped_id == grouped_id
            ).first()

        if not existing:
            existing = db.query(Message).filter(
                Message.channel_id == channel.id,
                Message.telegram_message_id == tg_msg_id
            ).first()

        if not existing:

            new_msg = Message(
                channel_id=channel.id,
                telegram_message_id=tg_msg_id,
                grouped_id=grouped_id,
                text=message_data.get('text'),
                views=message_data.get('views', 0),
                forwards=message_data.get('forwards', 0),
                has_media=1 if message_data.get('has_media') else 0,
                media_type=message_data.get('media_type'),
                media_path=message_data.get('media_path'),
                telegram_date=datetime.fromisoformat(message_data.get('date')) if message_data.get('date') else datetime.utcnow()
            )
            db.add(new_msg)
            db.flush()
            existing = new_msg
            logger.info(f"Persisted new message {tg_msg_id} from @{username}")
        else:
            existing.views = message_data.get('views', existing.views)
            existing.forwards = message_data.get('forwards', existing.forwards)
            if not existing.text and message_data.get('text'):
                existing.text = message_data.get('text')
            db.flush()

        if message_data.get('has_media') and message_data.get('media_path'):
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
