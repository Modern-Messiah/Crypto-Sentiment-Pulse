from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    telegram_message_id = Column(BigInteger, index=True)
    
    __table_args__ = (
        UniqueConstraint('channel_id', 'telegram_message_id', name='_channel_msg_uc'),
    )
    text = Column(Text, nullable=True)
    views = Column(Integer, default=0)
    forwards = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    telegram_date = Column(DateTime, nullable=True)

    channel = relationship("Channel", backref="messages")
