from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.timezone = 'UTC'

# Configure periodic tasks (Beat)
celery_app.conf.beat_schedule = {
    'save-prices-every-10-seconds': {
        'task': 'app.tasks.price_tasks.save_price_snapshot',
        'schedule': 10.0, # seconds
    },
}

celery_app.autodiscover_tasks(['app.tasks.price_tasks', 'app.tasks.telegram_tasks'])
