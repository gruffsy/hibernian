$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$secrets = Join-Path $repoRoot 'pipeline\config\secrets.local.ps1'

if (Test-Path $secrets) {
    . $secrets
}

$env:PYTHONPATH = 'src'
Set-Location (Join-Path $repoRoot 'pipeline')
python -m hibernian_pipeline.cli --pipeline-root . publish-r2
