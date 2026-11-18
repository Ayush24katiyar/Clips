from __future__ import annotations

from app.utils.ffprobe import MediaInfo


def test_media_info_parsing() -> None:
    info = MediaInfo.from_dict(
        {
            "format": {"duration": "12.5"},
            "streams": [
                {
                    "codec_type": "video",
                    "codec_name": "h264",
                    "pix_fmt": "yuv420p",
                    "width": 1080,
                    "height": 1920,
                    "r_frame_rate": "30000/1001",
                },
                {"codec_type": "audio", "codec_name": "aac"},
            ],
        }
    )
    assert info.duration == 12.5
    assert info.codec == "h264"
    assert info.has_audio is True
    assert 29.9 < info.fps < 30.1
