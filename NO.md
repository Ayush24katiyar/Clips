# NO — Hard Prohibitions

These are non-negotiable. Violating any of them is a bug, not a style issue.

## Security & legal

- **NO** secrets, API keys, cookies, `.env`, or tokens in git, logs, tests, or screenshots.
- **NO** AGPL-licensed code in this repository (`vinci-clips` is reference-only). MIT/BSD/Unlicense only.
- **NO** uploading a user's local video to any third party except the configured AI provider, and only with consent. Groq receives extracted audio/metadata, never the full source video.
- **NO** bypassing YouTube/Twitch bot protections or auth walls. Use cookies only for content the user owns.

## Media quality

- **NO** delivery re-encode with CRF > 18 (default 17). Balanced mode may use CRF 21 only when explicitly selected.
- **NO** AV1 encoding — the RTX 3050 (GA106, 7th-gen NVENC) has no AV1 encoder. VP9 on CPU for WebM.
- **NO** `libx264 -crf 0` / FFV1 for delivery files — lossless masters are MKV/MOV archive only.
- **NO** stream-copy (`-c copy`) when the clip is reframed or captioned — it cannot cut on non-keyframes and cannot apply filters.
- **NO** output without `ffprobe` validation: must be playable MP4, H.264, `yuv420p`, `+faststart`, correct duration and resolution.
- **NO** stretching to 9:16. Use face-tracked crop with deadzone/smoothing, or letterbox. Never distort.
- **NO** claiming "2K vertical" from a 16:9 4K source — native vertical is ~1215x2160; 1080x1920 is the honest delivery target.

## Architecture & code

- **NO** direct ffmpeg/ffprobe subprocess calls outside `services/ffmpeg_service.py` and `utils/ffprobe.py`.
- **NO** AI/provider calls outside `services/groq_client.py` (or the provider abstraction).
- **NO** raw LLM text parsed with string splitting — use Pydantic structured output.
- **NO** business logic in routers or pipeline stages; routers are HTTP-only, stages are pure transforms.
- **NO** hardcoded paths, models, keys, CRF values, or ports — all from `core/config.py` / `.env`.
- **NO** `print()` — use `core/logging.py`.
- **NO** silent failure: every failed stage raises a typed error and emits a failed progress event.
- **NO** editing Alembic migration files after they are applied — create a new revision.
- **NO** committing generated artifacts (`storage/`, `node_modules`, `.venv`, `dist/`, build caches).

## Behaviour

- **NO** auto-posting to social platforms in v1.
- **NO** inventing quotes, comments, or captions that are not traceable to the transcript.
- **NO** heavy effects as a growth claim — packaging is a quality floor; moment selection is the lever (see `RESEARCH.md`).
