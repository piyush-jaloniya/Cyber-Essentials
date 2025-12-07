# Install CE Agent as Windows Service using NSSM
# Requires: NSSM (Non-Sucking Service Manager)
# Download from: https://nssm.cc/download

param(
    [string]$ControllerUrl = "https://controller.local:8000",
    [string]$InstallPath = "C:\Program Files\CyberEssentials\Agent",
    [string]$PythonPath = "C:\Python311\python.exe"
)

Write-Host "Installing Cyber Essentials Agent Service..." -ForegroundColor Green

# Check if NSSM is available
if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: NSSM not found. Please install NSSM first." -ForegroundColor Red
    Write-Host "Download from: https://nssm.cc/download" -ForegroundColor Yellow
    exit 1
}

# Create install directory
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
}

# Copy agent files
Copy-Item "agent.py" -Destination $InstallPath
Copy-Item "config.py" -Destination $InstallPath
Copy-Item "token_store.py" -Destination $InstallPath
Copy-Item "requirements.txt" -Destination $InstallPath

# Install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Cyan
& $PythonPath -m pip install -r "$InstallPath\requirements.txt"

# Install service using NSSM
$serviceName = "CEAgent"
$agentScript = Join-Path $InstallPath "agent.py"

Write-Host "Installing service '$serviceName'..." -ForegroundColor Cyan

# Remove existing service if present
nssm stop $serviceName 2>$null
nssm remove $serviceName confirm 2>$null

# Install new service
nssm install $serviceName $PythonPath "$agentScript --daemon"
nssm set $serviceName AppDirectory $InstallPath
nssm set $serviceName DisplayName "Cyber Essentials Agent"
nssm set $serviceName Description "Fleet management agent for Cyber Essentials compliance scanning"
nssm set $serviceName Start SERVICE_AUTO_START
nssm set $serviceName AppStdout "$InstallPath\ce-agent.log"
nssm set $serviceName AppStderr "$InstallPath\ce-agent-error.log"

# Set environment variables
nssm set $serviceName AppEnvironmentExtra "CE_CONTROLLER_URL=$ControllerUrl"

Write-Host "Service installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Register the agent: cd '$InstallPath' && python agent.py --register --controller $ControllerUrl"
Write-Host "2. Start the service: nssm start $serviceName"
Write-Host "3. Check status: nssm status $serviceName"
Write-Host ""
Write-Host "Service logs: $InstallPath\ce-agent.log" -ForegroundColor Cyan
