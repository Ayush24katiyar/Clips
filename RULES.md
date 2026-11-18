# Rules — Conventions

## Layering

`router → controller → service → pipeline stage → model/DB`

- **Routers** parse requests, call one controller, return a schema. No logic.
- **Controllers** own business rules, transactions, and stage ordering.
- **Services** wrap external systems (Groq, yt-dlp, FFmpeg, YouTube/Twitch APIs).
- **Pipeline stages** are pure-ish functions: `(JobContext) -> JobContext`, with progress callbacks.
- **Models** are SQLAlchemy ORM; **schemas** are Pydantic DTOs at every boundary.

## Python

- Python 3.12; full type hints; `from __future__ import annotations` in new modules.
- Async FastAPI endpoints; blocking FFmpeg/yt-dlp work runs in Celery workers, not the event loop.
- Pydantic v2 for all request/response/LLM schemas. Use `model_validate` with strict JSON.
- One class per file for services/controllers; module-level functions for small utilities.
- Errors: define typed exceptions in `core/errors.py`; catch at router level and map to HTTP codes.
- Logging: `logger = logging.getLogger(__name__)`; include `job_id` in every log line.
- Config: `core/config.py` using `pydantic-settings`; env vars only.
- Tests: one test file per service/stage; mock external APIs; no network in unit tests.
- Lint/format: ruff (line length 100, rules E/F/I/UP/B). Run before finishing.

## Frontend

- TypeScript strict; functional components only; no class components.
- All API calls in `frontend/src/lib/api.ts`; components never hardcode URLs.
- Server state via TanStack Query; local UI state via `useState`/Zustand.
- Tailwind for styling; shadcn/ui primitives; no inline CSS unless dynamic values require it.
- Route folders under `src/app`; shared UI in `src/components`.
- `npx tsc --noEmit` must pass.

## Pipeline

- Stage order is fixed: `ingest → transcribe → analyze → select → render → package → thumbnail`.
- Every stage writes its result to `JobContext.artifacts` and emits progress `[stage, percent]`.
- Stages must be idempotent: re-running with the same inputs overwrites its own artifacts only.
- Persist transcripts and scores so a re-render never re-calls Groq.

## Data

- Alembic migrations for every schema change; descriptive revision messages.
- Timestamps in UTC; durations in seconds (float); file sizes in bytes.
- Foreign keys with cascading deletes; no orphan clips.

## Commits

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- One logical change per commit; never mix generated files with source.
