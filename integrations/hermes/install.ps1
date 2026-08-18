param(
    [string]$HermesHome = $(if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $HOME ".hermes" })
)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$Target = Join-Path $HermesHome "plugins\sage"
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Existing = Join-Path $Target "__init__.py"
if (Test-Path $Existing) {
    Copy-Item $Existing "$Existing.bak" -Force
}
Copy-Item (Join-Path $Root "sage\__init__.py") $Existing -Force
Copy-Item (Join-Path $Root "sage\plugin.yaml") (Join-Path $Target "plugin.yaml") -Force
Write-Host "Installed SAGE Hermes plugin to $Target"

if (Get-Command hermes -ErrorAction SilentlyContinue) {
    & hermes plugins enable sage
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Enabled Hermes plugin: sage"
    } else {
        Write-Host "Plugin copied. Enable it with: hermes plugins enable sage"
    }
} else {
    Write-Host "Hermes CLI was not found on this machine."
    Write-Host "Enable inside Hermes with: hermes plugins enable sage"
}

Write-Host ""
Write-Host "Configure Hermes with:"
Write-Host "  SAGE_URL=http://127.0.0.1:8080"
Write-Host "  SAGE_AGENT_ID=hermes-a"
Write-Host "  SAGE_WORKSPACE=default"
Write-Host "  SAGE_API_KEY=                 # only when auth is enabled"
