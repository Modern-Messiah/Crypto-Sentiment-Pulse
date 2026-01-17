import os
import time
import requests
from celery import Celery
from celery.schedules import crontab
from database import SessionLocal, PriceHistory, init_db
from datetime import datetime

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000/api/prices")

celery = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

# Configure periodic tasks
celery.conf.beat_schedule = {
    'save-prices-every-10-seconds': {
        'task': 'celery_worker.save_price_snapshot',
        'schedule': 10.0, # seconds
    },
}
celery.conf.timezone = 'UTC'

@celery.task
def save_price_snapshot():
    """Fetches current prices from backend API and saves to DB"""
    try:
        response = requests.get(BACKEND_API_URL, timeout=5)
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
                # print(f"✅ Saved snapshot for {len(data)} symbols")
            except Exception as e:
                print(f"DB Error in Celery: {e}")
                db.rollback()
            finally:
                db.close()
    except Exception as e:
        print(f"API Error in Celery: {e}")

if __name__ == "__main__":
    init_db()
    # This block is for manual testing or startup
