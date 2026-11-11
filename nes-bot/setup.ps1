# Create an isolated Python 3.13 environment for the bot and run its emulator-free checks.
#   .\nes-bot\setup.ps1                 # .venv-original at the repository root
#   .\nes-bot\setup.ps1 -Train          # also PyTorch, for value-net training
param(
    [string]$EnvironmentPath = (Join-Path (Split-Path -Parent $PSScriptRoot) '.venv-original'),
    [switch]$Train,
    [switch]$SkipTests
)
$ErrorActionPreference = 'Stop'
$EnvironmentPath = [System.IO.Path]::GetFullPath($EnvironmentPath)
$python = Join-Path $EnvironmentPath 'Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) {
    & py -3.13 -m venv $EnvironmentPath
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the Python 3.13 environment' }
}
$requirements = Join-Path $PSScriptRoot $(if ($Train) { 'requirements-train.txt' } else { 'requirements.txt' })
& $python -m pip install -r $requirements
if ($LASTEXITCODE -ne 0) { throw 'Dependencies failed to install' }
if (-not $SkipTests) {
    Push-Location (Split-Path -Parent $PSScriptRoot)
    try {
        & $python -m pytest -q
        if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
    } finally { Pop-Location }
}
Write-Host "Bot Python: $python"
