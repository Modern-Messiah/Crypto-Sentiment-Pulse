import asyncio
import logging
import random
from collections import deque
from datetime import datetime

logger = logging.getLogger(__name__)

class DemoGenerator:
    def __init__(self, messages_buffer: deque):
        self.messages = messages_buffer
        self._running = False

    def start(self):
        self._running = True
        logger.info("Demo mode: Not connecting to Telegram")
        asyncio.create_task(self._generate_demo_messages())

    def stop(self):
        self._running = False

    async def _generate_demo_messages(self):
        demo_channels = [
            {'username': 'bitcoin', 'title': 'Bitcoin'},
            {'username': 'ethereum', 'title': 'Ethereum'},
            {'username': 'whale_alert', 'title': 'Whale Alert'},
            {'username': 'CoinDesk', 'title': 'CoinDesk'},
        ]

        demo_texts = [
            "BTC looking strong today! Bulls are back in control.",
            "Large transfer detected: 1,500 BTC moved from unknown wallet to Binance",
            "ETH just broke key resistance at $3,500. Next target: $4,000",
            "Breaking: Major crypto exchange announces new listings",
            "Whale alert: 50,000,000 USDT transferred to Coinbase",
            "Market sentiment turning bullish as BTC holds above $95K",
            "Crypto adoption continues to grow in emerging markets",
            "Lightning Network capacity reaches new ATH",
        ]

        while self._running:
            await asyncio.sleep(random.uniform(5, 15))

            channel = random.choice(demo_channels)
            text = random.choice(demo_texts)

            msg = {
                'id': random.randint(1000, 99999),
                'channel_username': channel['username'],
                'channel_title': channel['title'],
                'text': text,
                'views': random.randint(100, 50000),
                'forwards': random.randint(0, 500),
                'date': datetime.utcnow().isoformat() + "Z",
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'is_demo': True
            }

            self.messages.appendleft(msg)
            logger.debug(f"Demo message: {text[:50]}...")
