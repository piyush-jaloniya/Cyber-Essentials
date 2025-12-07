# Intune Deployment Script for CE Agent
# Package this script as a Win32 app in Intune

param(
    [string]$ControllerUrl = "https://controller.local:8000",
    [string]$InstallPath = "C:\Program Files\CyberEssentials\Agent"
)

$ErrorActionPreference = "Stop"
$LogPath = "C:\ProgramData\CyberEssentials\install.log"

# Create log directory
$logDir = Split-Path $LogPath
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogPath -Append
    Write-Host $Message
}

Write-Log "=== CE Agent Intune Deployment Started ==="

try {
    # Create installation directory
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Log "Created directory: $InstallPath"
    }
    
    # Copy agent files from package directory
    $packageDir = $PSScriptRoot
    Copy-Item "$packageDir\agent.py" -Destination $InstallPath -Force
    Copy-Item "$packageDir\config.py" -Destination $InstallPath -Force
    Copy-Item "$packageDir\token_store.py" -Destination $InstallPath -Force
    Copy-Item "$packageDir\requirements.txt" -Destination $InstallPath -Force
    Write-Log "Agent files copied successfully"
    
    # Check Python installation
    $pythonPath = "C:\Python311\python.exe"
    if (-not (Test-Path $pythonPath)) {
        Write-Log "ERROR: Python not found. Installing Python..."
        
        # Download and install Python (silent install)
        $pythonInstaller = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe" -OutFile $pythonInstaller
        
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
        Remove-Item $pythonInstaller -Force
        
        Write-Log "Python installed successfully"
    }
    
    # Install dependencies
    Write-Log "Installing Python dependencies..."
    & $pythonPath -m pip install --upgrade pip 2>&1 | Out-File -FilePath $LogPath -Append
    & $pythonPath -m pip install -r "$InstallPath\requirements.txt" 2>&1 | Out-File -FilePath $LogPath -Append
    Write-Log "Dependencies installed successfully"
    
    # Register agent with controller
    Write-Log "Registering agent with controller ($ControllerUrl)..."
    & $pythonPath "$InstallPath\agent.py" --register --controller $ControllerUrl 2>&1 | Out-File -FilePath $LogPath -Append
    
    if ($LASTEXITCODE -ne 0) {
        throw "Agent registration failed with exit code $LASTEXITCODE"
    }
    
    Write-Log "Agent registered successfully"
    
    # Install as service using NSSM (if available) or create scheduled task
    if (Get-Command nssm -ErrorAction SilentlyContinue) {
        Write-Log "Installing agent as Windows service..."
        
        $serviceName = "CEAgent"
        nssm stop $serviceName 2>$null
        nssm remove $serviceName confirm 2>$null
        
        nssm install $serviceName $pythonPath "$InstallPath\agent.py --daemon"
        nssm set $serviceName AppDirectory $InstallPath
        nssm set $serviceName DisplayName "Cyber Essentials Agent"
        nssm set $serviceName Description "Fleet management agent for Cyber Essentials compliance"
        nssm set $serviceName Start SERVICE_AUTO_START
        nssm set $serviceName AppEnvironmentExtra "CE_CONTROLLER_URL=$ControllerUrl"
        
        nssm start $serviceName
        Write-Log "Service installed and started"
        
    } else {
        Write-Log "NSSM not available, creating scheduled task..."
        
        $taskName = "CyberEssentialsAgent"
        
        # Remove existing task
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        
        # Create new task
        $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$InstallPath\agent.py --daemon" -WorkingDirectory $InstallPath
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3
        
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
        Start-ScheduledTask -TaskName $taskName
        
        Write-Log "Scheduled task created and started"
    }
    
    # Write version file
    "0.2.0" | Out-File -FilePath "$InstallPath\version.txt" -Force
    
    Write-Log "=== CE Agent Intune Deployment Completed Successfully ==="
    exit 0
    
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log $_.ScriptStackTrace
    exit 1
}
