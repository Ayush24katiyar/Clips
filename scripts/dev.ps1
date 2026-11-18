# Start API + worker + frontend without Docker (requires local Redis and Postgres)
$ErrorActionPreference = "Stop"

$env:PYTHONPATH = "backend"
Start-Process -FilePath ".venv\Scripts\uvicorn.exe" -ArgumentList "app.main:app --reload --port 8000" -NoNewWindow
Start-Process -FilePath ".venv\Scripts\celery.exe" -ArgumentList "-A app.workers.celery_app.celery_app worker --loglevel=info" -NoNewWindow
Set-Location frontend
npm run dev
