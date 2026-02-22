import os
from typing import List


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

# Redis channels / keys
REDIS_CHANNEL = "crypto:updates"
REDIS_PRICES_KEY = "crypto:prices"
REDIS_FEAR_GREED_KEY = "crypto:fear_greed"
