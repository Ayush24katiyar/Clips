from __future__ import annotations

from dataclasses import dataclass

from ..schemas.analysis import ClipCandidate, Transcript

HOOK_WORDS = ("but", "because", "actually", "never", "every", "nobody", "really", "wait")
NUMBER_WORDS = ("first", "second", "three", "million", "percent", "%")


@dataclass
class SignalResult:
    start: float
    end: float
    bonus: float
    label: str


def hook_density(transcript: Transcript) -> float:
    words = transcript.words
    if not words:
        return 0.0
    hits = sum(1 for w in words if w.word.lower().strip(".,!? ") in HOOK_WORDS + NUMBER_WORDS)
    return min(hits / max(len(words) / 1000, 1.0), 100.0)


def local_signal_candidates(
    transcript: Transcript,
    min_seconds: float,
    max_seconds: float,
    limit: int,
) -> list[SignalResult]:
    """Fallback when LLM analysis is unavailable: score transcript windows.

    Real implementation will add silence/loudness/face peaks (see ARCHITECTURE.md).
    """
    words = transcript.words
    if not words:
        return []
    results: list[SignalResult] = []
    step = max(int(len(words) / (limit * 2)), 1)
    for i in range(0, len(words), step):
        start = words[i].start
        window = [w for w in words[i:] if w.start <= start + max_seconds]
        if not window:
            continue
        end = window[-1].end
        duration = end - start
        if not (min_seconds <= duration <= max_seconds):
            continue
        text = " ".join(w.word for w in window).lower()
        density = sum(1 for w in window if w.word.lower() in HOOK_WORDS + NUMBER_WORDS)
        bonus = min(density * 4 + (8 if any(k in text for k in NUMBER_WORDS) else 0), 35)
        results.append(SignalResult(start=max(start, 0), end=end, bonus=bonus, label="transcript"))
    return sorted(results, key=lambda r: r.bonus, reverse=True)[:limit]


def combine(candidates: list[ClipCandidate], signals: list[SignalResult]) -> list[ClipCandidate]:
    signal_by_start = {round(s.start): s for s in signals}
    merged: list[ClipCandidate] = []
    for clip in candidates:
        signal = signal_by_start.get(round(clip.start))
        if signal:
            clip = clip.model_copy(update={"score": min(clip.score + signal.bonus, 100)})
        merged.append(clip)
    return sorted(merged, key=lambda c: c.score, reverse=True)
