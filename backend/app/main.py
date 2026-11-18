from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .core.config import settings
from .core.logging import configure_logging
from .db.base import Base
from .db.session import engine
from .routers import captions, clips, discover, events, jobs, thumbnails, uploads
from .services.storage_service import StorageService

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    StorageService().ensure_dirs()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="ClipForge", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (jobs, clips, uploads, captions, thumbnails, discover, events):
    app.include_router(router.router)

app.mount("/media", StaticFiles(directory=settings.storage_root), name="media")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "provider": settings.ai_provider}
