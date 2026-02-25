from datetime import datetime
import logging
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.cryptopanic_news import CryptoPanicNews

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.cryptopanic_tasks.fetch_and_persist_news")
def fetch_and_persist_news(news_list: list):
    if not news_list:
        logger.info("No news received from news_service")
        return

    db = SessionLocal()
    new_count = 0
    try:
        for item in news_list:
            title = item.get("title", "").strip()
            if not title:
                continue

            published_str = item.get("published_at")
            if not published_str:
                continue

            try:
                published_at = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                published_at = datetime.utcnow()

            existing = db.query(CryptoPanicNews).filter(
                CryptoPanicNews.title == title,
                CryptoPanicNews.published_at == published_at
            ).first()

            if existing:
                continue

            try:
                with db.begin_nested():
                    news = CryptoPanicNews(
                        title=title,
                        description=item.get("description"),
                        published_at=published_at,
                        kind=item.get("kind", "news"),
                        source_title=item.get("source", {}).get("title") if isinstance(item.get("source"), dict) else None,
                        url=item.get("url"),
                    )
                    db.add(news)
                db.flush()
                new_count += 1
            except Exception:
                db.rollback()
                logger.debug(f"Skipping duplicate news: {title}")

        db.commit()
        logger.info(f"Persisted {new_count} new CryptoPanic news items")
    except Exception as e:
        logger.error(f"Error persisting CryptoPanic news: {e}")
        db.rollback()
    finally:
        db.close()
