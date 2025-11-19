# GUI Quick Start Guide

## Installation

```bash
pip install PySide6
```

## Launch

```bash
python run_gui.py
```

## Basic Usage

### 1. Configure Your Scan

| Setting | Options | Description |
|---------|---------|-------------|
| **Compliance Mode** | Standard / Strict | Standard for personal devices, Strict for corporate |
| **Output Format** | JSON / HTML / Both | Report file format |
| **Report Name** | `report.json` | Custom filename (default: report.json) |
| **Options** | ☐ Compare / ☐ Remediation | Optional features |

### 2. Run Scan

1. Click **"🔍 Start Scan"**
2. Watch progress in real-time
3. Review results when complete

### 3. View Results

Switch between tabs:
- **📝 Scan Progress** - Real-time log
- **📊 Results Summary** - Status table with scores
- **📄 Detailed Report** - Complete findings
- **💡 Recommendations** - Action items

## Quick Reference

### Status Colors

- 🟢 **PASS** - Compliant
- 🟡 **WARN** - Warnings only
- 🔴 **FAIL** - Not compliant
- ⚪ **UNKNOWN** - Need admin privileges

### Control Areas

1. **Firewalls** - Host firewall enabled
2. **Secure Configuration** - System hardening
3. **Access Control** - Passwords, MFA
4. **Malware Protection** - AV, encryption
5. **Patch Management** - Updates current
6. **Remote Work & MDM** - VPN, device management

### Keyboard Shortcuts

- **Tab** - Navigate controls
- **Enter** - Activate button
- **Space** - Toggle checkbox

## Troubleshooting

**GUI won't start?**
```bash
pip install --upgrade --force-reinstall PySide6
```

**All results UNKNOWN?**
- Run with administrator/sudo privileges

**Scan freezes?**
- Click "⏹ Stop" button
- Restart GUI

## Need Help?

📖 See [GUI_GUIDE.md](GUI_GUIDE.md) for complete documentation

---

**Version:** 1.0.0  
**Compatible with:** Scanner v0.2.0  
**Standard:** UK Cyber Essentials v3.2 (2025)
