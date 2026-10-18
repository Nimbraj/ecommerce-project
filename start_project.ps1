# PowerShell script to start the E-commerce project

# Check if we're in the right directory
$projectRoot = $PSScriptRoot
Set-Location $projectRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting JN ECOMMERCE App" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Function to check if a command exists
function Test-CommandExists {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Check Node.js
if (-not (Test-CommandExists "node")) {
    Write-Host "Error: Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "Node.js found: $(node --version)" -ForegroundColor Green
Write-Host "npm found: $(npm.cmd --version)" -ForegroundColor Green

# --- BACKEND SETUP ---
Write-Host "`n[1/4] Setting up Backend..." -ForegroundColor Yellow
Set-Location "$projectRoot\backend"
$backendPython = Join-Path $projectRoot "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $backendPython)) {
    if (Test-CommandExists "uv") {
        uv venv .venv --python 3.12
    } elseif (Test-CommandExists "py") {
        py -3.12 -m venv .venv
    } else {
        throw "Install Python 3.12 or uv to create the backend virtual environment."
    }
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $backendPython)) {
        throw "Could not create the backend virtual environment."
    }
}

# Check if dependencies are installed
try {
    & $backendPython -c "import fastapi, uvicorn, sqlalchemy, pydantic, passlib, jose, pyotp, qrcode, PIL, dotenv" 2>$null
    if ($LASTEXITCODE -ne 0) { throw "Backend dependencies are missing" }
    Write-Host "Backend dependencies already installed." -ForegroundColor Green
} catch {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    if (Test-CommandExists "uv") {
        uv pip install -r requirements.txt --python $backendPython
    } else {
        & $backendPython -m pip install -r requirements.txt
    }
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed" }
}

# Seed database if shopswift.db doesn't exist
if (-not (Test-Path "./shopswift.db")) {
    Write-Host "Database not found. Seeding database..." -ForegroundColor Yellow
    & $backendPython seed_main.py
    if ($LASTEXITCODE -ne 0) { throw "Database seeding failed" }
} else {
    Write-Host "Database already exists." -ForegroundColor Green
}

# --- FRONTEND SETUP ---
Write-Host "`n[2/4] Setting up Frontend..." -ForegroundColor Yellow
Set-Location "$projectRoot\ecommerc-app"

if (-not (Test-Path "./node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm.cmd install
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed" }
} else {
    Write-Host "Frontend dependencies already installed." -ForegroundColor Green
}

# --- START SERVERS ---
Write-Host "`n[3/4] Starting Backend Server..." -ForegroundColor Yellow
$backendPythonPath = $backendPython
$projectRootPath = $projectRoot
$backendJob = Start-Job -ScriptBlock {
    param($pythonPath, $rootPath)
    Set-Location (Join-Path $rootPath "backend")
    & $pythonPath -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
} -ArgumentList $backendPythonPath, $projectRootPath

# Wait a moment for backend to start
Start-Sleep -Seconds 3

Write-Host "[4/4] Starting Frontend Server..." -ForegroundColor Yellow
$frontendJob = Start-Job -ScriptBlock {
    param($rootPath)
    Set-Location (Join-Path $rootPath "ecommerc-app")
    npm.cmd run dev
} -ArgumentList $projectRootPath

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Both servers are starting..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Green
Write-Host "API Docs:    http://localhost:8000/docs" -ForegroundColor Green
Write-Host "Frontend:    http://localhost:5173" -ForegroundColor Green
Write-Host "`nPress Ctrl+C to stop both servers." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Display logs in real-time
try {
    while ($true) {
        $backendOutput = Receive-Job -Job $backendJob
        $frontendOutput = Receive-Job -Job $frontendJob

        if ($backendOutput) {
            Write-Host "[BACKEND] $backendOutput" -ForegroundColor Blue
        }
        if ($frontendOutput) {
            Write-Host "[FRONTEND] $frontendOutput" -ForegroundColor Magenta
        }

        # Check if jobs are still running
        if ($backendJob.State -eq "Failed") {
            Write-Host "Backend server failed!" -ForegroundColor Red
            break
        }
        if ($frontendJob.State -eq "Failed") {
            Write-Host "Frontend server failed!" -ForegroundColor Red
            break
        }

        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`nStopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job -Job $frontendJob -ErrorAction SilentlyContinue
    Write-Host "Servers stopped." -ForegroundColor Green
}

