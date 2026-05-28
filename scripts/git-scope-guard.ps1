param(
  [string]$Objective = "",
  [string[]]$AllowedPaths = @(),
  [switch]$AllowPipelineData
)

$ErrorActionPreference = "Stop"

function Is-PipelineObjective {
  param([string]$Text)
  if ([string]::IsNullOrWhiteSpace($Text)) {
    return $false
  }

  return $Text -match '(?i)pipeline|r2|publish data|data refresh|scheduler|historical'
}

function Get-ChangedFiles {
  $output = git diff --cached --name-only
  if (-not $output) {
    $output = git status --short
  }
  $files = @()
  foreach ($line in $output) {
    $path = $line.Trim()
    if ($line.Length -ge 4 -and $line.Substring(0, 3) -match '^[ MADRCU?!]{2}\s$') {
      $path = $line.Substring(3).Trim()
    }
    if ($path) { $files += $path }
  }
  return $files
}

function Path-Is-Allowed {
  param(
    [string]$Path,
    [string[]]$Patterns
  )

  foreach ($pattern in $Patterns) {
    if ($Path -like $pattern) {
      return $true
    }
  }
  return $false
}

$changedFiles = Get-ChangedFiles
if (-not $changedFiles) {
  Write-Host "Ingen lokale endringer funnet."
  exit 0
}

$pipelineObjective = Is-PipelineObjective -Text $Objective

$blocked = @()
foreach ($file in $changedFiles) {
  if ($file -like 'legacy/frontend-static/data/publish/*' -and -not $AllowPipelineData -and -not $pipelineObjective) {
    $blocked += $file
    continue
  }

  if ($AllowedPaths.Count -gt 0 -and -not (Path-Is-Allowed -Path $file -Patterns $AllowedPaths)) {
    $blocked += $file
  }
}

if ($blocked.Count -gt 0) {
  Write-Host "Scope guard stoppet commit/push."
  Write-Host "Ulovlige eller uventede filer:"
  $blocked | ForEach-Object { Write-Host " - $_" }
  Write-Host ""
  Write-Host "Hvis dette faktisk er en pipeline-jobb, kjør med -AllowPipelineData eller sett Objective til å beskrive pipeline/data refresh."
  exit 1
}

Write-Host "Scope guard godkjent."
