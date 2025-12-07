# Cyber Essentials System Scanner AI Agent

**Updated for Cyber Essentials 2025 (v3.2 "Willow") Requirements**

This tool scans a workstation for the Cyber Essentials control areas and produces a structured JSON report covering:
- Firewalls
- Secure Configuration
- Access Control (with **MANDATORY MFA**)
- Malware Protection (with **MANDATORY Encryption**)
- Patch Management (14-day rule for CVSS 7+)
- Remote Work & MDM (NEW for 2025)

It provides a machine-readable compliance status with recommendations and can be integrated into a website for end users to run locally and upload results.

## 🚀 NEW: Fleet Management

**Scale from single-system scanning to enterprise fleet management!**

The scanner now includes a complete **Controller-Agent architecture** for managing compliance across multiple endpoints:

- **Controller Server:** FastAPI backend with PostgreSQL database
- **Web Dashboard:** React-based admin interface
- **Fleet Agent:** Lightweight daemon for remote scanning
- **Deployment Tools:** GPO, Intune, systemd, and LaunchDaemon scripts

👉 **See [FLEET_README.md](FLEET_README.md) for fleet management setup**
👉 **See [FLEET_ARCHITECTURE.md](FLEET_ARCHITECTURE.md) for architecture details**

## 🆕 What's New in 2025 (v0.2.0)

This scanner now includes **all critical Cyber Essentials 2025 requirements**:

### ✅ Mandatory MFA (Multi-Factor Authentication)
- Windows Hello, PIN, and biometric authentication detection
- Cloud MFA status (Azure AD/Microsoft 365)
- Touch ID support for macOS
- **CRITICAL**: MFA is now mandatory for ALL users (not just admins)

### 🔒 Mandatory Device Encryption
- BitLocker status for Windows
- FileVault status for macOS
- LUKS encryption for Linux
- **CRITICAL**: Encryption required for all portable/mobile devices

### ⏱️ 14-Day Patch Rule
- Changed from 30-day to **14-day** threshold for critical patches
- Checks for CVSS 7+ vulnerability remediation timeline
- Ensures only supported OS versions are in use

### 📱 Remote Work & MDM
- MDM enrollment detection (Intune, Jamf, etc.)
- Remote wipe capability verification
- VPN configuration for secure remote access
- Azure AD/cloud join status

### 🛡️ Enhanced Security Controls
- Default account detection (Administrator, Guest, DefaultAccount)
- Screen lock timeout verification (15-minute max)
- Application whitelisting (AppLocker, WDAC, Gatekeeper)
- OS support lifecycle verification

### 🎯 Compliance Modes (NEW)
- **Standard Mode:** For personal devices and BYOD (conditional checks as warnings)
- **Strict Mode (`--strict-mode`):** For corporate/managed devices (all checks mandatory)
- Automatic UAC elevation on Windows (no manual admin required)
- `--no-admin` flag for testing without privilege elevation

## Highlights
- **🖥️ Graphical User Interface (GUI)** - Modern PySide6-based interface for easy scanning
- Cross-platform (Windows, macOS, Linux)
- Modular checks with OS adapters
- Safe-by-default: returns `unknown` when OS information is unavailable or permissions are insufficient
- JSON report schema for ingestion and analytics
- Extensible AI summary hook (LLM integration optional on your backend)

## Quick Start

### Prerequisites
- Python 3.10+
- PySide6 (for GUI) - Optional, CLI works without it
- Some checks require elevated privileges (Administrator on Windows, sudo on Linux/macOS) for higher fidelity results
- The scanner will automatically prompt for admin elevation on Windows when needed

### Install
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install --upgrade pip
pip install PySide6  # For GUI support
```

### Run

#### Using the GUI (Recommended for Interactive Use)

**Launch the graphical interface:**
```bash
python run_gui.py
```

**Features:**
- Point-and-click configuration
- Real-time progress display
- Visual results with color-coded status
- Integrated report viewer
- Automatic report generation

See [GUI_GUIDE.md](GUI_GUIDE.md) for complete GUI documentation.

#### Using the Command Line

**Standard Mode (Personal/BYOD devices):**
```bash
python -m scanner.main
# Output: reports/report.json
```

**Strict Mode (Corporate/Managed devices):**
```bash
python -m scanner.main --strict-mode
# Output: reports/report.json
```

**Custom output location:**
```bash
python -m scanner.main --output reports/my_scan.json
```

**Skip Admin Prompt (for testing):**
```bash
python -m scanner.main --no-admin
```

**On Linux/macOS with elevated privileges:**
```bash
sudo python -m scanner.main --output report.json
```

### Example output
```json
{
  "scanner_version": "0.2.0",
  "timestamp_utc": "2025-11-14T10:30:00Z",
  "compliance_mode": "standard",
  "os": {
    "platform": "Windows",
    "version": "11 Home Single Language"
  },
  "controls": [
    {
      "name": "firewalls",
      "status": "pass",
      "score": 1.0,
      "findings": [],
      "recommendations": []
    },
    {
      "name": "secure_configuration",
      "status": "warn",
      "score": 0.6,
      "findings": [
        "RDP is enabled",
        "Guest account is enabled"
      ],
      "recommendations": [
        "Disable RDP unless strictly needed, or restrict to VPN/IP allowlist",
        "Disable the Guest account"
      ]
    }
  ],
  "overall": {
    "status": "warn",
    "score": 0.76
  }
}
```

## Compliance Modes

The scanner supports two compliance modes to accommodate different device types:

### Standard Mode (Default)
**For:** Personal devices, BYOD (Bring Your Own Device), home users

**Checks enforced:**
- ✅ Firewall enabled
- ✅ Antivirus/malware protection
- ✅ Patch management (14-day rule)
- ✅ Secure configuration (screen lock, default accounts)
- ✅ Access control (password policy, MFA recommended)

**Conditional checks (warnings only):**
- ⚠️ BitLocker/FileVault (recommended but not required)
- ⚠️ VPN configuration (if remote work applicable)
- ⚠️ MDM enrollment (if corporate device)
- ⚠️ Azure AD/cloud join (if managed device)

### Strict Mode (`--strict-mode`)
**For:** Corporate devices, managed workstations, compliance-critical environments

**All checks enforced:**
- ✅ Everything from Standard Mode
- ✅ **BitLocker/FileVault mandatory** (FAIL if not enabled)
- ✅ **VPN configuration required** (FAIL if missing)
- ✅ **MDM enrollment required** (FAIL if not enrolled)
- ✅ **Azure AD/cloud join required** (FAIL if not joined)

### When to Use Each Mode

| Device Type | Mode | Rationale |
|-------------|------|-----------|
| Personal laptop/desktop | Standard | BitLocker optional, no VPN/MDM expected |
| BYOD (Bring Your Own Device) | Standard | Employee-owned, limited corporate control |
| Corporate workstation | Strict | Full compliance required |
| Managed laptop | Strict | MDM, encryption, VPN mandatory |
| Development machine | Standard | Unless corporate policy requires strict |
| Production server | Strict | Maximum security posture required |

## What's Checked

### Firewalls ✅
- Windows: Defender Firewall (all profiles)
- macOS: Application Firewall status
- Linux: ufw/firewalld/nftables

### Secure Configuration ✅
- Windows: Guest/default accounts, RDP, SMBv1, screen lock timeout
- macOS: Guest login, Remote Login, screen saver
- Linux: SSH config, password policy, screen lock

### Access Control ✅
- Password policy (min length ≥8, complexity)
- MFA/Windows Hello/PIN (mandatory in CE 2025)
- Admin user count (≤3 recommended)
- Cloud MFA (Azure AD, Microsoft 365)

### Malware Protection ✅
- Antivirus status and real-time protection
- Device encryption (BitLocker/FileVault/LUKS)
  - Standard mode: Warning if disabled
  - Strict mode: Failure if disabled
- Application control (AppLocker/Gatekeeper/AppArmor)

### Patch Management ✅
- OS support status (no EOL systems allowed)
- Latest hotfix within 14 days (CE 2025 requirement)
- Pending updates detection
- Auto-update configuration

### Remote Work & MDM ✅ (NEW in CE 2025)
- MDM enrollment (Intune, Jamf, etc.)
- VPN configuration for remote access
- Azure AD/cloud join status
- Remote wipe capability
  - Standard mode: Warning if missing
  - Strict mode: Failure if missing

**Notes:**
- Elevated privileges required for full detection (BitLocker, hotfix history, etc.)
- Windows scanner automatically prompts for UAC elevation when needed
- `unknown` status indicates insufficient permissions or detection failure
- Use `--no-admin` flag to skip admin prompt for testing

## Admin Privilege Handling

### Automatic UAC Elevation (Windows)
The scanner automatically detects when it needs administrator privileges and prompts for UAC elevation:

```powershell
# Scanner detects it needs admin privileges
python -m scanner.main --output report.json

# Windows UAC prompt appears automatically
# User clicks "Yes" to allow elevation
# Scanner restarts with admin privileges
# Full scan runs with complete detection
```

### Flags
- **Default behavior:** Prompts for admin when needed
- **`--no-admin`:** Skips privilege check and UAC prompt (for testing)
- **`--strict-mode`:** Enables corporate compliance mode (still prompts for admin)

### Linux/macOS
```bash
sudo python -m scanner.main --output report.json
```

## Web Integration Pattern

1) Distribute the scanner binary/script to users (signed).
2) The scanner produces `report.json` locally.
3) Your website provides an Upload endpoint:
   - POST /api/upload-report
   - Body: JSON report
   - Validate schema, store, and optionally run AI summary for non-technical users.

Minimal API contract:
- Request body must conform to `report_schema/schema.json`
- Response:
  ```json
  { "ok": true, "reportId": "..." }
  ```

## Security and Privacy
- Principle of least privilege: many checks do not require admin; some do for accuracy.
- No collection of PII by default; machine/usernames can be hashed if included in future.
- Offline-first: report is created locally; users explicitly opt-in to upload.
- Signed distributions recommended, plus TLS pinning on uploader if feasible.

## Extending
- Add checks in `scanner/checks/` and use the `os` adapters.
- Add new AV vendor checks, org-specific baselines, or stricter password policies.
- Add an AI summary stage server-side using your preferred LLM with the JSON as context.

## License
MIT (example; pick what suits you)# Cyber-Essentials
