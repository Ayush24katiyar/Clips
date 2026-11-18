# Install FFmpeg locally with winget (Windows 10/11).
# Docker users can skip this — the API/worker image already includes FFmpeg.
$ErrorActionPreference = "Stop"

winget install --id Gyan.FFmpeg --source winget --accept-package-agreements --accept-source-agreements

$bin = (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue).Source
if (-not $bin) {
    $bin = Join-Path $env:LOCALAPPDATA "Microsoft\WinGet\Links\ffmpeg.exe"
}
$root = Split-Path $bin -Parent
$probe = Join-Path $root "ffprobe.exe"

if (Test-Path $bin) {
    $envPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($envPath -notlike "*$root*") {
        [Environment]::SetEnvironmentVariable("Path", "$envPath;$root", "User")
    }
    Write-Host "FFmpeg installed at $root. Restart your terminal, or set FFMPEG_BIN/FFPROBE_BIN in .env."
    Write-Host "FFPROBE: $probe"
} else {
    Write-Warning "winget finished but ffmpeg.exe was not found. Set FFMPEG_BIN and FFPROBE_BIN in .env manually."
}
