# SpeedReader Build Script
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== SpeedReader Build Script ===" -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv .venv
}

# Set execution policy for this process and activate venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
. .\.venv\Scripts\Activate.ps1

Write-Host "Installing/updating dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

Write-Host "Running tests..." -ForegroundColor Yellow
python -m pytest tests/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting build." -ForegroundColor Red
    exit 1
}

Write-Host "Building executable..." -ForegroundColor Yellow
# HIGH-RISK/REPEAT: run Nuitka from the venv (python -m), never the global `nuitka`,
# so the EXE bundles the venv's pinned packages (mcp<2), not global ones.
python -m nuitka --standalone --assume-yes-for-downloads --enable-plugin=tk-inter --include-module=pyttsx3.drivers.sapi5 --include-module=win32com.server --include-module=win32com.server.util SpeedReader.py

if ($LASTEXITCODE -eq 0) {
    # load_mcp_config falls back to config.json next to the EXE.
    if (Test-Path config.json) { Copy-Item config.json SpeedReader.dist\ -Force }
    Write-Host ""
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Executable: $scriptDir\SpeedReader.dist\SpeedReader.exe" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
