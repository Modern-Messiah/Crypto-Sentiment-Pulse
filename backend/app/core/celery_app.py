from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.timezone = 'UTC'

celery_app.conf.beat_schedule = {
    'save-prices-every-10-seconds': {
        'task': 'app.tasks.price_tasks.save_price_snapshot',
        'schedule': 10.0,
    },
    'fetch-cryptopanic-news-every-6h': {
        'task': 'app.tasks.cryptopanic_tasks.fetch_and_persist_news',
        'schedule': 21600.0,  # 6 hours
    },
}

celery_app.autodiscover_tasks(['app.tasks.price_tasks', 'app.tasks.telegram_tasks', 'app.tasks.cryptopanic_tasks'])
