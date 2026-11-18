# Research — Clipping Platforms & Tools

## Incumbents

| Product | Scale | Workflow | Moat |
|---|---|---|---|
| OpusClip 4.0 | 20M+ creators | ClipAnything + ReframeAnything; visual/audio/sentiment analysis; captions, CTA, trend data | Proprietary virality model + data flywheel + distribution (publish, teams, templates, API) |
| Klap | 3.5M users / 8.5M clips | Link → ranked clips by virality score, active-speaker reframe, animated captions, scheduler, $0.19–0.29/clip | Ranking data + agency workflow + API/MCP |
| Vizard | 10M+ users | Transcribe → AI clips → reframe → publish, vitality score, text editing, 100+ language captions | Proprietary scoring + install base |

Conclusion: rendering is commodity (FFmpeg + ASR + LLM). The moat is ranking data and distribution. Our wedge: local/private rendering, zero per-clip cost, uncompromised quality, transparent scoring.

## Evidence on what actually drives views

AutoClip research note *"Pick the moment, not the effect"* (158 clips, 2026-10-09):

- Same template → 8×–450× view differences within the same account. The subject and the **in-point** decide outcomes.
- Face or visible event within the first ~1.5 s predicts higher views; expressive-face openings beat screen/gameplay-first openings for the same streamer (4.7×–11×).
- Cut rate, punch-ins, stylised captions, stickers, grading, templates appear in hits and flops alike — packaging is a quality floor, not a growth lever.
- Default length ≤90 s; longer works only for continuous argument or continuous laughter.
- Technical floor: −14 LUFS ±1, true peak ≤ −1 dBTP, no dead-air endings, no lifted blacks.

Consequence: our scoring and `select` stage optimise in-point and content; packaging is kept competent but not over-invested.

## Open-source references (vetted)

| Repo | Stars | License | Use |
|---|---|---|---|
| `zhouxiaoka/autoclip` | 10.7k | MIT | Primary reference: FastAPI+React+Tauri, ranked clips, local ASR, face tracking, 4K flags, CLI/MCP |
| `NaufalRizqullah/opensource-clipping` | 321 | MIT | Caption/thumbnail/B-roll/BGM/diarization feature reference |
| `tryvinci/vinci-clips` | 163 | AGPL-3.0 | Architecture ideas only — code must NOT be copied |
| `SamurAIGPT/ai-clipping-generator` | 121 | MIT | SaaS/UI patterns only; rendering depends on paid MuAPI |

## AI provider: Groq

- `whisper-large-v3-turbo`: **$0.04/hour**, multilingual, `verbose_json` with `timestamp_granularities=["word","segment"]` → word-level captions. `whisper-large-v3`: $0.111/hour, ~10.3% WER.
- Limits: 25 MB free / 100 MB dev per audio file → chunk long videos (Groq cookbook pattern: overlapping segments, stitch with offset-adjusted timestamps). Free tier ≈ 20 RPM / 2000 RPD for Whisper → backoff + cache.
- Text: `gpt-oss-20b` (~1000 t/s, $0.075 in/$0.30 out per 1M) or `gpt-oss-120b` (~500 t/s, $0.15/$0.60); JSON mode. `qwen/qwen3.8-27b` for vision (3 images/request, 20 MB, JSON mode).
- `llama-3.1-8b-instant` / `llama-3.3-70b-versatile` are Enterprise/ContactSales in the current model list — not assumed available.
- Advantage: ~$0.05 per hour-long video, zero local VRAM for AI; RTX 3050 free for encode/face-tracking.

## Agent skills / tooling found

- `agents.md` open standard for `AGENTS.md` (60k+ repos, AAIF/Linux Foundation); OpenCode, Codex, Cursor, Claude Code all read it.
- OpenCode skills: `.opencode/skills/<id>/SKILL.md` with frontmatter; auto-discovered, loaded on demand.
- `kajisho5/ffmpeg-skill` (7.9k★): 42 FFmpeg tools + MCP server, Python, probe-edit-verify discipline — reference for our `ffmpeg-recipes` skill.
- `znyupup/ai-video-editing-skill`: ffmpeg + Whisper + vision reference.
- `fabriqaai/ffmpeg-analyse-video-skill`: frame extraction + vision summaries.
- MCP candidates: `KyaniteLabs/kinocut`, `video-creator/ffmpeg-mcp`, `guimatheus92/mcp-video-analyzer`.
- Licenses must be checked before copying any of the above code.
