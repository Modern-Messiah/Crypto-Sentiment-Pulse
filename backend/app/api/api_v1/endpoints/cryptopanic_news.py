from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.models.cryptopanic_news import CryptoPanicNews

router = APIRouter()


class NewsResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    published_at: str
    kind: str
    source_title: Optional[str] = None
    url: Optional[str] = None


@router.get("", response_model=List[NewsResponse])
def get_news(
    limit: int = Query(default=20, le=100),
    skip: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Get CryptoPanic news from database with pagination"""
    db_news = (
        db.query(CryptoPanicNews)
        .order_by(CryptoPanicNews.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        NewsResponse(
            id=n.id,
            title=n.title,
            description=n.description,
            published_at=n.published_at.isoformat() + "Z" if n.published_at else "",
            kind=n.kind or "news",
            source_title=n.source_title,
            url=n.url,
        )
        for n in db_news
    ]
