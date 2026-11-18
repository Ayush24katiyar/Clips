#!/bin/bash
echo "yt-dlp: $(yt-dlp --version 2>&1)"
echo "ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
echo "--- metadata only ---"
timeout 90 yt-dlp --no-playlist --skip-download --print '%(title)s | %(duration)s | %(height)s' 'https://www.youtube.com/watch?v=aqz-KE-bpKQ' 2>&1 | tail -25
echo "exit=$?"
