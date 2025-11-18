# Cyber Essentials Scanner - User Guide

A comprehensive compliance scanner for UK Cyber Essentials v3.2 (2025) "Willow" update.

## Table of Contents
- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Features](#features)
- [Configuration](#configuration)
- [Output Files](#output-files)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Cyber Essentials Scanner is a Python-based tool that assesses your Windows system against the UK Cyber Essentials certification requirements. It checks 6 core security controls and generates comprehensive reports in JSON and HTML formats.

**Supported Controls:**
1. Firewalls
2. Secure Configuration
3. Access Control
4. Malware Protection
5. Patch Management
6. Remote Work & MDM

---

## System Requirements

- **Operating System:** Windows 10/11 (Primary support), macOS, Linux (Basic support)
- **Python:** 3.11 or higher
- **Privileges:** Administrator/elevated privileges recommended for complete results
- **Disk Space:** ~50 MB for installation

---

## Installation

### Step 1: Clone the Repository

```powershell
git clone https://github.com/piyush-jaloniya/Cyber-Essentials.git
cd Cyber-Essentials
```

### Step 2: Create Virtual Environment

```powershell
python -m venv .venv
```

### Step 3: Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### Step 4: Install Dependencies

```powershell
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, the scanner has no external dependencies for CLI usage.

---

## Quick Start

### Basic Scan (Standard Mode)

```powershell
python -m scanner.main
```

This runs a scan with:
- **Mode:** Standard (Personal/BYOD)
- **Output:** `reports/json/report.json` and `reports/html/report.html`
- **Format:** JSON and HTML
- **Privileges:** Will prompt for admin elevation

### No Admin Prompt

```powershell
python -m scanner.main --no-admin
```

### Custom Output Location

```powershell
python -m scanner.main --output reports/my_scan.json --format both
```

---

## Usage

### Command Syntax

```powershell
python -m scanner.main [OPTIONS]
```

### Available Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--config` | `-c` | Path to configuration file | `ce-config.json` |
| `--output` | `-o` | Output file path | `reports/report.json` |
| `--format` | `-f` | Output format: `json`, `html`, or `both` | `json` |
| `--compare` | | Compare with previous scan results | Not enabled |
| `--generate-fix` | | Generate PowerShell remediation script (Windows only) | Not enabled |
| `--no-admin` | | Skip admin privilege check | Not enabled |
| `--strict-mode` | | Enable strict mode (corporate/managed devices) | Not enabled |
| `--verbose` | `-v` | Enable verbose logging for debugging | Not enabled |

### Examples

#### 1. Standard Scan with Both Formats

```powershell
python -m scanner.main --output reports/scan.json --format both
```

**Output:**
- `reports/json/scan.json`
- `reports/html/scan.html`

#### 2. Strict Mode (Corporate Compliance)

```powershell
python -m scanner.main --strict-mode --output reports/corporate.json --format both
```

Use strict mode for corporate/managed devices with stricter compliance requirements.

#### 3. Comparison with Previous Scan

```powershell
python -m scanner.main --output reports/scan.json --compare --format both
```

Shows changes (↑ improved, ↓ degraded, → unchanged) compared to the last scan.

**Output:**
- `reports/json/scan.json`
- `reports/html/scan.html`
- `reports/json/scan_comparison.json`

#### 4. Generate Remediation Script (Windows)

```powershell
python -m scanner.main --output reports/scan.json --generate-fix --format both
```

Creates a PowerShell script with automated fixes for common issues.

**Output:**
- `reports/json/scan.json`
- `reports/html/scan.html`
- `Auto_Fix_Scripts/scan_fix.ps1`

**To run the fix script:**
1. Right-click `Auto_Fix_Scripts/scan_fix.ps1`
2. Select "Run with PowerShell"
3. Approve UAC elevation prompt

#### 5. Full Featured Scan

```powershell
python -m scanner.main --output reports/full_scan.json --format both --compare --generate-fix --verbose
```

Combines all features with detailed logging.

#### 6. Custom Configuration File

```powershell
python -m scanner.main --config custom-config.json
```

---

## Features

### 1. **Logging & Error Handling**

The scanner includes comprehensive logging for troubleshooting:

```powershell
# Enable verbose logging
python -m scanner.main --verbose
```

Logs show:
- Command execution details
- Check progress
- Warnings and errors
- Timestamp for each operation

### 2. **Progress Feedback**

Real-time progress indicators:

```
[1/6] Checking Firewalls... ✓ PASS
[2/6] Checking Secure Configuration... ✓ PASS
[3/6] Checking Access Control... ? UNKNOWN
[4/6] Checking Malware Protection... ✓ PASS
[5/6] Checking Patch Management... ✓ PASS
[6/6] Checking Remote Work & MDM... ✓ PASS
```

**Status Icons:**
- ✓ PASS - Control meets requirements
- ✗ FAIL - Control does not meet requirements
- ⚠ WARN - Control has warnings
- ? UNKNOWN - Control status cannot be determined

### 3. **HTML Reports**

Professional, interactive HTML reports with:
- Color-coded status badges
- Collapsible sections
- Failed/warned controls auto-expanded
- Print-friendly format
- Overall score and status

**Opening HTML Reports:**
- Navigate to `reports/html/`
- Double-click the `.html` file
- Opens in your default browser

### 4. **Configuration Files**

Create `ce-config.json` for default settings:

```json
{
  "compliance_mode": "standard",
  "output": {
    "path": "reports/report.json",
    "format": "both"
  },
  "device_info": {
    "organization": "Your Organization",
    "device_name": "DESKTOP-001",
    "device_type": "Laptop"
  },
  "logging": {
    "level": "INFO",
    "file": "scanner.log"
  },
  "skip_admin_check": false
}
```

**Configuration Options:**

- `compliance_mode`: `"standard"` or `"strict"`
- `output.format`: `"json"`, `"html"`, or `"both"`
- `logging.level`: `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`
- `skip_admin_check`: `true` or `false`

### 5. **Scan Comparison**

Compare scans to track security posture over time:

```powershell
python -m scanner.main --output reports/weekly.json --compare
```

**Comparison Output:**
```
============================================================
📊 SCAN COMPARISON
============================================================
Previous: 2025-11-17T10:00:00Z
Current:  2025-11-18T10:00:00Z

Overall Status: WARN → PASS ↑
Overall Score:  0.8 → 0.95 (+0.15)

Control Changes:
  ↑ Improved:  2
  ↓ Degraded:  0
  → Unchanged: 4

Details:
  Access Control: WARN → PASS ↑
  Patch Management: PASS → PASS →
```

### 6. **Remediation Automation**

Automatically generate PowerShell scripts to fix common issues:

```powershell
python -m scanner.main --generate-fix
```

**Automated Fixes Include:**
- Enable screen lock timeout (15 minutes)
- Enable password-protected screen saver
- Configure Windows Update settings
- Enable Windows Firewall
- Enable Windows Defender real-time protection
- Enable User Account Control (UAC)
- Enable automatic updates

**Running Remediation Scripts:**
1. Scan completes and generates `Auto_Fix_Scripts/report_fix.ps1`
2. Right-click the script
3. Select "Run with PowerShell"
4. Approve UAC prompt
5. Review on-screen progress
6. Reboot if prompted

---

## Configuration

### Compliance Modes

#### Standard Mode (Default)
For personal devices and BYOD (Bring Your Own Device):
- More lenient requirements
- Suitable for home users
- Focuses on essential security

```powershell
python -m scanner.main
```

#### Strict Mode
For corporate/managed devices:
- Stricter compliance requirements
- Additional security checks
- Required for enterprise certification

```powershell
python -m scanner.main --strict-mode
```

### Output Formats

#### JSON (Machine-readable)
```powershell
python -m scanner.main --format json
```

Saves to: `reports/json/report.json`

#### HTML (Human-readable)
```powershell
python -m scanner.main --format html
```

Saves to: `reports/html/report.html`

#### Both (Default for most use cases)
```powershell
python -m scanner.main --format both
```

Saves to:
- `reports/json/report.json`
- `reports/html/report.html`

---

## Output Files

### Folder Structure

```
ce/
├── reports/
│   ├── json/              # JSON reports
│   │   ├── report.json
│   │   ├── scan_comparison.json
│   │   └── ...
│   └── html/              # HTML reports
│       ├── report.html
│       └── ...
├── Auto_Fix_Scripts/      # PowerShell remediation scripts
│   ├── report_fix.ps1
│   └── ...
└── scanner.log            # Optional log file (if configured)
```

### JSON Report Structure

```json
{
  "scanner_version": "0.2.0",
  "timestamp_utc": "2025-11-18T10:00:00Z",
  "compliance_mode": "standard",
  "os": {
    "platform": "Microsoft Windows 11 Home Single Language",
    "version": "10.0.26200"
  },
  "controls": [
    {
      "name": "Firewalls",
      "status": "pass",
      "score": 1.0,
      "findings": ["Windows Firewall is enabled"],
      "recommendations": [],
      "details": { ... }
    }
  ],
  "overall": {
    "status": "pass",
    "score": 0.95
  }
}
```

### HTML Report Features

- **Header:** Scanner version, timestamp, OS info
- **Overall Status:** Large color-coded badge (PASS/WARN/FAIL)
- **Score:** Visual percentage indicator
- **Controls:** Expandable sections for each control
- **Findings:** Bullet-pointed list of issues
- **Recommendations:** Actionable advice
- **Print-Friendly:** Optimized for PDF export

---

## Troubleshooting

### Issue: "Not running as Administrator" Warning

**Cause:** Some checks require elevated privileges.

**Solution:**
```powershell
# Option 1: Allow scanner to elevate automatically
python -m scanner.main
# When prompted, press 'Y' to elevate

# Option 2: Run PowerShell as Administrator first
# Right-click PowerShell → "Run as Administrator"
cd C:\path\to\ce
.venv\Scripts\Activate.ps1
python -m scanner.main

# Option 3: Skip admin check (incomplete results)
python -m scanner.main --no-admin
```

### Issue: Virtual Environment Not Activated

**Symptoms:**
```
ModuleNotFoundError: No module named 'scanner'
```

**Solution:**
```powershell
# Activate virtual environment first
.venv\Scripts\Activate.ps1

# Then run scanner
python -m scanner.main
```

### Issue: Reports Not Found

**Cause:** Looking in wrong folder or output path misconfigured.

**Solution:**
```powershell
# Reports are organized by type:
# - JSON reports: reports/json/
# - HTML reports: reports/html/

# List all reports
Get-ChildItem reports\json\
Get-ChildItem reports\html\
```

### Issue: "Command returned non-zero exit code" Messages

**Cause:** Normal probing for optional features (not actual errors).

**Solution:** These are debug messages and can be safely ignored. They only appear when commands check for features that may not be configured.

To suppress them completely, use default logging (not `--verbose`).

### Issue: UNKNOWN Status for Controls

**Cause:** Insufficient privileges or missing system features.

**Solutions:**
1. Run with administrator privileges
2. Some features (like BitLocker, Windows Hello) may not be available on all editions
3. Re-run scan after enabling features in Windows Settings

### Issue: Comparison Fails

**Cause:** No previous scan found.

**Solution:**
```powershell
# Run first scan to create baseline
python -m scanner.main --output reports/scan.json

# Subsequent runs can use --compare
python -m scanner.main --output reports/scan.json --compare
```

### Issue: Remediation Script Won't Run

**Cause:** PowerShell execution policy restrictions.

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy

# Temporarily allow script execution (run as Admin)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Run the script
.\Auto_Fix_Scripts\report_fix.ps1

# Or right-click script → "Run with PowerShell"
```

---

## Advanced Usage

### Automated Scanning (Scheduled Tasks)

Create a scheduled task to run weekly scans:

```powershell
# Create a batch file: C:\ce\run_scan.bat
@echo off
cd C:\Users\HP\Downloads\ce
call .venv\Scripts\activate.bat
python -m scanner.main --no-admin --output reports\weekly_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.json --format both --compare
```

Then create a Windows Task Scheduler task to run `run_scan.bat` weekly.

### Integration with CI/CD

Use the scanner in automated pipelines:

```powershell
# Exit with non-zero code if scan fails
python -m scanner.main --output reports\ci_scan.json --format json --no-admin

# Parse JSON output for pass/fail
$result = Get-Content reports\json\ci_scan.json | ConvertFrom-Json
if ($result.overall.status -eq "fail") {
    exit 1
}
```

### Programmatic Usage

Use the scanner as a Python library:

```python
from scanner.runner import run_scan

# Run scan programmatically
result = run_scan(
    output_path='reports/api_scan.json',
    output_format='both',
    strict_mode=False,
    compare=False,
    generate_fix=False,
    skip_admin=True,
    progress_callback=lambda msg: print(f"Progress: {msg}")
)

print(f"JSON: {result['json_path']}")
print(f"HTML: {result['html_path']}")
print(f"Status: {result['doc']['overall']['status']}")
print(f"Score: {result['doc']['overall']['score']}")
```

---

## Support

**Issues:** https://github.com/piyush-jaloniya/Cyber-Essentials/issues

**Documentation:** See `IMPROVEMENTS.md` for detailed feature documentation

**License:** Check `LICENSE` file in repository

---

## Version History

**v0.2.0 (Current)**
- UK Cyber Essentials v3.2 (2025) "Willow" compliance
- 6 security controls
- JSON and HTML reports
- Comparison mode
- Remediation automation
- Intelligent status logic
- Logging and verbose mode
- Configuration file support

---

## Quick Reference Card

```powershell
# Basic scan
python -m scanner.main

# Full featured scan
python -m scanner.main --output reports/scan.json --format both --compare --generate-fix

# Corporate scan
python -m scanner.main --strict-mode --output reports/corp.json --format both

# No admin (incomplete results)
python -m scanner.main --no-admin

# Debug mode
python -m scanner.main --verbose

# Custom config
python -m scanner.main --config my-config.json
```

**Output Locations:**
- JSON: `reports/json/`
- HTML: `reports/html/`
- Fixes: `Auto_Fix_Scripts/`

**Status Codes:**
- ✓ PASS - Compliant
- ⚠ WARN - Warnings
- ✗ FAIL - Non-compliant
- ? UNKNOWN - Cannot determine

---

*Last Updated: November 18, 2025*
