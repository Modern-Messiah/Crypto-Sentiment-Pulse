import json
import logging

from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)

class MessagePublisher:
    def __init__(self, redis_client):
        self._redis_client = redis_client

    async def publish_to_redis(self, msg_data: dict):
        if self._redis_client:
            try:
                payload = json.dumps({
                    "type": "telegram_update",
                    "data": msg_data
                }, default=str)
                await self._redis_client.publish(settings.REDIS_CHANNEL_TELEGRAM, payload)
            except Exception as e:
                logger.error(f"Error publishing to Redis: {e}")

    def send_to_celery(self, msg_data: dict):
        try:
            celery_app.send_task(
                "app.tasks.telegram_tasks.persist_telegram_message",
                args=[json.loads(json.dumps(msg_data, default=str))]
            )
        except Exception as e:
            logger.error(f"Error sending task to Celery: {e}")
