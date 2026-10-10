# SpeedReader Build Script
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== SpeedReader Build Script ===" -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Fail fast: a running EXE locks SpeedReader.dist and building anyway leaves a broken dist.
if (Get-Process SpeedReader -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "$scriptDir\SpeedReader.dist\*" }) {
    Write-Host "SpeedReader.exe is running from SpeedReader.dist - close it and rebuild." -ForegroundColor Red
    exit 1
}

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
# No console window; stdout/stderr go to SpeedReader.out.txt / .err.txt beside the EXE
# (uvicorn logs to stderr, which must not be None).
python -m nuitka --standalone --assume-yes-for-downloads --enable-plugin=tk-inter `
    --include-module=pyttsx3.drivers.sapi5 --include-module=win32com.server --include-module=win32com.server.util `
    --windows-icon-from-ico=assets/speedreader.ico --include-data-files=assets/speedreader.ico=assets/speedreader.ico `
    --windows-console-mode=disable "--force-stdout-spec={PROGRAM_BASE}.out.txt" "--force-stderr-spec={PROGRAM_BASE}.err.txt" `
    SpeedReader.py

if ($LASTEXITCODE -eq 0) {
    # load_mcp_config falls back to config.json next to the EXE.
    if (Test-Path config.json) { Copy-Item config.json SpeedReader.dist\ -Force }

    # HIGH-RISK/REPEAT: Smart App Control only trusts a CA-chained signature (Azure Artifact
    # Signing), never self-signed. Opt in via env vars; sign every unsigned binary, not just the EXE.
    if ($env:ARTIFACT_SIGNING_ACCOUNT) {
        Write-Host "Signing with Azure Artifact Signing..." -ForegroundColor Yellow
        if (-not (Get-Command sign -ErrorAction SilentlyContinue)) { dotnet tool install --global sign --prerelease }
        $unsigned = Get-ChildItem SpeedReader.dist -Recurse -Include *.exe, *.dll, *.pyd |
            Where-Object { (Get-AuthenticodeSignature $_.FullName).Status -ne 'Valid' } | ForEach-Object FullName
        sign code artifact-signing $unsigned -v Warning `
            -ase $env:ARTIFACT_SIGNING_ENDPOINT -asa $env:ARTIFACT_SIGNING_ACCOUNT -ascp $env:ARTIFACT_SIGNING_PROFILE
        if ($LASTEXITCODE -ne 0 -or (Get-AuthenticodeSignature SpeedReader.dist\SpeedReader.exe).Status -ne 'Valid') {
            Write-Host "Signing failed! (az login? Signer role? env vars?)" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Unsigned build (set ARTIFACT_SIGNING_* to sign) - Smart App Control will block it." -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "=== Build Complete ===" -ForegroundColor Green
    Write-Host "Executable: $scriptDir\SpeedReader.dist\SpeedReader.exe" -ForegroundColor Green
} else {
    Write-Host "Build failed!" -ForegroundColor Red
    exit 1
}
