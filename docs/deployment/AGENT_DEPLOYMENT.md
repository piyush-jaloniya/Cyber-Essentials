# Agent Deployment Guide

## Overview

The Cyber Essentials Agent is a lightweight daemon that runs on endpoints, performs compliance scans, and reports to the controller.

## Prerequisites

- Python 3.10+
- Network connectivity to controller
- Administrative privileges (for full scan functionality)

## Deployment Methods

### 1. Manual Installation (Windows)

1. **Install Python 3.11+:**
   - Download from https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH"
   - ✅ Check "Install for all users"

2. **Create installation directory:**
   ```powershell
   New-Item -ItemType Directory -Path "C:\Program Files\CyberEssentials\Agent" -Force
   cd "C:\Program Files\CyberEssentials\Agent"
   ```

3. **Copy agent files:**
   ```powershell
   # Copy from repository: agent/*.py and agent/requirements.txt
   ```

4. **Install dependencies:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

5. **Configure agent:**
   ```powershell
   $env:CE_CONTROLLER_URL = "https://controller.yourdomain.com"
   ```

6. **Register with controller:**
   ```powershell
   python agent.py --register --controller https://controller.yourdomain.com
   ```

7. **Install as service (using NSSM):**
   ```powershell
   # Download NSSM from https://nssm.cc/download
   nssm install CEAgent "C:\Python311\python.exe" "C:\Program Files\CyberEssentials\Agent\agent.py --daemon"
   nssm set CEAgent AppDirectory "C:\Program Files\CyberEssentials\Agent"
   nssm set CEAgent DisplayName "Cyber Essentials Agent"
   nssm start CEAgent
   ```

### 2. GPO Deployment (Windows Domain)

**Step 1: Prepare Network Share**

1. Create a network share accessible by all computers:
   ```powershell
   New-Item -ItemType Directory -Path "\\domain.local\NETLOGON\CyberEssentials"
   ```

2. Copy agent files to the share:
   - agent.py
   - config.py
   - token_store.py
   - requirements.txt
   - version.txt (contains "0.2.0")

3. Copy deployment script:
   - deployment/gpo/deploy-agent-gpo.ps1

**Step 2: Create GPO**

1. Open **Group Policy Management**
2. Create new GPO: "Deploy Cyber Essentials Agent"
3. Edit GPO → Computer Configuration → Policies → Windows Settings → Scripts
4. Add Startup Script:
   ```powershell
   Script: \\domain.local\NETLOGON\CyberEssentials\deploy-agent-gpo.ps1
   Parameters: -ControllerUrl "https://controller.yourdomain.com"
   ```

5. Link GPO to appropriate OU (e.g., Workstations)

**Step 3: Verify Deployment**

```powershell
# On target computer
Get-ScheduledTask -TaskName "CyberEssentialsAgent"
Test-Path "C:\Program Files\CyberEssentials\Agent\agent.py"
```

### 3. Intune Deployment (Modern Management)

**Step 1: Prepare Win32 App Package**

1. Create package directory:
   ```powershell
   mkdir CEAgent-Package
   cd CEAgent-Package
   ```

2. Copy files:
   - agent.py
   - config.py
   - token_store.py
   - requirements.txt
   - deployment/intune/deploy-agent-intune.ps1 (rename to install.ps1)

3. Create detection script (detect.ps1):
   ```powershell
   $path = "C:\Program Files\CyberEssentials\Agent\version.txt"
   if (Test-Path $path) {
       $version = Get-Content $path
       if ($version -eq "0.2.0") {
           Write-Output "Installed"
           exit 0
       }
   }
   exit 1
   ```

4. Package with Microsoft Win32 Content Prep Tool:
   ```powershell
   .\IntuneWinAppUtil.exe -c .\CEAgent-Package -s install.ps1 -o .\output
   ```

**Step 2: Create Intune App**

1. Go to Intune portal → Apps → Windows → Add
2. App type: Windows app (Win32)
3. Upload .intunewin file
4. Configure:
   - Name: Cyber Essentials Agent
   - Install command: `powershell.exe -ExecutionPolicy Bypass -File install.ps1 -ControllerUrl "https://controller.yourdomain.com"`
   - Uninstall command: `powershell.exe -Command "Unregister-ScheduledTask -TaskName CyberEssentialsAgent -Confirm:\$false"`
   - Install behavior: System
   - Detection: Use custom detection script (detect.ps1)

5. Assign to device groups

### 4. Linux Deployment (systemd)

1. **Install Python dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Create installation directory:**
   ```bash
   sudo mkdir -p /opt/ce-agent
   sudo cp agent/*.py /opt/ce-agent/
   sudo cp agent/requirements.txt /opt/ce-agent/
   ```

3. **Install Python packages:**
   ```bash
   cd /opt/ce-agent
   sudo pip3 install -r requirements.txt
   ```

4. **Register agent:**
   ```bash
   sudo python3 /opt/ce-agent/agent.py --register --controller https://controller.yourdomain.com
   ```

5. **Install systemd service:**
   ```bash
   sudo cp deployment/systemd/ce-agent.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable ce-agent
   sudo systemctl start ce-agent
   sudo systemctl status ce-agent
   ```

### 5. macOS Deployment (LaunchDaemon)

1. **Install Python (if needed):**
   ```bash
   brew install python@3.11
   ```

2. **Create installation directory:**
   ```bash
   sudo mkdir -p /opt/ce-agent
   sudo cp agent/*.py /opt/ce-agent/
   sudo cp agent/requirements.txt /opt/ce-agent/
   ```

3. **Install dependencies:**
   ```bash
   cd /opt/ce-agent
   sudo pip3 install -r requirements.txt
   ```

4. **Register agent:**
   ```bash
   sudo python3 /opt/ce-agent/agent.py --register --controller https://controller.yourdomain.com
   ```

5. **Install LaunchDaemon:**
   ```bash
   sudo cp deployment/macos/com.cyberessentials.agent.plist /Library/LaunchDaemons/
   sudo launchctl load /Library/LaunchDaemons/com.cyberessentials.agent.plist
   sudo launchctl start com.cyberessentials.agent
   ```

## Configuration

### Environment Variables

Create `.env` file in agent directory:

```bash
CE_CONTROLLER_URL=https://controller.yourdomain.com
CE_VERIFY_SSL=true
CE_HEARTBEAT_INTERVAL=60
CE_COMMAND_POLL_INTERVAL=30
CE_SCAN_SCHEDULE=daily
CE_LOG_LEVEL=INFO
```

### Scan Schedules

- `daily`: Runs at 2:00 AM every day
- `weekly`: Runs at 2:00 AM every Monday
- `manual`: Only runs when triggered by controller

## Testing

### Verify Registration

```bash
# Windows
python agent.py --register --controller https://controller.yourdomain.com

# Linux/macOS
sudo python3 agent.py --register --controller https://controller.yourdomain.com
```

### Run One-Shot Scan

```bash
# Windows
python agent.py --scan --mode standard

# Linux/macOS
sudo python3 agent.py --scan --mode standard
```

### Check Service Status

**Windows (NSSM):**
```powershell
nssm status CEAgent
Get-Service CEAgent
```

**Windows (Scheduled Task):**
```powershell
Get-ScheduledTask -TaskName "CyberEssentialsAgent"
```

**Linux:**
```bash
sudo systemctl status ce-agent
sudo journalctl -u ce-agent -f
```

**macOS:**
```bash
sudo launchctl list | grep cyberessentials
sudo tail -f /var/log/ce-agent.log
```

## Troubleshooting

### Agent won't register

1. **Check controller connectivity:**
   ```bash
   curl https://controller.yourdomain.com/health
   ```

2. **Verify SSL certificate:**
   ```bash
   # If self-signed, use --no-verify-ssl flag
   python agent.py --register --controller https://controller.local --no-verify-ssl
   ```

3. **Check firewall rules**

### Agent not reporting

1. **Check logs:**
   - Windows: `C:\Program Files\CyberEssentials\Agent\ce-agent.log`
   - Linux: `sudo journalctl -u ce-agent -n 50`
   - macOS: `/var/log/ce-agent.log`

2. **Verify token storage:**
   ```bash
   # Token should be stored in OS keyring or config directory
   ```

3. **Test connectivity:**
   ```bash
   python agent.py --scan --mode standard
   ```

### Service won't start

1. **Check Python installation:**
   ```bash
   python --version  # Should be 3.10+
   ```

2. **Verify file permissions:**
   ```bash
   # Linux/macOS
   ls -la /opt/ce-agent/
   ```

3. **Check service logs:**
   ```bash
   # Windows
   nssm status CEAgent

   # Linux
   sudo systemctl status ce-agent
   sudo journalctl -u ce-agent -e

   # macOS
   sudo launchctl list | grep cyberessentials
   ```

## Uninstallation

### Windows

```powershell
# Stop and remove service
nssm stop CEAgent
nssm remove CEAgent confirm

# Or remove scheduled task
Unregister-ScheduledTask -TaskName "CyberEssentialsAgent" -Confirm:$false

# Remove files
Remove-Item "C:\Program Files\CyberEssentials\Agent" -Recurse -Force
```

### Linux

```bash
sudo systemctl stop ce-agent
sudo systemctl disable ce-agent
sudo rm /etc/systemd/system/ce-agent.service
sudo systemctl daemon-reload
sudo rm -rf /opt/ce-agent
```

### macOS

```bash
sudo launchctl unload /Library/LaunchDaemons/com.cyberessentials.agent.plist
sudo rm /Library/LaunchDaemons/com.cyberessentials.agent.plist
sudo rm -rf /opt/ce-agent
```

## Security Considerations

1. **Token Storage:**
   - Windows: Stored in Credential Manager (DPAPI)
   - macOS: Stored in Keychain
   - Linux: Stored in system keyring or encrypted file

2. **Network Security:**
   - Always use HTTPS for controller communication
   - Verify SSL certificates (don't use --no-verify-ssl in production)

3. **File Permissions:**
   - Agent files should be owned by root/SYSTEM
   - Regular users should not have write access

4. **Logging:**
   - Logs may contain system information
   - Rotate logs regularly
   - Restrict log file access

## Best Practices

1. **Test in staging environment first**
2. **Deploy in phases** (pilot group → department → organization)
3. **Monitor initial deployments** for issues
4. **Document controller URL** and share with IT team
5. **Set up alerts** for offline agents
6. **Schedule regular updates** for agent software
7. **Backup agent configurations** before updates

## Support

For deployment issues:
- Check agent logs
- Verify controller connectivity
- Review firewall rules
- Contact IT support with error logs
