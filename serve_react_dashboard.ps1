Set-Location -Path "$PSScriptRoot"

Write-Host "Starting local server on http://localhost:8000 ..." -ForegroundColor Cyan
Write-Host "Open: http://localhost:8000/react_dashboard.html" -ForegroundColor Cyan
Write-Host ""

python -m http.server 8000

