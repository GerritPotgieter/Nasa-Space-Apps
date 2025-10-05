<#!
.SYNOPSIS
    Ensure virtual environment, install minimal dependencies (none required beyond stdlib for this script), and run the Celestrak active satellites update.
.DESCRIPTION
    Creates a .venv if absent, then runs update_active_satellites.py with archive enabled by default.
.PARAMETER Limit
    Optional integer to limit number of records (testing).
.PARAMETER NoArchive
    Switch to skip daily CSV archive.
.EXAMPLE
    ./run_update.ps1
.EXAMPLE
    ./run_update.ps1 -Limit 100
#>
param(
    [int] $Limit,
    [switch] $NoArchive
)

$ErrorActionPreference = 'Stop'

Write-Host "[run_update] Ensuring virtual environment..." -ForegroundColor Cyan
if (-not (Test-Path .venv)) {
    python -m venv .venv
}

# Activate
. .\.venv\Scripts\Activate.ps1

# (Optional) place for dependency installs if you add any future libs
# python -m pip install --upgrade pip

$script = 'update_active_satellites.py'
if (-not (Test-Path $script)) {
    throw "Cannot find $script in current directory: $(Get-Location)"
}

$argsList = @()
if ($Limit) { $argsList += '--limit'; $argsList += $Limit }
if ($NoArchive) { $argsList += '--no-archive' }

Write-Host "[run_update] Running update script..." -ForegroundColor Cyan
python $script @argsList

Write-Host "[run_update] Done." -ForegroundColor Green
