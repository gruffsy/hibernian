param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("start", "finish", "run")]
  [string]$Mode,

  [string]$Owner = "tmux",
  [string]$Objective = "",
  [string]$Scope = "",
  [string]$NextStep = "",
  [string]$Verification = "",
  [string]$Blockers = "ingen",
  [string]$Summary = "",
  [string]$Command = "",
  [string]$AgentsPath = (Join-Path $PSScriptRoot "..\AGENTS.md")
)

$ErrorActionPreference = "Stop"

function Get-IsoStamp {
  Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
}

function Normalize-Text {
  param([string]$Value)
  if ([string]::IsNullOrWhiteSpace($Value)) {
    return "<ikke spesifisert>"
  }
  return $Value.Trim()
}

function Read-AgentLines {
  param([string]$Path)
  if (-not (Test-Path $Path)) {
    throw "Fant ikke AGENTS-fil: $Path"
  }
  return Get-Content -Path $Path
}

function Write-AgentLines {
  param(
    [string]$Path,
    [string[]]$Lines
  )
  Set-Content -Path $Path -Value $Lines -Encoding UTF8
}

function Get-CurrentBounds {
  param([string[]]$Lines)

  $current = [Array]::IndexOf($Lines, "## Current")
  if ($current -lt 0) {
    throw "Fant ikke Current-blokken i AGENTS.md"
  }

  $open = -1
  $close = -1
  for ($i = $current + 1; $i -lt $Lines.Length; $i++) {
    if ($open -lt 0 -and $Lines[$i].Trim() -eq '```text') {
      $open = $i
      continue
    }
    if ($open -ge 0 -and $Lines[$i].Trim() -eq '```') {
      $close = $i
      break
    }
  }

  if ($open -lt 0 -or $close -lt 0) {
    throw "Current-blokken har ugyldig format i AGENTS.md"
  }

  return @{
    current = $current
    open = $open
    close = $close
  }
}

function Get-CurrentFieldValue {
  param(
    [string[]]$Lines,
    [string]$Field
  )

  $bounds = Get-CurrentBounds -Lines $Lines
  for ($i = $bounds.open + 1; $i -lt $bounds.close; $i++) {
    $line = $Lines[$i]
    $prefix = $Field + ": "
    if ($line.StartsWith($prefix)) {
      return $line.Substring($prefix.Length).Trim()
    }
  }

  return ""
}

function Set-CurrentBlock {
  param(
    [string[]]$Lines,
    [hashtable]$Values
  )

  $bounds = Get-CurrentBounds -Lines $Lines
  $replacement = @(
    "status: $($Values.status)",
    "owner: $($Values.owner)",
    "started_at: $($Values.started_at)",
    "updated_at: $($Values.updated_at)",
    "objective: $($Values.objective)",
    "scope: $($Values.scope)",
    "next_step: $($Values.next_step)",
    "verification: $($Values.verification)",
    "blockers: $($Values.blockers)"
  )

  $output = New-Object System.Collections.Generic.List[string]
  for ($i = 0; $i -le $bounds.open; $i++) {
    $output.Add($Lines[$i])
  }
  foreach ($line in $replacement) {
    $output.Add($line)
  }
  for ($i = $bounds.close; $i -lt $Lines.Length; $i++) {
    $output.Add($Lines[$i])
  }

  return $output.ToArray()
}

function Append-HistoryEntry {
  param(
    [string[]]$Lines,
    [hashtable]$Values
  )

  $entryText = @'

### __STAMP__

```text
timestamp: __TIMESTAMP__
owner: __OWNER__
status: __STATUS__
summary: __SUMMARY__
files: __FILES__
next: __NEXT__
```
'@
  $entryText = $entryText.Replace("__STAMP__", (Get-IsoStamp))
  $entryText = $entryText.Replace("__TIMESTAMP__", $Values.timestamp)
  $entryText = $entryText.Replace("__OWNER__", $Values.owner)
  $entryText = $entryText.Replace("__STATUS__", $Values.status)
  $entryText = $entryText.Replace("__SUMMARY__", $Values.summary)
  $entryText = $entryText.Replace("__FILES__", $Values.files)
  $entryText = $entryText.Replace("__NEXT__", $Values.next)

  return $Lines + ($entryText -split "`r?`n")
}

function Read-CurrentState {
  param([string[]]$Lines)

  return @{
    started_at = Get-CurrentFieldValue -Lines $Lines -Field "started_at"
    owner = Get-CurrentFieldValue -Lines $Lines -Field "owner"
  }
}

$AgentsPath = (Resolve-Path $AgentsPath).Path
$now = Get-IsoStamp
$lines = Read-AgentLines -Path $AgentsPath

switch ($Mode) {
  "start" {
    $updated = Set-CurrentBlock -Lines $lines -Values @{
      status = "in_progress"
      owner = Normalize-Text $Owner
      started_at = $now
      updated_at = $now
      objective = Normalize-Text $Objective
      scope = Normalize-Text $Scope
      next_step = Normalize-Text $NextStep
      verification = Normalize-Text $Verification
      blockers = Normalize-Text $Blockers
    }
    Write-AgentLines -Path $AgentsPath -Lines $updated
    Write-Host "AGENTS.md oppdatert for start."
  }

  "finish" {
    $status = if ($Blockers -and $Blockers -ne "ingen") { "blocked" } else { "complete" }
    $currentState = Read-CurrentState -Lines $lines
    $updated = Set-CurrentBlock -Lines $lines -Values @{
      status = $status
      owner = Normalize-Text $Owner
      started_at = if ($currentState.started_at) { $currentState.started_at } else { $now }
      updated_at = $now
      objective = Normalize-Text $Objective
      scope = Normalize-Text $Scope
      next_step = Normalize-Text $NextStep
      verification = Normalize-Text $Verification
      blockers = Normalize-Text $Blockers
    }
    if ($Summary) {
      $updated = Append-HistoryEntry -Lines $updated -Values @{
        timestamp = $now
        owner = Normalize-Text $Owner
        status = $status
        summary = Normalize-Text $Summary
        files = Normalize-Text $Scope
        next = Normalize-Text $NextStep
      }
    }
    Write-AgentLines -Path $AgentsPath -Lines $updated
    Write-Host "AGENTS.md oppdatert for finish."
  }

  "run" {
    if ([string]::IsNullOrWhiteSpace($Command)) {
      throw "Mode=run krever -Command"
    }

    $started = Set-CurrentBlock -Lines $lines -Values @{
      status = "in_progress"
      owner = Normalize-Text $Owner
      started_at = $now
      updated_at = $now
      objective = Normalize-Text $Objective
      scope = Normalize-Text $Scope
      next_step = Normalize-Text $NextStep
      verification = Normalize-Text $Verification
      blockers = Normalize-Text $Blockers
    }
    Write-AgentLines -Path $AgentsPath -Lines $started

    $exitCode = 0
    try {
      Invoke-Expression $Command
      $exitCode = $LASTEXITCODE
    }
    catch {
      $exitCode = 1
      $Blockers = $_.Exception.Message
    }

    $finishStatus = if ($exitCode -eq 0 -and ($Blockers -eq "ingen" -or [string]::IsNullOrWhiteSpace($Blockers))) { "complete" } else { "blocked" }
    $freshLines = Read-AgentLines -Path $AgentsPath
    $currentState = Read-CurrentState -Lines $freshLines
    $finished = Set-CurrentBlock -Lines $freshLines -Values @{
      status = $finishStatus
      owner = Normalize-Text $Owner
      started_at = if ($currentState.started_at) { $currentState.started_at } else { $now }
      updated_at = Get-IsoStamp
      objective = Normalize-Text $Objective
      scope = Normalize-Text $Scope
      next_step = Normalize-Text $NextStep
      verification = Normalize-Text $Verification
      blockers = Normalize-Text $Blockers
    }
    if ($Summary) {
      $finished = Append-HistoryEntry -Lines $finished -Values @{
        timestamp = Get-IsoStamp
        owner = Normalize-Text $Owner
        status = $finishStatus
        summary = Normalize-Text $Summary
        files = Normalize-Text $Scope
        next = Normalize-Text $NextStep
      }
    }
    Write-AgentLines -Path $AgentsPath -Lines $finished
    if ($exitCode -ne 0) {
      throw "Kommando feilet med exit code $exitCode"
    }
    Write-Host "AGENTS.md oppdatert etter kjøring."
  }
}
