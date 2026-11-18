# ClipForge

Local-first AI clipping platform. Paste a YouTube/Twitch link → ranked, captioned, high-quality vertical clips.

## Quick start

```powershell
uv sync
cp .env.example .env        # add GROQ_API_KEY
docker compose up --build
```

Open http://localhost:3000. API docs at http://localhost:8000/docs.

## Requirements

- Python 3.12+ (managed by `uv`), Node 20+, Docker Compose v2
- FFmpeg + ffprobe on PATH. Docker images include them; for local dev run `./scripts/install_ffmpeg.ps1` (winget) or set `FFMPEG_BIN` / `FFPROBE_BIN` in `.env`.
- Optional: NVIDIA GPU for face tracking / draft NVENC encoding

## Docs

- `OBJECTIVES.md` — product goals and acceptance criteria
- `ARCHITECTURE.md` — system design and DB schema
- `QUALITY.md` — media/quality policy
- `RULES.md` — coding conventions
- `NO.md` — hard prohibitions
- `RESEARCH.md` — competitive and technical research
- `AGENTS.md` — instructions for AI coding agents

## Status

Phase 0 — scaffolded architecture. Implementation in progress.
