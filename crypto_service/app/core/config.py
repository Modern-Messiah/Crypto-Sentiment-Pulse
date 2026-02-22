import os
from typing import List


class Settings:
    PROJECT_NAME: str = "Crypto Service"

    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://user:pass@db:5432/cryptodb")
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://redis:6379/0")

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

    REDIS_CHANNEL: str = "crypto:updates"
    REDIS_PRICES_KEY: str = "crypto:prices"
    REDIS_FEAR_GREED_KEY: str = "crypto:fear_greed"


settings = Settings()
