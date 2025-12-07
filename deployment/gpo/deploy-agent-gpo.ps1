# GPO Deployment Script for CE Agent
# This script should be deployed via GPO as a startup or logon script

param(
    [string]$ControllerUrl = "https://controller.local:8000",
    [string]$NetworkShare = "\\domain.local\NETLOGON\CyberEssentials",
    [string]$InstallPath = "C:\Program Files\CyberEssentials\Agent"
)

$ErrorActionPreference = "Stop"

# Create log directory
$LogPath = "C:\Windows\Temp\ce-agent-install.log"

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogPath -Append
    Write-Host $Message
}

Write-Log "=== CE Agent GPO Deployment Started ==="

try {
    # Check if agent is already installed and up to date
    $installedVersion = $null
    if (Test-Path "$InstallPath\version.txt") {
        $installedVersion = Get-Content "$InstallPath\version.txt"
    }
    
    $networkVersion = Get-Content "$NetworkShare\version.txt"
    
    if ($installedVersion -eq $networkVersion) {
        Write-Log "Agent already up to date (version: $installedVersion)"
        exit 0
    }
    
    Write-Log "Installing CE Agent from network share..."
    Write-Log "Source: $NetworkShare"
    Write-Log "Destination: $InstallPath"
    
    # Create installation directory
    if (-not (Test-Path $InstallPath)) {
        New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null
        Write-Log "Created directory: $InstallPath"
    }
    
    # Copy agent files
    Copy-Item "$NetworkShare\*" -Destination $InstallPath -Recurse -Force
    Write-Log "Agent files copied successfully"
    
    # Check if Python is installed
    $pythonPath = "C:\Python311\python.exe"
    if (-not (Test-Path $pythonPath)) {
        Write-Log "ERROR: Python not found at $pythonPath"
        Write-Log "Please install Python 3.11+ on all workstations"
        exit 1
    }
    
    # Install Python dependencies
    Write-Log "Installing Python dependencies..."
    & $pythonPath -m pip install -r "$InstallPath\requirements.txt" 2>&1 | Out-File -FilePath $LogPath -Append
    
    # Register agent if not already registered
    $tokenPath = "$env:USERPROFILE\AppData\Roaming\CyberEssentials\.agent_token"
    if (-not (Test-Path $tokenPath)) {
        Write-Log "Registering agent with controller..."
        & $pythonPath "$InstallPath\agent.py" --register --controller $ControllerUrl 2>&1 | Out-File -FilePath $LogPath -Append
    } else {
        Write-Log "Agent already registered"
    }
    
    # Create scheduled task for agent daemon
    $taskName = "CyberEssentialsAgent"
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    
    if (-not $existingTask) {
        Write-Log "Creating scheduled task for agent daemon..."
        
        $action = New-ScheduledTaskAction -Execute $pythonPath -Argument "$InstallPath\agent.py --daemon"
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Force | Out-Null
        Write-Log "Scheduled task created successfully"
    } else {
        Write-Log "Scheduled task already exists"
    }
    
    # Start the scheduled task
    Start-ScheduledTask -TaskName $taskName
    Write-Log "Agent started successfully"
    
    Write-Log "=== CE Agent GPO Deployment Completed Successfully ==="
    
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    Write-Log $_.ScriptStackTrace
    exit 1
}
