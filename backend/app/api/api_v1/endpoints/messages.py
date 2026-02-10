from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.models.message import Message
from app.services import telegram as tg

router = APIRouter()


class MediaItem(BaseModel):
    type: str
    url: str


class MessageResponse(BaseModel):
    id: int
    channel_username: str
    channel_title: str
    text: str
    views: int
    forwards: int
    date: str
    is_demo: Optional[bool] = False
    has_media: Optional[bool] = False
    media_type: Optional[str] = None # Keeping for backward compatibility
    media_url: Optional[str] = None  # Keeping for backward compatibility
    media: List[MediaItem] = []


@router.get("", response_model=List[MessageResponse])
def get_messages(
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Get messages from database for consistent pagination"""
    db_messages = (
        db.query(Message)
        .order_by(Message.telegram_date.desc(), Message.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    responses = []
    for msg in db_messages:
        media_items = []
        for m in (msg.media or []):
            media_items.append(MediaItem(
                type=m.media_type,
                url=f"/media/{m.media_path}"
            ))
            
        responses.append(MessageResponse(
            id=msg.telegram_message_id,
            channel_username=msg.channel.username if msg.channel else '',
            channel_title=msg.channel.title if msg.channel else '',
            text=msg.text or '',
            views=msg.views or 0,
            forwards=msg.forwards or 0,
            date=(msg.telegram_date.isoformat() if msg.telegram_date else msg.created_at.isoformat()) + "Z",
            is_demo=False,
            has_media=bool(msg.has_media or media_items),
            media_type=msg.media_type,
            media_url=f"/media/{msg.media_path}" if msg.media_path else (media_items[0].url if media_items else None),
            media=media_items
        ))
    
    return responses


@router.get("/status")
def get_telegram_status():
    """Get Telegram service status"""
    if not tg.telegram_service:
        return {"status": "not_initialized", "demo_mode": True}
    
    return {
        "status": "running",
        "demo_mode": tg.telegram_service.is_demo_mode,
        "messages_buffered": len(tg.telegram_service.messages),
        "channels_count": len(tg.telegram_service.channels)
    }
