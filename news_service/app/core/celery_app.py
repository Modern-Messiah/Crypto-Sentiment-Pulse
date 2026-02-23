from celery import Celery
from app.core.config import settings

# Minimal Celery client — only used for send_task(), not as a worker
celery_app = Celery("news_service", broker=settings.REDIS_URL)
