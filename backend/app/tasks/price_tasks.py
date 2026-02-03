import os
import requests
import logging
from celery import Celery
from datetime import datetime
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.price_history import PriceHistory

logger = logging.getLogger(__name__)

celery_app = Celery(__name__, broker=settings.REDIS_URL, backend=settings.REDIS_URL)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    'save-prices-every-10-seconds': {
        'task': 'app.tasks.price_tasks.save_price_snapshot',
        'schedule': 10.0, # seconds
    },
}
celery_app.conf.timezone = 'UTC'

@celery_app.task
def save_price_snapshot():
    try:
        response = requests.get(settings.BACKEND_API_URL, timeout=5)
        if response.status_code == 200:
            data = response.json().get("data", {})
            
            db = SessionLocal()
            try:
                for symbol, price_data in data.items():
                    history_entry = PriceHistory(
                        symbol=symbol,
                        price=price_data['price'],
                        timestamp=datetime.utcnow()
                    )
                    db.add(history_entry)
                db.commit()
            except Exception as e:
                logger.error(f"DB Error in Celery: {e}")
                db.rollback()
            finally:
                db.close()
    except Exception as e:
        logger.error(f"API Error in Celery: {e}")

from app.tasks import price_tasks
