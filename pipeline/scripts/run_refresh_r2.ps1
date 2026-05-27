param(
    [string]$NavSqlUsername = $env:HIBERNIAN_NAV_SQL_USERNAME,
    [string]$NavSqlPassword = $env:HIBERNIAN_NAV_SQL_PASSWORD,
    [string]$R2AccessKeyId = $env:HIBERNIAN_R2_ACCESS_KEY_ID,
    [string]$R2SecretAccessKey = $env:HIBERNIAN_R2_SECRET_ACCESS_KEY,
    [string]$PipelineRoot = ".",
    [string]$SecretsFile = ".\config\secrets.local.ps1"
)

$ErrorActionPreference = "Stop"

if (Test-Path -LiteralPath $SecretsFile) {
    . $SecretsFile
    if (-not $PSBoundParameters.ContainsKey("NavSqlUsername")) { $NavSqlUsername = $env:HIBERNIAN_NAV_SQL_USERNAME }
    if (-not $PSBoundParameters.ContainsKey("NavSqlPassword")) { $NavSqlPassword = $env:HIBERNIAN_NAV_SQL_PASSWORD }
    if (-not $PSBoundParameters.ContainsKey("R2AccessKeyId")) { $R2AccessKeyId = $env:HIBERNIAN_R2_ACCESS_KEY_ID }
    if (-not $PSBoundParameters.ContainsKey("R2SecretAccessKey")) { $R2SecretAccessKey = $env:HIBERNIAN_R2_SECRET_ACCESS_KEY }
}

function Assert-Value {
    param(
        [string]$Name,
        [string]$Value
    )

    if ([string]::IsNullOrWhiteSpace($Value)) {
        throw "Missing required value: $Name"
    }
}

Assert-Value -Name "HIBERNIAN_NAV_SQL_USERNAME" -Value $NavSqlUsername
Assert-Value -Name "HIBERNIAN_NAV_SQL_PASSWORD" -Value $NavSqlPassword
Assert-Value -Name "HIBERNIAN_R2_ACCESS_KEY_ID" -Value $R2AccessKeyId
Assert-Value -Name "HIBERNIAN_R2_SECRET_ACCESS_KEY" -Value $R2SecretAccessKey

$env:PYTHONPATH = "src"
$env:HIBERNIAN_NAV_SQL_USERNAME = $NavSqlUsername
$env:HIBERNIAN_NAV_SQL_PASSWORD = $NavSqlPassword
$env:HIBERNIAN_R2_ACCESS_KEY_ID = $R2AccessKeyId
$env:HIBERNIAN_R2_SECRET_ACCESS_KEY = $R2SecretAccessKey

python -m hibernian_pipeline.cli --pipeline-root $PipelineRoot refresh-r2
