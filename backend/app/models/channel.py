from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from datetime import datetime
import enum
from app.db.base import Base


class ChannelPriority(str, enum.Enum):
    HIGH = "high"
    LOW = "low"


class Channel(Base):
    __tablename__ = "channels"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=True)
    subscribers_count = Column(Integer, default=0)
    priority = Column(String, default=ChannelPriority.LOW.value)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched_at = Column(DateTime, nullable=True)
