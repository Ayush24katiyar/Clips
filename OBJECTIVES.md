# Objectives — ClipForge

## Product goal

A local web app that turns a long YouTube/Twitch video into several short, vertical, shareable clips with high quality preserved — plus captions, thumbnails, and a creator-discovery feed.

## Acceptance criteria (from the original brief)

1. **Competitive research documented** — incumbent workflow and moats recorded in `RESEARCH.md`.
2. **Open-source inspiration vetted** — MIT-based projects credited; AGPL code excluded. See `RESEARCH.md`.
3. **Quality preserved** — source downloaded up to 4K; default delivery CRF 17 x264; 1080p vertical (native from 4K) or 1440p/2160p widescreen. No visible generation loss.
4. **Lossless option** — bit-exact stream-copy mode and true-lossless MKV master available; documented tradeoffs in `QUALITY.md`.
5. **Valid output** — MP4 (H.264 + AAC, `yuv420p`, `+faststart`) primary, WebM/VP9 optional; every output validated with `ffprobe`.
6. **Thumbnails** — generated per clip from the peak frame with title overlay.
7. **Discovery section** — regional popular YouTube creators and top Twitch gamers/streamers, with country/category filters and a "Clip this" handoff.
8. **Captions** — Groq Whisper word-level timestamps → SRT/VTT + karaoke ASS burn-in; editable in UI.
9. **No greenfield rendering** — reuse proven MIT implementations (AutoClip, opensource-clipping) for render/caption logic.
10. **Clean architecture** — documented DB / controller / router separation, tech stack, file system, and rules.

## Success metrics

- One 60-minute 4K link → 5–10 ranked clips in under 10 minutes on the target machine.
- Delivery clip visually indistinguishable from source at 100% zoom.
- Caption word timing accurate within ~150 ms.
- Cost under US $0.10 per processed hour with Groq.

## Non-goals (v1)

- No multi-tenant auth, billing, or public hosting.
- No AV1 encoding (RTX 3050 cannot encode AV1).
- No automatic publishing to social platforms (deferred to v2).
