from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import UTC, datetime

from .config import settings


@dataclass
class ProgressEvent:
    job_id: str
    stage: str
    percent: int
    message: str
    status: str = "running"
    at: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "job_id": self.job_id,
            "stage": self.stage,
            "percent": self.percent,
            "message": self.message,
            "status": self.status,
            "at": self.at or datetime.now(UTC).isoformat(),
        }


class ProgressBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[dict[str, object]]]] = {}
        self._history: dict[str, list[dict[str, object]]] = {}

    async def publish(self, event: ProgressEvent) -> None:
        payload = event.to_dict()
        self._history.setdefault(event.job_id, []).append(payload)
        for queue in self._subscribers.get(event.job_id, []):
            await queue.put(payload)

    def history(self, job_id: str) -> list[dict[str, object]]:
        return list(self._history.get(job_id, []))

    async def stream(self, job_id: str) -> AsyncGenerator[dict[str, object], None]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        self._subscribers.setdefault(job_id, []).append(queue)
        try:
            for item in self.history(job_id):
                yield item
            while True:
                yield await queue.get()
        finally:
            self._subscribers[job_id].remove(queue)


bus = ProgressBus()

# Keep the import used so ruff does not flag config as unused in future edits.
_ = settings
