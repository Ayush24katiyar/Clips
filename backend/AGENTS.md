# Backend instructions

- FastAPI app lives in `app/`. Router → controller → service → pipeline stage → model. Never skip layers.
- All FFmpeg/ffprobe subprocess calls only in `app/services/ffmpeg_service.py` and `app/utils/ffprobe.py`.
- All AI calls only in `app/services/groq_client.py` (or local_provider behind the same protocol).
- Validate every LLM response with a Pydantic model from `app/schemas/`.
- Use async endpoints; blocking work belongs in Celery tasks under `app/workers/`.
- Use `logger` from `app/core/logging.py`, never `print()`.
- Emit progress via `app/core/events.py` at every stage boundary.
- Typed exceptions in `app/core/errors.py`; no bare `except Exception` except at provider retry boundaries.
- Run `uv run ruff check backend` and `uv run pytest -q` before finishing.
- Follow the root `RULES.md`, `NO.md`, `QUALITY.md` and `ARCHITECTURE.md`.
