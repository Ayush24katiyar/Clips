---
name: Groq API
description: Groq model choices, audio chunking, word-level timestamps, structured JSON output and rate-limit handling for ClipForge. Use when changing transcription, highlight analysis, captions, or discovery AI calls.
---

# Groq API

All calls go through `backend/app/services/groq_client.py`. Key from `.env` only.

## Models (verified from Groq docs)

- `whisper-large-v3-turbo` — $0.04/audio-hour, multilingual, translation unsupported. Use for transcription.
- `whisper-large-v3` — $0.111/audio-hour, ~10.3% WER; use for error-sensitive work/translation.
- `gpt-oss-20b` — ~1000 tok/s, $0.075 in / $0.30 out per 1M. Default text model.
- `gpt-oss-120b` — ~500 tok/s, $0.15 in / $0.60 out per 1M. Upgrade for hard prompts.
- `qwen/qwen3.8-27b` — vision, up to 3 images/request, 20 MB each, JSON mode.
- `llama-3.1-8b-instant` / `llama-3.3-70b-versatile` are Enterprise/ContactSales — do not assume access.

## Transcription

```python
client.audio.transcriptions.create(
    file=audio_file,
    model="whisper-large-v3-turbo",
    response_format="verbose_json",
    timestamp_granularities=["word", "segment"],
    language=language,          # ISO-639-1, optional
    temperature=0.0,
)
```

- Preprocess: `ffmpeg -i src -ar 16000 -ac 1 -map 0:a -c:a flac audio.flac` (lossless, smaller).
- File limits: 25 MB free / 100 MB dev tier. Chunk by duration/size with 1–2 s overlap.
- Merge chunks by adding the chunk offset to every word/segment timestamp; drop overlap duplicates.
- Cache merged transcript to `storage/captions/<source_id>.json` — never re-transcribe.

## Structured text

Use JSON mode / structured outputs; validate with a Pydantic model in `backend/app/schemas/`.
Prompt for candidate moments with start/end, score, reason, title, description. Never parse raw text with string splitting.

## Rate limits & errors

- Free tier ≈ 20 RPM / 2000 RPD for Whisper; developer tier 300–400 RPM.
- Implement exponential backoff on 429/5xx with jitter; cap retries at 5.
- Set a spend limit in the Groq console.

## Privacy

Only extracted audio and transcript text leave the machine. Never upload full video files.
