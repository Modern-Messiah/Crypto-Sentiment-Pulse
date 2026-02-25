from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import Optional, List

from app.db.session import get_db
from app.models.channel import Channel, ChannelPriority

router = APIRouter()


class ChannelCreate(BaseModel):
    username: str
    priority: Optional[str] = "low"


class ChannelResponse(BaseModel):
    id: int
    username: str
    title: Optional[str]
    subscribers_count: int
    priority: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=List[ChannelResponse])
def get_channels(db: Session = Depends(get_db)):
    """Get all monitored channels"""
    channels = db.query(Channel).filter(Channel.is_active == True).all()
    return channels


@router.post("", response_model=ChannelResponse)
def add_channel(channel_data: ChannelCreate, db: Session = Depends(get_db)):
    existing = db.query(Channel).filter(Channel.username == channel_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Channel already exists")

    channel = Channel(
        username=channel_data.username,
        title=channel_data.username,
        subscribers_count=0,
        priority=channel_data.priority,
        is_active=True
    )

    db.add(channel)
    db.commit()
    db.refresh(channel)

    return channel


@router.delete("/{channel_id}")
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    channel.is_active = False
    db.commit()

    return {"message": f"Channel {channel.username} removed"}
