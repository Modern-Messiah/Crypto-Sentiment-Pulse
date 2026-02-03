from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Crypto Sentiment Pulse"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "secret-key-goes-here" # Change in production
    
    # DB Settings
    DATABASE_URL: str = "postgresql://user:pass@db:5432/cryptodb"
    
    # Redis Settings
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Binance Settings
    TRACKED_SYMBOLS: List[str] = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "SOLUSDT",
        "XRPUSDT", "DOGEUSDT", "POLUSDT", "DOTUSDT", "LINKUSDT",
        "AVAXUSDT", "UNIUSDT", "LTCUSDT", "ARBUSDT", "ATOMUSDT",
        "XLMUSDT", "TRXUSDT", "ETCUSDT", "FILUSDT", "NEARUSDT",
    ]
    
    # Celery Settings
    BACKEND_API_URL: str = "http://backend:8080/api/v1/prices"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
