# Cyber Essentials Agent

Fleet agent for remote compliance scanning.

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Register with controller
python agent.py --register --controller https://controller.local

# Start daemon
python agent.py --daemon
```

## Usage

### Register Agent

```bash
python agent.py --register --controller https://controller.local
```

This will:
1. Connect to controller
2. Send system information
3. Receive and store agent token
4. Print agent ID

### Run One-Shot Scan

```bash
python agent.py --scan --mode standard
```

Modes:
- `standard` - Personal/BYOD devices
- `strict` - Corporate/managed devices

### Start Daemon

```bash
python agent.py --daemon
```

This will:
1. Send heartbeat every 60 seconds
2. Poll for commands every 30 seconds
3. Run scheduled scans (daily at 2:00 AM)
4. Execute remote scan commands

## Configuration

### Environment Variables

```bash
CE_CONTROLLER_URL=https://controller.local:8000
CE_VERIFY_SSL=true
CE_HEARTBEAT_INTERVAL=60
CE_COMMAND_POLL_INTERVAL=30
CE_SCAN_SCHEDULE=daily
CE_LOG_LEVEL=INFO
CE_LOG_FILE=ce-agent.log
```

### Configuration File

Create `config.py` and override defaults:

```python
CONTROLLER_URL = "https://controller.yourdomain.com"
HEARTBEAT_INTERVAL = 60
SCAN_SCHEDULE = "daily"  # daily, weekly, manual
```

## Deployment

### Windows Service (NSSM)

```powershell
cd ../deployment/windows
.\install-agent-service.ps1 -ControllerUrl "https://controller.local"
```

### Linux Systemd

```bash
sudo cp ../deployment/systemd/ce-agent.service /etc/systemd/system/
sudo systemctl enable ce-agent
sudo systemctl start ce-agent
```

### macOS LaunchDaemon

```bash
sudo cp ../deployment/macos/com.cyberessentials.agent.plist /Library/LaunchDaemons/
sudo launchctl load /Library/LaunchDaemons/com.cyberessentials.agent.plist
```

See [../docs/deployment/AGENT_DEPLOYMENT.md](../docs/deployment/AGENT_DEPLOYMENT.md) for detailed deployment options.

## Troubleshooting

### Registration Failed

```bash
# Check controller connectivity
curl https://controller.local/health

# Try without SSL verification (testing only)
python agent.py --register --controller http://controller.local --no-verify-ssl
```

### Agent Not Reporting

```bash
# Check agent logs
tail -f ce-agent.log  # Linux/macOS
type ce-agent.log     # Windows

# Test scan manually
python agent.py --scan --mode standard

# Check service status
sudo systemctl status ce-agent  # Linux
nssm status CEAgent             # Windows
```

### Token Storage Issues

Token is stored:
- **Windows:** Credential Manager (DPAPI)
- **macOS:** Keychain
- **Linux:** System keyring or `~/.config/cyber-essentials/.agent_token`

To re-register, clear token:
```bash
# Delete from keyring or
rm ~/.config/cyber-essentials/.agent_token
```

## Security

### Token Storage

Tokens are stored securely using OS-native credential stores:
- Windows: Data Protection API (DPAPI)
- macOS: Keychain Services
- Linux: keyring library or encrypted file (0600 permissions)

### Network Security

- All communication over HTTPS/TLS
- Bearer token authentication
- Certificate verification enabled by default

## Development

### Test Locally

```bash
# Run standalone scan (no controller)
cd ..
python -m scanner.main --output test-report.json

# Test agent registration
python agent.py --register --controller http://localhost:8000 --no-verify-ssl

# Test one-shot scan with upload
python agent.py --scan --mode standard
```

### Debug Mode

```bash
export CE_LOG_LEVEL=DEBUG
python agent.py --daemon
```

## Commands Reference

```bash
# Registration
python agent.py --register --controller URL

# One-shot scan
python agent.py --scan [--mode standard|strict]

# Daemon mode
python agent.py --daemon

# Disable SSL verification (testing only)
python agent.py --no-verify-ssl

# Help
python agent.py --help
```
