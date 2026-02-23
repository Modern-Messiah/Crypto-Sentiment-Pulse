import os
from typing import List, Optional


class Settings:
    PROJECT_NAME: str = "News Service"

    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://redis:6379/0")

    TELEGRAM_API_ID: Optional[int] = (
        int(os.environ["TELEGRAM_API_ID"])
        if os.environ.get("TELEGRAM_API_ID")
        else None
    )
    TELEGRAM_API_HASH: Optional[str] = os.environ.get("TELEGRAM_API_HASH") or None
    CRYPTOPANIC_API_TOKEN: Optional[str] = (
        os.environ.get("CRYPTOPANIC_API_TOKEN") or None
    )

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

    # Redis Pub/Sub channels
    REDIS_CHANNEL_TELEGRAM: str = "news:telegram"
    REDIS_CHANNEL_CRYPTOPANIC: str = "news:cryptopanic"

    # CryptoPanic fetch interval (seconds)
    CRYPTOPANIC_FETCH_INTERVAL: int = 21600  # 6 hours


settings = Settings()
