from celery import Celery
from app.core.config import settings

celery_app = Celery("worker", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.timezone = 'UTC'

celery_app.conf.beat_schedule = {
    'fetch-cryptopanic-news-every-6h': {
        'task': 'app.tasks.cryptopanic_tasks.fetch_and_persist_news',
        'schedule': 21600.0,  # 6 hours
    },
}

celery_app.autodiscover_tasks(['app.tasks.telegram_tasks', 'app.tasks.cryptopanic_tasks'])
