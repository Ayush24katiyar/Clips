---
name: FFmpeg Recipes
description: Correct FFmpeg commands for ClipForge media tasks — probing, lossless/visually-lossless cutting, face-tracked 9:16 reframing, caption burn-in, loudness, thumbnails, WebM. Use when touching render code or debugging video output.
---

# FFmpeg Recipes

All commands must be issued through `backend/app/services/ffmpeg_service.py`; probe through `backend/app/utils/ffprobe.py`. Never call subprocess directly elsewhere.

## Probe

```bash
ffprobe -v error -show_entries format=duration:stream=index,codec_name,codec_type,width,height,r_frame_rate -of json INPUT
```

## Visually lossless delivery (default, `visually_lossless`)

```bash
ffmpeg -ss START -i SOURCE -t DURATION \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles=ass.ass" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p \
  -c:a aac -b:a 320k -ar 48000 \
  -af loudnorm=I=-14:TP=-1:LRA=11 \
  -movflags +faststart OUTPUT.mp4
```

## Bit-exact archive (`bit_exact`) — no filters allowed

```bash
ffmpeg -ss START -i SOURCE -t DURATION -map 0 -c copy OUTPUT.mp4
```
Cuts snap to keyframes. Do not add `-vf` or `-af`.

## True lossless master (`true_lossless`)

```bash
ffmpeg -ss START -i SOURCE -t DURATION -c:v ffv1 -level 3 -c:a flac OUTPUT.mkv
```
Archive only; never delivered to the UI.

## Draft NVENC (preview only)

```bash
ffmpeg -ss START -i SOURCE -t DURATION -c:v h264_nvenc -cq 20 -preset p4 -pix_fmt yuv420p -c:a aac -b:a 192k OUTPUT.mp4
```

## WebM / VP9

```bash
ffmpeg -i INPUT.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus -b:a 128k OUTPUT.webm
```

## Caption styles

- `captions_service.py` writes `.srt`, `.vtt`, and karaoke `.ass` from Groq word timestamps.
- ASS karaoke uses `{\k<centiseconds>}` inline tags; one style per speaker colour.
- Burn with `subtitles=ass.ass:fontsdir=/app/storage/fonts`.

## Thumbnail

```bash
ffmpeg -ss FRAME_TIME -i INPUT -frames:v 1 -q:v 2 THUMB.jpg
```
Add title overlay with Pillow in `thumbnail_service.py`, never with `drawtext` font hacks.

## Verification after every render

Run `ffprobe` on the output and assert: codec=h264, pix_fmt=yuv420p, has video+audio streams, duration within 0.2 s of requested.
