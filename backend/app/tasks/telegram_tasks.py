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
    Persist a telegram message to the database.
    message_data expected keys:
      - channel_username: str
      - id: int (telegram_message_id)
      - text: str
      - views: int
      - forwards: int
      - date: str (isoformat)
    """
    db = SessionLocal()
    try:
        # 1. Find the channel
        username = message_data.get('channel_username', '').strip('@')
        channel = db.query(Channel).filter(Channel.username == username).first()
        
        if not channel:
            # If channel doesn't exist, we might want to create it or skip
            # For now, let's create it if we have at least a title
            channel = Channel(
                username=username,
                title=message_data.get('channel_title', username),
                is_active=True
            )
            db.add(channel)
            db.flush() # Get the ID
            
        # 2. Check if message already exists (to avoid duplicates)
        tg_msg_id = message_data.get('id')
        
        # We use a try-except block for the entire creation to handle race conditions via UniqueConstraint
        try:
            # Check if exists first to avoid unnecessary inserts/errors
            existing = db.query(Message).filter(
                Message.channel_id == channel.id,
                Message.telegram_message_id == tg_msg_id
            ).first()
            
            if not existing:
                # 3. Create the message
                new_msg = Message(
                    channel_id=channel.id,
                    telegram_message_id=tg_msg_id,
                    text=message_data.get('text'),
                    views=message_data.get('views', 0),
                    forwards=message_data.get('forwards', 0),
                    telegram_date=datetime.fromisoformat(message_data.get('date')) if message_data.get('date') else datetime.utcnow()
                )
                db.add(new_msg)
                db.commit()
                logger.info(f"Persisted new message {tg_msg_id} from @{username}")
            else:
                # Optional: Update views/forwards if it already exists
                existing.views = message_data.get('views', existing.views)
                existing.forwards = message_data.get('forwards', existing.forwards)
                db.commit()
                logger.debug(f"Updated existing message {tg_msg_id} from @{username}")
                
        except Exception as e:
            db.rollback()
            # If it's a unique constraint error, we can ignore it (message already exists)
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                logger.debug(f"Message {tg_msg_id} already being persisted by another task")
            else:
                raise e
            
    except Exception as e:
        logger.error(f"Error persisting telegram message: {e}")
        db.rollback()
    finally:
        db.close()
