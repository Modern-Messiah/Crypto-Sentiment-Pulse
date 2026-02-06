import os
import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Optional
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


# Check if Telethon is available
try:
    from telethon import TelegramClient, events
    from telethon.tl.functions.channels import GetFullChannelRequest
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logger.warning("Telethon not installed. Telegram integration will use demo mode.")


class TelegramService:
    """
    Service for monitoring Telegram channels.
    Falls back to demo mode if Telethon is not available or credentials are missing.
    """
    
    def __init__(self, api_id: Optional[int], api_hash: Optional[str], session_name: str = "crypto_bot"):
        self.api_id = api_id
        self.api_hash = api_hash
        
        # Ensure session directory exists
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # This is 'app' dir
        session_dir = os.path.join(base_dir, "data", "sessions")
        if not os.path.exists(session_dir):
            os.makedirs(session_dir, exist_ok=True)
            logger.info(f"Created session directory: {session_dir}")
        
        self.session_path = os.path.join(session_dir, session_name)
        self.session_name = session_name
        self.client: Optional['TelegramClient'] = None
        self._running = False
        self.messages = deque(maxlen=500)  # Last 500 messages for WebSocket
        self.channels = {}  # channel_username -> channel_info
        self.channels_by_id = {}
        self._message_callback = None
        self._demo_mode = not TELETHON_AVAILABLE or not api_id or not api_hash
        
        if self._demo_mode:
            logger.info("Telegram service running in DEMO mode")
    
    def set_message_callback(self, callback):
        """Set a callback for real-time message notifications"""
        self._message_callback = callback

    @property
    def is_demo_mode(self) -> bool:
        return self._demo_mode
    
    async def start(self, channel_usernames: list[str]):
        """Start monitoring channels"""
        if self._demo_mode:
            logger.info("Demo mode: Not connecting to Telegram")
            self._running = True
            asyncio.create_task(self._generate_demo_messages())
            return
        
        try:
            loop = asyncio.get_event_loop()
            self.client = TelegramClient(self.session_path, self.api_id, self.api_hash, loop=loop)
            
            # Explicitly add event handlers BEFORE start
            self.channels_by_id = {info['id']: username for username, info in self.channels.items()}
            logger.info(f"Registering handlers for {len(self.channels)} channels.")
            
            self.client.add_event_handler(self._new_message_handler, events.NewMessage())
            self.client.add_event_handler(self._edit_message_handler, events.MessageEdited())
            self.client.add_event_handler(self._raw_update_handler, events.Raw())

            await self.client.start()
            logger.info("Connected and authorized in Telegram!")
            
            # Start background listener task
            asyncio.create_task(self.client.run_until_disconnected())
            logger.info("Telethon background listener task started.")
            
            # Subscribe to channels (ensure entities are loaded)
            for username in channel_usernames:
                try:
                    await self._subscribe_channel(username)
                except Exception as e:
                    logger.error(f"Failed to subscribe to {username}: {e}")
            
            # Sync state to "kickstart" updates
            logger.info("Syncing dialogs to activate update stream...")
            await self.client.get_dialogs(limit=10)
            
            # Fetch initial history
            logger.info("Fetching initial history...")
            await self._fetch_initial_history()
            
            self._running = True
            logger.info(f"Telegram monitoring fully active.")
            
            # Start heartbeat
            asyncio.create_task(self._heartbeat())
            
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}", exc_info=True)
            self._demo_mode = True
            asyncio.create_task(self._generate_demo_messages())

    async def _new_message_handler(self, event):
        """Internal handler for NewMessage events"""
        chat_id = event.chat_id
        tg_id = chat_id
        if str(tg_id).startswith('-100'):
            tg_id = int(str(tg_id)[4:])
        
        if tg_id in self.channels_by_id:
            logger.info(f"EVENT: NewMessage from {self.channels_by_id[tg_id]} ({chat_id})")
            await self._handle_message(event)

    async def _edit_message_handler(self, event):
        """Internal handler for MessageEdited events"""
        chat_id = event.chat_id
        tg_id = chat_id
        if str(tg_id).startswith('-100'):
            tg_id = int(str(tg_id)[4:])
        
        if tg_id in self.channels_by_id:
            logger.info(f"EVENT: MessageEdited from {self.channels_by_id[tg_id]} ({chat_id})")
            await self._handle_message(event, is_edit=True)

    async def _raw_update_handler(self, event):
        """Low-level handler for ALL Telegram updates"""
        try:
            update_type = type(event).__name__
            logger.debug(f"RAW_UPDATE: {update_type}")
        except:
            pass

    async def _heartbeat(self):
        """Log status periodicially to confirm the service is alive"""
        while self._running:
            try:
                if self.client and await self.client.is_user_authorized():
                    me = await self.client.get_me()
                    isConnected = self.client.is_connected()
                    
                    # Manual Poll as fallback
                    for username, info in self.channels.items():
                        try:
                            # Fetch only the latest message
                            msgs = await self.client.get_messages(info['id'], limit=1)
                            if msgs:
                                m = msgs[0]
                                # Check if we already have this message ID in our buffer
                                if not any(msg['id'] == m.id and msg['channel_username'] == username for msg in self.messages):
                                    logger.info(f"POLL: Found new message from @{username}")
                                    await self._process_raw_message(m, username, info['title'])
                        except Exception as poll_e:
                            logger.error(f"Poll error for {username}: {poll_e}")

                    logger.info(f"Telegram heartbeat: Connected={isConnected}, User={me.username}, Buffer={len(self.messages)}")
                else:
                    logger.warning("Telegram heartbeat: Client not authorized")
            except Exception as e:
                logger.error(f"Telegram heartbeat error: {e}")
            await asyncio.sleep(10) # More frequent heartbeat

    async def _fetch_initial_history(self):
        """Fetch the last messages from each monitored channel"""
        for username, info in self.channels.items():
            try:
                # Get last 3 messages to ensure we get some content
                messages = await self.client.get_messages(info['id'], limit=3)
                for msg in messages:
                    # Use provided text/caption or fallback
                    text_content = msg.text or msg.message or ""
                    if not text_content:
                        if msg.photo or msg.video or msg.document:
                             text_content = "[Media Content]"
                        elif msg.poll:
                             text_content = f"[Poll: {msg.poll.poll.question}]"
                        elif msg.venue or msg.geo:
                             text_content = "[Location/Venue]"
                        else:
                             text_content = "[Message]" # Fallback for any content
                    
                    parsed_msg = {
                        'id': msg.id,
                        'channel_username': username,
                        'channel_title': info['title'],
                        'text': text_content,
                        'views': getattr(msg, 'views', 0) or 0,
                        'forwards': getattr(msg, 'forwards', 0) or 0,
                        'date': msg.date.isoformat() if msg.date else datetime.utcnow().isoformat() + "Z",
                        'timestamp': datetime.utcnow().isoformat() + "Z"
                    }
                    self.messages.appendleft(parsed_msg)
                    
                    # Persist to DB
                    celery_app.send_task(
                        "app.tasks.telegram_tasks.persist_telegram_message",
                        args=[parsed_msg]
                    )
            except Exception as e:
                logger.error(f"Could not fetch history for {username}: {e}")

    
    async def _subscribe_channel(self, username: str):
        """Subscribe to a channel and get its info"""
        try:
            entity = await self.client.get_entity(username)
            full = await self.client(GetFullChannelRequest(entity))
            
            self.channels[username] = {
                'id': entity.id,
                'entity': entity,
                'username': username,
                'title': entity.title,
                'subscribers': full.full_chat.participants_count or 0
            }
            
            logger.info(f"Subscribed to @{username} (ID: {entity.id}, {full.full_chat.participants_count} subscribers)")
            
        except Exception as e:
            logger.error(f"Error subscribing to {username}: {e}")
            raise
    
    async def _handle_message(self, event, is_edit=False):
        """Handle incoming message from channel (Event-driven)"""
        try:
            chat_id = event.chat_id
            tg_id = chat_id
            if str(tg_id).startswith('-100'):
                tg_id = int(str(tg_id)[4:])
                
            username = self.channels_by_id.get(tg_id, "unknown")
            info = self.channels.get(username, {})
            title = info.get('title', 'Unknown')
            
            await self._process_raw_message(event, username, title, is_edit)
            
        except Exception as e:
            logger.error(f"Error handling message event: {e}", exc_info=True)

    async def _process_raw_message(self, msg_or_event, username: str, title: str, is_edit: bool = False):
        """Common logic to process a message object or event"""
        try:
            # Extract content
            text_content = getattr(msg_or_event, 'text', '') or getattr(msg_or_event, 'message', '') or ''
            
            if not text_content:
                if getattr(msg_or_event, 'photo', None) or getattr(msg_or_event, 'video', None) or getattr(msg_or_event, 'document', None):
                    text_content = "[Media Content]"
                elif getattr(msg_or_event, 'poll', None):
                    text_content = f"[Poll: {msg_or_event.poll.poll.question}]"
                elif getattr(msg_or_event, 'venue', None) or getattr(msg_or_event, 'geo', None):
                    text_content = "[Location/Venue]"
                else:
                    text_content = "[New Update]"

            parsed_msg = {
                'id': msg_or_event.id,
                'channel_username': username,
                'channel_title': title,
                'text': text_content,
                'views': getattr(msg_or_event, 'views', 0) or 0,
                'forwards': getattr(msg_or_event, 'forwards', 0) or 0,
                'date': msg_or_event.date.isoformat() if hasattr(msg_or_event, 'date') and msg_or_event.date else datetime.utcnow().isoformat() + "Z",
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'is_edit': is_edit
            }
            
            # Update deque
            if is_edit:
                for i, m in enumerate(self.messages):
                    if m['id'] == parsed_msg['id']:
                        self.messages[i] = parsed_msg
                        break
                else:
                    self.messages.appendleft(parsed_msg)
            else:
                # Avoid duplicates even for polling
                if not any(m['id'] == parsed_msg['id'] and m['channel_username'] == username for m in self.messages):
                    self.messages.appendleft(parsed_msg)
                else:
                    return # Duplicate
            
            # Persist to DB
            celery_app.send_task(
                "app.tasks.telegram_tasks.persist_telegram_message",
                args=[parsed_msg]
            )
            
            # Trigger real-time callback
            if self._message_callback:
                asyncio.create_task(self._message_callback(parsed_msg))
            
            logger.info(f"Processed {'edit' if is_edit else 'msg'} from @{username}: {text_content[:50]}...")

        except Exception as e:
            logger.error(f"Error processing raw message: {e}", exc_info=True)
    
    async def _generate_demo_messages(self):
        """Generate demo messages for testing"""
        import random
        
        demo_channels = [
            {'username': 'bitcoin', 'title': 'Bitcoin'},
            {'username': 'ethereum', 'title': 'Ethereum'},
            {'username': 'whale_alert', 'title': '🐳 Whale Alert'},
            {'username': 'CoinDesk', 'title': 'CoinDesk'},
        ]
        
        demo_texts = [
            "🚀 BTC looking strong today! Bulls are back in control.",
            "⚠️ Large transfer detected: 1,500 BTC moved from unknown wallet to Binance",
            "📊 ETH just broke key resistance at $3,500. Next target: $4,000",
            "🔥 Breaking: Major crypto exchange announces new listings",
            "💰 Whale alert: 50,000,000 USDT transferred to Coinbase",
            "📈 Market sentiment turning bullish as BTC holds above $95K",
            "🌐 Crypto adoption continues to grow in emerging markets",
            "⚡ Lightning Network capacity reaches new ATH",
        ]
        
        while self._running:
            await asyncio.sleep(random.uniform(5, 15))  # Random interval 5-15 seconds
            
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
    
    def get_messages(self, limit: int = 20, skip: int = 0) -> list:
        """Get recent messages sorted by date (newest first)"""
        # Convert to list and sort
        all_msgs = list(self.messages)
        # Parse date string to compare? Dates are ISO strings, so string comparison works (mostly)
        # But better to rely on 'date' field being ISO8601
        
        all_msgs.sort(key=lambda x: x['date'], reverse=True)
        return all_msgs[skip : skip + limit]
    
    def get_latest_message(self) -> Optional[dict]:
        """Get the most recent message"""
        return self.messages[0] if self.messages else None
    
    async def add_channel(self, username: str) -> dict:
        """Add a new channel to monitor"""
        if self._demo_mode:
            return {
                'username': username,
                'title': username.title(),
                'subscribers': 0,
                'is_demo': True
            }
        
        await self._subscribe_channel(username)
        return self.channels.get(username)
    
    async def close(self):
        """Close Telegram connection"""
        self._running = False
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")


# Global instance
telegram_service: Optional[TelegramService] = None


async def init_telegram_service(
    api_id: Optional[int],
    api_hash: Optional[str],
    session_name: str,
    channels: list[str]
) -> TelegramService:
    """Initialize the Telegram service"""
    global telegram_service
    
    telegram_service = TelegramService(api_id, api_hash, session_name)
    await telegram_service.start(channels)
    
    return telegram_service
