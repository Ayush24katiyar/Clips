from __future__ import annotations


class ClipForgeError(Exception):
    """Base typed error."""


class DownloadError(ClipForgeError):
    """Source download failed."""


class TranscriptionError(ClipForgeError):
    """ASR failed."""


class AnalysisError(ClipForgeError):
    """LLM analysis failed."""


class RenderError(ClipForgeError):
    """FFmpeg render failed."""


class ValidationError(ClipForgeError):
    """Output validation failed."""


class ProviderError(ClipForgeError):
    """AI provider call failed."""
