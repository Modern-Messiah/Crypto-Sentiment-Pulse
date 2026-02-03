from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.db.base import Base

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
