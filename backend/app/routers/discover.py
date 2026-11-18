from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..controllers.discovery_controller import DiscoveryController
from ..db.session import get_db

router = APIRouter(prefix="/discover", tags=["discover"])


class StreamerRead(BaseModel):
    id: str
    platform: str
    name: str
    country: str | None
    category: str | None
    channel_url: str
    avatar_url: str | None

    model_config = {"from_attributes": True}


@router.get("", response_model=list[StreamerRead])
def discover(
    country: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> list[StreamerRead]:
    return [StreamerRead.model_validate(s) for s in DiscoveryController(db).list(country, category)]


@router.post("/refresh", response_model=list[StreamerRead])
def refresh(region: str = "US", db: Session = Depends(get_db)) -> list[StreamerRead]:
    return [StreamerRead.model_validate(s) for s in DiscoveryController(db).refresh(region)]
