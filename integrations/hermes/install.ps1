param(
    [string]$HermesHome = $(if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME ".hermes" })
)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Target = Join-Path $HermesHome "plugins\aifence"
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Existing = Join-Path $Target "__init__.py"
if (Test-Path $Existing) {
    Copy-Item $Existing "$Existing.bak" -Force
}
Copy-Item (Join-Path $Root "aifence\__init__.py") $Existing -Force
Copy-Item (Join-Path $Root "aifence\plugin.yaml") (Join-Path $Target "plugin.yaml") -Force
Write-Host "Installed AIFENCE Hermes plugin to $Target"

if (Get-Command hermes -ErrorAction SilentlyContinue) {
    & hermes plugins enable aifence
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Enabled Hermes plugin: aifence"
    } else {
        Write-Host "Plugin copied. Enable it with: hermes plugins enable aifence"
    }
} else {
    Write-Host "Hermes CLI was not found on this machine."
    Write-Host "Enable inside Hermes with: hermes plugins enable aifence"
}

Write-Host ""
Write-Host "Configure Hermes with:"
Write-Host "  AIFENCE_BUS_URL=http://127.0.0.1:8080"
Write-Host "  AIFENCE_BUS_AGENT_ID=hermes-a"
Write-Host "  AIFENCE_BUS_WORKSPACE=default"
Write-Host "  AIFENCE_BUS_API_KEY=                 # only when auth is enabled"
