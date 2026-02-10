import os
import asyncio
import logging
from collections import deque
from datetime import datetime
from typing import Optional
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


try:
    from telethon import TelegramClient, events
    from telethon.tl.functions.channels import GetFullChannelRequest
    TELETHON_AVAILABLE = True
except ImportError:
    TELETHON_AVAILABLE = False
    logger.warning("Telethon not installed. Telegram integration will use demo mode.")


class TelegramService:
    
    def __init__(self, api_id: Optional[int], api_hash: Optional[str], session_name: str = "crypto_bot"):
        self.api_id = api_id
        self.api_hash = api_hash
        
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
        self.processing_ids = set() # Set of (channel, msg_id) currently being processed
        self._message_callback = None
        self._demo_mode = not TELETHON_AVAILABLE or not api_id or not api_hash
        
        if self._demo_mode:
            logger.info("Telegram service running in DEMO mode")
    
    def set_message_callback(self, callback):
        self._message_callback = callback

    @property
    def is_demo_mode(self) -> bool:
        return self._demo_mode
    
    async def start(self, channel_usernames: list[str]):
        if self._demo_mode:
            logger.info("Demo mode: Not connecting to Telegram")
            self._running = True
            asyncio.create_task(self._generate_demo_messages())
            return
        
        try:
            loop = asyncio.get_event_loop()
            self.client = TelegramClient(self.session_path, self.api_id, self.api_hash, loop=loop)
            
            self.channels_by_id = {info['id']: username for username, info in self.channels.items()}
            logger.info(f"Registering handlers for {len(self.channels)} channels.")
            
            self.client.add_event_handler(self._new_message_handler, events.NewMessage())
            self.client.add_event_handler(self._edit_message_handler, events.MessageEdited())
            self.client.add_event_handler(self._raw_update_handler, events.Raw())

            await self.client.start()
            logger.info("Connected and authorized in Telegram!")
            
            asyncio.create_task(self.client.run_until_disconnected())
            logger.info("Telethon background listener task started.")
            
            for username in channel_usernames:
                try:
                    await self._subscribe_channel(username)
                except Exception as e:
                    logger.error(f"Failed to subscribe to {username}: {e}")
            
            logger.info("Syncing dialogs to activate update stream...")
            await self.client.get_dialogs(limit=10)
            
            logger.info("Fetching initial history...")
            await self._fetch_initial_history()
            
            self._running = True
            logger.info(f"Telegram monitoring fully active.")
            
            asyncio.create_task(self._heartbeat())
            
        except Exception as e:
            logger.error(f"Failed to start Telegram client: {e}", exc_info=True)
            self._demo_mode = True
            asyncio.create_task(self._generate_demo_messages())

    async def _new_message_handler(self, event):
        chat_id = event.chat_id
        tg_id = chat_id
        if str(tg_id).startswith('-100'):
            tg_id = int(str(tg_id)[4:])
        
        if tg_id in self.channels_by_id:
            logger.info(f"EVENT: NewMessage from {self.channels_by_id[tg_id]} ({chat_id})")
            await self._handle_message(event)

    async def _edit_message_handler(self, event):
        chat_id = event.chat_id
        tg_id = chat_id
        if str(tg_id).startswith('-100'):
            tg_id = int(str(tg_id)[4:])
        
        if tg_id in self.channels_by_id:
            logger.info(f"EVENT: MessageEdited from {self.channels_by_id[tg_id]} ({chat_id})")
            await self._handle_message(event, is_edit=True)

    async def _raw_update_handler(self, event):
        try:
            update_type = type(event).__name__
            logger.debug(f"RAW_UPDATE: {update_type}")
        except:
            pass

    async def _heartbeat(self):
        while self._running:
            try:
                if self.client and await self.client.is_user_authorized():
                    me = await self.client.get_me()
                    isConnected = self.client.is_connected()
                    
                    for username, info in self.channels.items():
                        try:
                            msgs = await self.client.get_messages(info['id'], limit=1)
                            if msgs:
                                m = msgs[0]
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
            await asyncio.sleep(10)

    async def _fetch_initial_history(self):
        for username, info in self.channels.items():
            try:
                messages = await self.client.get_messages(info['id'], limit=3)
                for msg in messages:
                    text_content = msg.text or msg.message or ""
                    if not text_content:
                        if msg.photo or msg.video or msg.document:
                             text_content = "[Media Content]"
                        elif msg.poll:
                             text_content = f"[Poll: {msg.poll.poll.question}]"
                        elif msg.venue or msg.geo:
                             text_content = "[Location/Venue]"
                        else:
                             text_content = "[Message]"
                    
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
                    
                    celery_app.send_task(
                        "app.tasks.telegram_tasks.persist_telegram_message",
                        args=[parsed_msg]
                    )
            except Exception as e:
                logger.error(f"Could not fetch history for {username}: {e}")

    
    async def _subscribe_channel(self, username: str):
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
                    # Skip service messages or empty updates we don't recognize
                    logger.debug(f"Skipping empty/service update from @{username}")
                    return

            # Extract grouped_id for albums
            grouped_id = getattr(msg_or_event, 'grouped_id', None)
            
            # 1. Early De-duplication Check
            msg_key = (username, msg_or_event.id)
            if msg_key in self.processing_ids:
                logger.debug(f"Skipping: Message {msg_or_event.id} from @{username} is already being processed")
                return
            
            # 2. Check for album grouping (grouped_id)
            existing_in_buffer = None
            if grouped_id:
                # Look for an existing message in our buffer with the same grouped_id
                for m in self.messages:
                    if m.get('grouped_id') == grouped_id and m.get('channel_username') == username:
                        existing_in_buffer = m
                        break
            
            # If not an album or first message in album, check for normal duplicate
            if not existing_in_buffer and not is_edit:
                if any(m['id'] == msg_or_event.id and m['channel_username'] == username for m in self.messages):
                    logger.debug(f"Skipping: Message {msg_or_event.id} from @{username} already in buffer")
                    return
            
            # Start processing
            self.processing_ids.add(msg_key)
            
            try:
                # Media handling
                has_media = False
                media_type = None
                media_path = None
                
                if not self._demo_mode:
                    try:
                        if getattr(msg_or_event, 'photo', None):
                            has_media = True
                            media_type = 'photo'
                        elif getattr(msg_or_event, 'video', None):
                            has_media = True
                            media_type = 'video'
                        elif getattr(msg_or_event, 'document', None):
                            doc = msg_or_event.document
                            is_gif = any(isinstance(attr, (getattr(events, 'DocumentAttributeAnimated', object), object)) 
                                        for attr in doc.attributes)
                            if 'video' in doc.mime_type or is_gif:
                                has_media = True
                                media_type = 'gif' if is_gif else 'video'
                        
                        if has_media:
                            media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "media")
                            if not os.path.exists(media_dir):
                                os.makedirs(media_dir, exist_ok=True)
                            
                            ext = '.jpg' if media_type == 'photo' else '.mp4'
                            filename = f"{username}_{msg_or_event.id}{ext}"
                            full_path = os.path.join(media_dir, filename)
                            
                            if not os.path.exists(full_path):
                                logger.info(f"Downloading media for message {msg_or_event.id} from @{username}...")
                                await self.client.download_media(msg_or_event, file=full_path)
                            
                            media_path = filename
                    except Exception as media_e:
                        logger.error(f"Error downloading media: {media_e}")

                parsed_msg = {
                    'id': msg_or_event.id,
                    'channel_username': username,
                    'channel_title': title,
                    'text': text_content,
                    'views': getattr(msg_or_event, 'views', 0) or 0,
                    'forwards': getattr(msg_or_event, 'forwards', 0) or 0,
                    'date': msg_or_event.date.isoformat() if hasattr(msg_or_event, 'date') and msg_or_event.date else datetime.utcnow().isoformat() + "Z",
                    'timestamp': datetime.utcnow().isoformat() + "Z",
                    'is_edit': is_edit,
                    'grouped_id': grouped_id,
                    'has_media': has_media,
                    'media_type': media_type,
                    'media_path': media_path,
                    'media_list': [] # Will be populated by frontend or merged here
                }
                
                # If it's part of an album, merge it into the existing message in buffer
                if existing_in_buffer:
                    # Update text if current part has text and existing doesn't
                    if not existing_in_buffer.get('text') and text_content:
                        existing_in_buffer['text'] = text_content
                    # Ensure media_list exists and append current media
                    if 'media_list' not in existing_in_buffer:
                        existing_in_buffer['media_list'] = []
                    
                    if has_media and media_path:
                        # Add to list if not already there
                        if not any(item['path'] == media_path for item in existing_in_buffer['media_list']):
                            existing_in_buffer['media_list'].append({
                                'type': media_type,
                                'path': media_path,
                                'url': f"/media/{media_path}"
                            })
                    
                    # Also update legacy fields for compatibility
                    if not existing_in_buffer.get('media_path'):
                        existing_in_buffer['has_media'] = has_media
                        existing_in_buffer['media_type'] = media_type
                        existing_in_buffer['media_path'] = media_path

                    # Broadcast the update
                    if self._message_callback:
                        asyncio.create_task(self._message_callback(existing_in_buffer))
                else:
                    # New message
                    if has_media and media_path:
                        parsed_msg['media_list'] = [{
                            'type': media_type,
                            'path': media_path,
                            'url': f"/media/{media_path}"
                        }]
                    
                    # Update buffer
                    if is_edit:
                        for i, m in enumerate(self.messages):
                            if m['id'] == parsed_msg['id']:
                                self.messages[i] = parsed_msg
                                break
                        else:
                            self.messages.appendleft(parsed_msg)
                    else:
                        self.messages.appendleft(parsed_msg)

                    # Broadcast the update
                    if self._message_callback:
                        asyncio.create_task(self._message_callback(parsed_msg))

                # Persist to DB (Celery task will handle grouping in the DB)
                celery_app.send_task(
                    "app.tasks.telegram_tasks.persist_telegram_message",
                    args=[parsed_msg]
                )
                
                logger.info(f"Processed {'edit' if is_edit else 'msg'} from @{username}: {text_content[:50]}...")
            finally:
                self.processing_ids.discard(msg_key)

        except Exception as e:
            logger.error(f"Error processing raw message: {e}", exc_info=True)
    
    async def _generate_demo_messages(self):
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
        all_msgs = list(self.messages)
        
        all_msgs.sort(key=lambda x: x['date'], reverse=True)
        return all_msgs[skip : skip + limit]
    
    def get_latest_message(self) -> Optional[dict]:
        """Get the most recent message"""
        return self.messages[0] if self.messages else None
    
    async def add_channel(self, username: str) -> dict:
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

        self._running = False
        if self.client:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")


telegram_service: Optional[TelegramService] = None


async def init_telegram_service(
    api_id: Optional[int],
    api_hash: Optional[str],
    session_name: str,
    channels: list[str]
) -> TelegramService:
    global telegram_service
    
    telegram_service = TelegramService(api_id, api_hash, session_name)
    await telegram_service.start(channels)
    
    return telegram_service
