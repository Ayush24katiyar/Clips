# One-time local setup (Windows / PowerShell)
$ErrorActionPreference = "Stop"

uv sync
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env — add your GROQ_API_KEY before running."
}

foreach ($d in @("storage/sources", "storage/clips", "storage/thumbs", "storage/captions", "storage/exports")) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

Write-Host "Bootstrap complete. Run: docker compose up --build"
