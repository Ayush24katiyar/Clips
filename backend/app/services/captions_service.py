from __future__ import annotations

from pathlib import Path

from ..schemas.analysis import ClipCandidate, Transcript


def _ts(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class CaptionsService:
    def write_all(self, transcript: Transcript, clip: ClipCandidate, directory: Path) -> dict[str, Path]:
        words = transcript.words_between(clip.start, clip.end)
        if not words:
            return {}
        directory.mkdir(parents=True, exist_ok=True)
        base = directory / f"clip_{int(clip.start)}"
        return {
            "srt": self._write_srt(words, clip.start, base.with_suffix(".srt")),
            "vtt": self._write_vtt(words, clip.start, base.with_suffix(".vtt")),
            "ass": self._write_ass(words, clip.start, base.with_suffix(".ass")),
        }

    def _write_srt(self, words: list, offset: float, path: Path) -> Path:
        lines: list[str] = []
        for index, word in enumerate(words, 1):
            lines += [
                str(index),
                f"{_ts(word.start - offset)} --> {_ts(word.end - offset)}",
                word.word.strip(),
                "",
            ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _write_vtt(self, words: list, offset: float, path: Path) -> Path:
        lines = ["WEBVTT", ""]
        for word in words:
            lines += [
                f"{_ts(word.start - offset).replace(',', '.')} --> {_ts(word.end - offset).replace(',', '.')}",
                word.word.strip(),
                "",
            ]
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    def _write_ass(self, words: list, offset: float, path: Path) -> Path:
        header = (
            "[Script Info]\n"
            "ScriptType: v4.00+\n"
            "PlayResX: 1080\n"
            "PlayResY: 1920\n"
            "WrapStyle: 2\n"
            "\n"
            "[V4+ Styles]\n"
            "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, "
            "Bold, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: Default,Arial,72,&H00FFFFFF,&H00000000,&H80000000,-1,2,60,60,240,1\n"
            "\n"
            "[Events]\n"
            "Format: Layer, Start, End, Style, Text\n"
        )
        lines = [header]
        for word in words:
            start = self._ass_ts(word.start - offset)
            end = self._ass_ts(word.end - offset)
            lines.append(
                f"Dialogue: 0,{start},{end},Default,"
                f"{{\\k{int(max((word.end - word.start) * 100, 1))}}}{word.word.strip()}"
            )
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def _ass_ts(seconds: float) -> str:
        centis = int(seconds * 100)
        hours, centis = divmod(centis, 360000)
        minutes, centis = divmod(centis, 6000)
        secs, centis = divmod(centis, 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"
