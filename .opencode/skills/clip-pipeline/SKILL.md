---
name: Clip Pipeline
description: How ClipForge's seven-stage job pipeline works and how to add or modify a stage safely. Use when changing pipeline orchestration, stage contracts, progress reporting, or job state.
---

# Clip Pipeline

Stages run in a fixed order: `ingest → transcribe → analyze → select → render → package → thumbnail`.

## Contract

Each stage lives in `backend/app/pipeline/stages/<name>.py` and exports:

```python
async def run(ctx: JobContext, progress: ProgressFn) -> JobContext: ...
```

- Read inputs from `ctx.artifacts`; write outputs to `ctx.artifacts`.
- Emit `progress(stage_name, 0..100, message)` at start, milestones, and end.
- Raise typed errors from `core/errors.py` on failure — never swallow.
- Be idempotent: re-running overwrites only that stage's artifacts.
- Never call Groq twice for the same source: cache transcripts/scores in `ctx.artifacts` and DB.

## Registering a stage

Add it to `STAGES` in `backend/app/pipeline/pipeline.py`. Do not change order without updating `ARCHITECTURE.md`.

## Job state

`jobs.status`: `queued | running | succeeded | failed | cancelled`.
`jobs.stage`, `jobs.progress` are updated on every progress event via `controllers/job_controller.py`.
`core/events.py` broadcasts to SSE subscribers on `/api/jobs/{id}/events`.

## Tests

One test per stage in `backend/tests/test_pipeline_<stage>.py`, mocking external services. Assert artifacts and progress sequence.
