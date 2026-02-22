from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    telegram_message_id = Column(BigInteger, index=True)
    grouped_id = Column(BigInteger, nullable=True, index=True)

    __table_args__ = (
        UniqueConstraint("channel_id", "telegram_message_id", name="_channel_msg_uc"),
    )
    text = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    forwards = Column(Integer, default=0)

    has_media = Column(Integer, default=0)  # 0 or 1
    media_type = Column(String, nullable=True)
    media_path = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    telegram_date = Column(DateTime, nullable=True)

    channel = relationship("Channel", backref="messages")
    media = relationship(
        "MessageMedia", back_populates="message", cascade="all, delete-orphan"
    )


class MessageMedia(Base):
    __tablename__ = "message_media"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    media_type = Column(String, nullable=False)
    media_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    message = relationship("Message", back_populates="media")
