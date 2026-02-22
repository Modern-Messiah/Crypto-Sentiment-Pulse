from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Crypto Sentiment Pulse"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "secret-key-goes-here"
    DATABASE_URL: str = "postgresql://user:pass@db:5432/cryptodb"
    REDIS_URL: str = "redis://redis:6379/0"

    TRACKED_SYMBOLS: List[str] = [
        "BTCUSDT",
        "ETHUSDT",
        "BNBUSDT",
        "ADAUSDT",
        "SOLUSDT",
        "XRPUSDT",
        "DOGEUSDT",
        "POLUSDT",
        "DOTUSDT",
        "LINKUSDT",
        "AVAXUSDT",
        "UNIUSDT",
        "LTCUSDT",
        "ARBUSDT",
        "ATOMUSDT",
        "XLMUSDT",
        "TRXUSDT",
        "ETCUSDT",
        "FILUSDT",
        "NEARUSDT",
    ]

    BACKEND_API_URL: str = "http://backend:8080/api/v1/prices"

    TELEGRAM_API_ID: Optional[int] = None
    TELEGRAM_API_HASH: Optional[str] = None
    CRYPTOPANIC_API_TOKEN: Optional[str] = None

    TELEGRAM_SESSION_NAME: str = "crypto_sentiment_bot"
    TELEGRAM_CHANNELS: List[str] = [
        "binance_ru",
        "forklog",
        "DeCenter",
        "Coin_Post",
        "binancekillers",
        "CryptoKlondike",
        "Pro_Blockchain",
        "wublockchainenglish",
        "bitcoin",
        "whale_alert",
        "CoinDesk",
        "CoinTelegraph",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
