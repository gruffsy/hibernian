param(
  [Parameter(Mandatory = $true)]
  [string]$Message,

  [string]$Objective = "",
  [switch]$AllowPipelineData,
  [switch]$SkipPrimaryBeta
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
  param(
    [Parameter(Mandatory = $true)]
    [string[]]$Arguments
  )

  & git @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
  }
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$objectiveText = if ([string]::IsNullOrWhiteSpace($Objective)) { $Message.Trim() } else { $Objective.Trim() }
$scopeGuardPath = Join-Path $PSScriptRoot "git-scope-guard.ps1"
$syncScriptPath = Join-Path $PSScriptRoot "sync-beta-remotes.ps1"

Set-Location $repoRoot

$statusBefore = (& git status --short)
if ($LASTEXITCODE -ne 0) {
  throw "Could not read git status."
}

if (-not $statusBefore) {
  throw "Working tree is clean. Nothing to publish."
}

Write-Host "Staging local changes..."
Invoke-Git -Arguments @("add", "-A")

$stagedFiles = (& git diff --cached --name-only)
if ($LASTEXITCODE -ne 0) {
  throw "Could not inspect staged files."
}

if (-not $stagedFiles) {
  throw "No staged changes were found after git add -A."
}

$guardArgs = @(
  "-ExecutionPolicy", "Bypass",
  "-File", $scopeGuardPath,
  "-Objective", $objectiveText
)
if ($AllowPipelineData) {
  $guardArgs += "-AllowPipelineData"
}

Write-Host "Running scope guard..."
& powershell @guardArgs
if ($LASTEXITCODE -ne 0) {
  throw "Scope guard blocked the publish."
}

Write-Host "Creating commit..."
Invoke-Git -Arguments @("commit", "-m", $Message)

$syncArgs = @(
  "-ExecutionPolicy", "Bypass",
  "-File", $syncScriptPath
)
if ($SkipPrimaryBeta) {
  $syncArgs += "-SkipPrimaryBeta"
}

Write-Host "Syncing to beta remotes..."
& powershell @syncArgs
if ($LASTEXITCODE -ne 0) {
  throw "Remote sync failed."
}

Write-Host ""
Write-Host "Publish complete."
Write-Host "Primary objective: $objectiveText"
