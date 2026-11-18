# ClipForge — Agent Instructions

Local-first AI clipping platform. Paste a YouTube/Twitch link → ranked, captioned, high-quality vertical clips. Runs on one machine (RTX 3050 4GB / 16GB RAM), Groq-first AI.

## Commands

- Install: `uv sync` · activate: `.venv\Scripts\activate`
- Run API: `uv run uvicorn app.main:app --reload --app-dir backend`
- Worker: `uv run celery -A app.workers.celery_app.celery_app worker --loglevel=info --app-dir backend`
- Frontend: `cd frontend && npm run dev`
- Everything: `docker compose up --build`
- Tests: `uv run pytest -q` · Lint: `uv run ruff check backend` · Format: `uv run ruff format backend`
- Frontend check: `cd frontend && npx tsc --noEmit`

## Layout

- `backend/app/routers` — HTTP only. `controllers` — business logic. `services` — external APIs. `pipeline/stages` — ordered render steps. `models`/`schemas` — DB/Pydantic. `core` — config, logging, progress events.
- `frontend/src/app` — pages. `frontend/src/components` — UI. `frontend/src/lib/api.ts` — all backend calls.
- `storage/` — sources, clips, thumbs, captions, exports. Gitignored.
- `.opencode/skills/` — reusable agent skills. Load them when relevant.

## Conventions

- Flow: router → controller → service → pipeline stage → model. Never skip layers.
- All FFmpeg/ffprobe calls go through `services/ffmpeg_service.py` and `utils/ffprobe.py`.
- All AI calls go through `services/groq_client.py` behind a provider interface (`groq` | `local`).
- Every LLM response is parsed with Pydantic schemas; never trust raw text.
- Every job emits progress events via `core/events.py` at each stage boundary.
- Python 3.12, type hints everywhere, async endpoints, structured logging (no `print`).
- TypeScript strict mode, functional React components, server state via TanStack Query.

## Verification (required before finishing any task)

1. `uv run ruff check backend` and `uv run pytest -q`
2. `cd frontend && npx tsc --noEmit`
3. If FFmpeg/ASS/caption code changed: render a 5-second sample and run `ffprobe` on the output.
4. Update `ARCHITECTURE.md` / `QUALITY.md` when behavior changes.

## Boundaries

- Never commit `.env`, API keys, `storage/`, `.venv`, `node_modules`.
- Read `RULES.md` for conventions, `NO.md` for hard prohibitions, `QUALITY.md` for media policy, `ARCHITECTURE.md` for system design, `OBJECTIVES.md` for product goals.
- Borrow only MIT/BSD/Unlicense code. AGPL code must not enter this repository.
- User chat instructions override all files here.
