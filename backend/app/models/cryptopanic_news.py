from sqlalchemy import Column, Integer, String, Text, DateTime, UniqueConstraint
from datetime import datetime
from app.db.base import Base


class CryptoPanicNews(Base):
    __tablename__ = "cryptopanic_news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    kind = Column(String, default="news")
    source_title = Column(String, nullable=True)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('title', 'published_at', name='_title_published_uc'),
    )
