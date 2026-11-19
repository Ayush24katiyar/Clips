from __future__ import annotations

import logging

from ..core.config import settings
from ..core.errors import AnalysisError
from ..pipeline.prompts.analyze import ANALYZE_SYSTEM, ANALYZE_USER
from ..schemas.analysis import ClipCandidate, ClipPlan, Transcript
from .groq_client import AIProvider
from .scorer import combine, hook_density, local_signal_candidates

logger = logging.getLogger(__name__)


class Analyzer:
    def __init__(self, provider: AIProvider) -> None:
        self.provider = provider

    async def analyze(
        self,
        transcript: Transcript,
        clip_count: int,
        min_seconds: float,
        max_seconds: float,
    ) -> ClipPlan:
        if transcript.language and not transcript.language.lower().startswith("en"):
            raise AnalysisError(
                f"Only English videos are supported (detected: {transcript.language}). "
                "Please use an English-language source."
            )

        words = transcript.words
        limit = settings.groq_analysis_max_words
        if len(words) > limit:
            # Sample evenly across the whole video so long streams stay within TPM limits.
            step = len(words) / limit
            words = [words[min(int(i * step), len(words) - 1)] for i in range(limit)]
        lines = [f"[{w.start:.2f}-{w.end:.2f}] {w.word}" for w in words]
        prompt = ANALYZE_USER.format(
            clip_count=clip_count,
            min_seconds=min_seconds,
            max_seconds=max_seconds,
            transcript="\n".join(lines) or transcript.text[:4000],
            hook_density=hook_density(transcript),
        )
        try:
            plan = await self.provider.complete_json(ANALYZE_SYSTEM, prompt, ClipPlan)
        except Exception as exc:
            # Rate limits and transient provider errors must not kill the job:
            # deterministic transcript signals are a perfectly good selection.
            logger.warning("LLM analysis unavailable, using local signals: %s", exc)
            plan = ClipPlan()

        signals = local_signal_candidates(transcript, min_seconds, max_seconds, clip_count)
        plan.clips = combine(plan.clips, signals)[:clip_count]

        if not plan.clips:
            # LLM returned nothing usable — fall back to transcript-signal windows.
            plan.clips = [
                ClipCandidate(
                    start=s.start,
                    end=s.end,
                    score=max(s.bonus, 40.0),
                    reason="Automatic transcript-signal selection",
                    title=f"Clip {index}",
                    description="A self-contained moment selected from the transcript.",
                )
                for index, s in enumerate(signals, 1)
            ][:clip_count]
        return plan
