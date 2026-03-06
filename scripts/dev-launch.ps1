$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $repoRoot "backend"
$frontendFile = Join-Path $repoRoot "frontend\index_simple.html"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python executable not found at $pythonExe. Create the .venv first."
}

# Free port 8000 if another process is already bound.
$existingListeners = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($existingListeners) {
    $listenerPids = $existingListeners | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($listenerPid in $listenerPids) {
        try {
            Stop-Process -Id $listenerPid -Force -ErrorAction Stop
            Write-Host "Stopped process on port 8000 (PID: $listenerPid)"
        } catch {
            Write-Warning "Could not stop PID $listenerPid on port 8000: $($_.Exception.Message)"
        }
    }
}

# Start backend in detached mode from project virtual environment.
$backendProcess = Start-Process -FilePath $pythonExe `
    -ArgumentList "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" `
    -WorkingDirectory $backendDir `
    -PassThru

Write-Host "Started backend (PID: $($backendProcess.Id))"

# Probe health for up to 20 seconds.
$healthUrl = "http://127.0.0.1:8000/api/health"
$healthy = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $response = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 2
        if ($response.status -eq "healthy") {
            $healthy = $true
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($healthy) {
    Write-Host "Backend health check passed: $healthUrl"
} else {
    Write-Warning "Backend did not become healthy within timeout."
}

if (Test-Path $frontendFile) {
    Start-Process -FilePath $frontendFile | Out-Null
    Write-Host "Opened frontend: $frontendFile"
} else {
    Write-Warning "Frontend file not found at $frontendFile"
}

Write-Host "Dev launcher completed."
