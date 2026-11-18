from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ..core.config import settings
from ..utils.paths import thumbnail_path
from .ffmpeg_service import extract_frame


class ThumbnailService:
    def generate(self, clip_id: str, video: Path, frame_time: float, title: str) -> Path:
        raw = settings.storage_path("thumbs") / f"{clip_id}_raw.jpg"
        extract_frame(video, raw, frame_time)
        image = Image.open(raw).convert("RGB")

        overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        height = image.height
        draw.rectangle([0, int(height * 0.62), image.width, height], fill=(0, 0, 0, 150))

        font_size = max(int(image.width * 0.075), 28)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except OSError:
            font = ImageFont.load_default()

        draw.text(
            (int(image.width * 0.06), int(height * 0.72)),
            title[:48],
            font=font,
            fill=(255, 255, 255, 255),
        )
        final = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
        output = thumbnail_path(clip_id)
        final.save(output, quality=90)
        raw.unlink(missing_ok=True)
        return output
