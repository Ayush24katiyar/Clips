from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/health")
async def event_bus_health() -> dict:
    return {"ok": True, "subscribers": "in-process"}
