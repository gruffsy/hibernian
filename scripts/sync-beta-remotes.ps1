param(
  [string]$PrimaryRemote = "origin",
  [string]$PrimaryBranch = "main",
  [string]$SecondaryRemote = "hibernian",
  [string]$SecondaryBranch = "beta",
  [switch]$SkipPrimaryBeta,
  [switch]$IncludeSecondaryRemote
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
Set-Location $repoRoot

$statusOutput = (& git status --short)
if ($LASTEXITCODE -ne 0) {
  throw "Could not read git status."
}

if ($statusOutput) {
  throw "Working tree is not clean. Commit or stash changes before syncing branches."
}

$currentBranch = (& git branch --show-current).Trim()
if ($LASTEXITCODE -ne 0) {
  throw "Could not determine current branch."
}

if ($currentBranch -ne $PrimaryBranch) {
  throw "Current branch is '$currentBranch'. Switch to '$PrimaryBranch' before syncing."
}

$headSha = (& git rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) {
  throw "Could not determine HEAD commit."
}

Write-Host "Syncing commit $headSha from $PrimaryRemote/$PrimaryBranch ..."

Invoke-Git -Arguments @("push", $PrimaryRemote, $PrimaryBranch)

if (-not $SkipPrimaryBeta) {
  Invoke-Git -Arguments @("push", $PrimaryRemote, "$PrimaryBranch`:beta")
}

if ($IncludeSecondaryRemote) {
  Invoke-Git -Arguments @("push", $SecondaryRemote, "$PrimaryBranch`:$SecondaryBranch")
}

$primaryMainSha = (& git ls-remote $PrimaryRemote "refs/heads/$PrimaryBranch").Split("`t")[0]
$primaryBetaSha = (& git ls-remote $PrimaryRemote "refs/heads/beta").Split("`t")[0]
Write-Host ""
Write-Host "Done."
Write-Host "$PrimaryRemote/$PrimaryBranch  $primaryMainSha"
if (-not $SkipPrimaryBeta) {
  Write-Host "$PrimaryRemote/beta        $primaryBetaSha"
}
if ($IncludeSecondaryRemote) {
  $secondaryBetaSha = (& git ls-remote $SecondaryRemote "refs/heads/$SecondaryBranch").Split("`t")[0]
  Write-Host "$SecondaryRemote/$SecondaryBranch  $secondaryBetaSha"
}
