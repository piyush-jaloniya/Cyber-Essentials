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

## Highlights
- Cross-platform (Windows, macOS, Linux)
- Modular checks with OS adapters
- Safe-by-default: returns `unknown` when OS information is unavailable or permissions are insufficient
- JSON report schema for ingestion and analytics
- Extensible AI summary hook (LLM integration optional on your backend)

## Quick Start

### Prerequisites
- Python 3.10+
- Some checks require elevated privileges (Administrator on Windows, sudo on Linux/macOS) for higher fidelity results.

### Install
```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .\.venv\Scripts\activate
pip install --upgrade pip
```

### Run
```bash
python -m scanner.main --output report.json
```

Optional elevated permission:
```bash
sudo python -m scanner.main --output report.json
```

### Example output
```json
{
  "scanner_version": "0.1.0",
  "timestamp_utc": "2025-11-10T16:29:34Z",
  "os": {
    "platform": "Windows",
    "version": "10.0.19045"
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

## What’s Checked (initial coverage)

- Firewalls
  - Windows: Defender Firewall profiles enabled
  - macOS: Application Firewall status (socketfilterfw)
  - Linux: ufw/firewalld/nftables basic checks

- Secure Configuration
  - Windows: Guest account status, RDP, SMBv1
  - macOS: Guest login, Remote Login (SSH)
  - Linux: SSH config basics, password policy markers (login.defs/PAM presence)

- Access Control
  - Windows: Size of local Administrators group, password policy summary
  - macOS: Admin group members
  - Linux: sudo/wheel members

- Malware Protection
  - Windows: Registered AV via SecurityCenter2 (name and basic state if accessible)
  - macOS: Gatekeeper status, known AV presence (best-effort)
  - Linux: ClamAV presence and service state (if installed)

- Patch Management
  - Windows: Latest hotfix date (Get-HotFix) heuristic
  - macOS: softwareupdate history and pending update check
  - Linux: Pending updates via package manager discovery (apt/dnf/yum/zypper) heuristics

Notes:
- These are pragmatic, minimally invasive checks for a first pass. Production deployments often integrate with:
  - Enterprise AV/EDR APIs (Defender for Endpoint, CrowdStrike, etc.)
  - MDM/endpoint management APIs
  - Windows Update APIs, macOS MDM profiles, Linux patch management tooling
- Where data is unavailable, status may be `unknown` with actionable recommendations to re-run with elevated privileges.

## Web Integration Pattern

1) Distribute the scanner binary/script to users (signed).
2) The scanner produces `report.json` locally.
3) Your website provides an Upload endpoint:
   - POST /api/upload-report
   - Body: JSON report
   - Validate schema, store, and optionally run AI summary for non-technical users.

Minimal API contract:
- Request body must conform to `report/schema.json`
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
