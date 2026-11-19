# Quality & Media Policy

## The reality

A 4K YouTube source is already lossy. "Lossless clip" means **no additional generation loss**. Compression and losslessness are mutually exclusive, so three explicit modes exist.

| Mode | Command shape | Use |
|---|---|---|
| `visually_lossless` (default) | `libx264 -crf 17 -preset slow`, `yuv420p`, AAC 320k | Delivery. Visually indistinguishable (FFmpeg wiki: 17–18 is visually lossless). |
| `bit_exact` | `-ss … -to … -c copy` | Archive/faithful clips. No reframe/captions; keyframe-snapped cuts. |
| `true_lossless` | `-qp 0` H.264 or FFV1 in MKV/MOV | Master archive only. GBs/min, not browser playable. |
| `balanced` | `libx264 -crf 21` | Explicit user choice for small files. |

## Encoder choice on RTX 3050 4GB

- Final: **CPU libx264** (`-preset slow`) — best quality at a given bitrate. Short clips make this affordable.
- Draft/preview: **h264_nvenc -cq 20** — fast, GPU offload.
- **No AV1 encode** (GA106 7th-gen NVENC supports H.264/H.265 only; AV1 decode only).
- WebM: CPU VP9 (`libvpx-vp9 -crf 30 -b:v 0`) + Opus.

## Resolution honesty

A 16:9 4K source (3840×2160) contains only ~1215×2160 pixels of vertical frame.

| Output | From 4K source |
|---|---|
| `1080x1920` vertical (default) | slight downscale → very sharp, native-quality |
| `1440x2560` vertical | upscaled; only if user explicitly accepts |
| `2560x1440` / `3840x2160` widescreen | native, no upscale |

Never stretch. Two `reframe` modes are available:
- `crop` (default) — face/center crop to fill the vertical frame.
- `letterbox` — full 16:9 frame over a blurred fill, preserving gameplay UI and facecam;
  recommended for gaming streams where cropping would cut off important screen content.

Every clip also carries a 1.5 s hook text overlay burned into the ASS captions, written from
the clip title so it stays traceable to the transcript.

## Mandatory output properties

- Container MP4, video H.264 High, pixel format `yuv420p`, `-movflags +faststart`.
- Audio AAC 320k (or Opus for WebM), 48 kHz stereo.
- Loudness `loudnorm` target −14 LUFS, true peak ≤ −1 dBTP.
- Captions: SRT/VTT sidecar + karaoke ASS burn-in from Groq word timestamps.
- Every file validated with `ffprobe`: codec, resolution, duration, streams present.

## Thumbnails

Peak frame (highest detected energy / expressive face) + title overlay, exported JPG at 90% quality. Never a black frame.
