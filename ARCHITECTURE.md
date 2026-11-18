# Architecture — ClipForge

## System

```
Browser (Next.js 16)
   │  REST + SSE progress
   ▼
FastAPI (api) ──► Redis (broker/cache) ──► Celery workers
   │                                           │
   │  SQLAlchemy                                │  FFmpeg / yt-dlp / Groq
   ▼                                           ▼
PostgreSQL 16                            storage/ (sources, clips, thumbs, captions)
```

Services in `docker-compose.yml`: `frontend`, `api`, `worker`, `redis`, `db`.

## Pipeline (Celery job)

```
1. ingest      yt-dlp best format (≤4K, cookies) → ffprobe metadata
2. transcribe  extract 16kHz mono FLAC → chunk → Groq whisper-large-v3-turbo
               (verbose_json, word + segment timestamps) → merge offsets
3. analyze     Groq gpt-oss-20b JSON: candidate moments, virality score, titles
               + local signals: silence, loudness, energy, scene cuts, face peaks
4. select      in-point at visual/emotional peak ±3s, end on reaction, 15–90s
5. render      CRF 17 x264 (final) or NVENC (draft) → face-tracked 9:16 crop
               → ASS caption burn-in → −14 LUFS loudness normalisation
6. package     MP4 (+faststart) + WebM/VP9 optional + SRT/VTT + metadata JSON
7. thumbnail   peak frame + title overlay → JPG/PNG
```

Provider switch in `.env`: `AI_PROVIDER=groq` (default) | `local` (faster-whisper + Ollama).

## Modules

| Path | Responsibility |
|---|---|
| `core/config.py` | typed settings from `.env` |
| `core/events.py` | SSE progress bus |
| `db/` | session, base, Alembic migrations |
| `models/` | User, Source, Job, Clip, Caption, Thumbnail, Streamer, StreamerMetric |
| `schemas/` | Pydantic DTOs incl. LLM output schemas |
| `controllers/` | job, clip, caption, thumbnail, discovery business logic |
| `routers/` | `jobs`, `clips`, `uploads`, `captions`, `thumbnails`, `discover`, `events` |
| `services/` | downloader, groq_client, transcriber, analyzer, scorer, ffmpeg_service, captions_service, thumbnail_service, discovery_service, storage_service |
| `pipeline/` | orchestrator + ordered stages + prompt templates |
| `workers/` | Celery app and tasks |
| `utils/` | ffprobe, chunker, time, paths |

## Database (initial schema)

- `users` — id, email, created_at (single local user in v1).
- `sources` — id, url, platform, video_id, title, duration, source_path, height, fetched_at.
- `jobs` — id, source_id, status, stage, progress, quality_mode, params(JSON), error, created_at, finished_at.
- `clips` — id, job_id, start, end, score, ratio, file_path, webm_path, width, height, crf, title, description.
- `captions` — id, clip_id, format(srt/vtt/ass), text, words(JSON with start/end).
- `thumbnails` — id, clip_id, path, frame_time.
- `streamers` — id, platform, external_id, name, country, category, channel_url, avatar_url.
- `streamer_metrics` — id, streamer_id, views, followers, rank, captured_at.

## Discovery data sources

- YouTube Data API v3: `videos.list(chart=mostPopular, regionCode=<country>)`.
- Twitch Helix: `/helix/streams`, `/helix/games/top` with app token.
- Daily snapshot job stores deltas; no scraping of fragile third-party trackers.

## Extension points

- Add a provider by implementing the `AIProvider` protocol in `services/groq_client.py`.
- Add a pipeline stage by creating `pipeline/stages/<name>.py` and registering it in `pipeline/pipeline.py`.
- Add an output format in `services/ffmpeg_service.py` + `QUALITY.md`.
