param(
  [int]$Port = 4173
)

$ErrorActionPreference = "Stop"

Write-Host "Starter lokal preview pa http://127.0.0.1:$Port"
Write-Host "Trykk Ctrl+C for a stoppe serveren."
Write-Host "Hvis brannmuren tillater det, kan siden ogsa naes pa lokal IP."

python -m http.server $Port --bind 0.0.0.0
