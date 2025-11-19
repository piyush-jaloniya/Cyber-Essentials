# Cyber Essentials Scanner - GUI Guide

## Overview

The Cyber Essentials Scanner now includes a modern graphical user interface (GUI) built with PySide6, providing an intuitive way to run security compliance scans without using the command line.

## Screenshots

### Main Window
![GUI Main Window](https://github.com/user-attachments/assets/9f9481f0-8f11-4957-98e9-876328614032)

### Results View
![GUI Results View](https://github.com/user-attachments/assets/78a5de3e-9b9e-439a-a565-5cc9708f806c)

## Installation

### Prerequisites
- Python 3.10 or higher
- PySide6 (Qt 6 for Python)

### Install Dependencies

```bash
pip install PySide6
```

## Running the GUI

### Method 1: Using the Launcher Script (Recommended)
```bash
python run_gui.py
```

### Method 2: Using Python Module
```bash
python -m scanner.gui
```

### Method 3: Direct Execution
```bash
python scanner/gui.py
```

## Features

### 1. Scan Configuration Panel

The configuration panel at the top allows you to customize your scan:

#### **Compliance Mode**
- **Standard (Personal/BYOD)**: For personal devices and BYOD scenarios
  - Encryption, VPN, and MDM are warnings (not failures)
  - Suitable for home users and personal laptops
- **Strict (Corporate/Managed)**: For corporate and managed devices
  - All checks are mandatory
  - Encryption, VPN, and MDM failures will cause overall FAIL status

#### **Output Format**
- **Both (JSON + HTML)**: Creates both report formats (recommended)
- **JSON Only**: Creates only the JSON report
- **HTML Only**: Creates only the HTML report

#### **Options**
- ☑️ **Compare with previous scan**: Enables comparison with the last scan to track changes
- ☑️ **Generate remediation script**: Creates an automated PowerShell fix script (Windows only)

#### **Report Name**
- Specify the output filename (default: `report.json`)
- Reports are saved in `reports/json/` and `reports/html/` folders
- Use the "Browse..." button to select a custom location

### 2. Scan Controls

Three main control buttons:

- **🔍 Start Scan**: Begin the security compliance scan
- **⏹ Stop**: Cancel the current scan (if running)
- **🗑 Clear Results**: Clear all displayed results and reset the interface

### 3. Progress Bar

The progress bar shows:
- Scan progress percentage (0-100%)
- Current status message
- "Ready" when idle, "Scanning..." during scan, "Complete" when finished

### 4. Tabbed Results Interface

#### **📝 Scan Progress Tab**
- Real-time progress messages during the scan
- Shows which control is being checked
- Displays status for each completed check
- Auto-scrolls to show latest messages

#### **📊 Results Summary Tab**
- **Overall Status**: PASS/WARN/FAIL/UNKNOWN with color coding
- **Overall Score**: Numerical score out of 100
- **Controls Table**: Detailed breakdown of all 6 control areas
  - Control name
  - Status (color-coded)
  - Score (0.0 to 1.0)
  - Summary of findings

#### **📄 Detailed Report Tab**
- Complete text report with all findings
- System information (OS, version, scanner version)
- Detailed findings for each control area
- Timestamps and compliance mode

#### **💡 Recommendations Tab**
- Actionable recommendations for each failed or warned control
- Organized by control area
- Clear steps to improve compliance

### 5. Status Bar

Bottom status bar shows:
- Current operation status
- File paths for saved reports
- Success/error messages

## Control Areas Checked

The GUI scanner checks all 6 Cyber Essentials 2025 control areas:

1. **🔥 Firewalls**: Host firewall status and configuration
2. **⚙️ Secure Configuration**: System hardening, screen lock, default accounts
3. **🔐 Access Control**: Password policy, MFA/Windows Hello, admin users
4. **🛡️ Malware Protection**: Antivirus, encryption, application control
5. **📦 Patch Management**: OS support status, pending updates (14-day rule)
6. **📱 Remote Work & MDM**: VPN configuration, MDM enrollment, cloud join

## Status Indicators

### Color Coding
- 🟢 **Green (PASS)**: Control meets all requirements
- 🟡 **Yellow (WARN)**: Control has warnings but not critical failures
- 🔴 **Red (FAIL)**: Control does not meet requirements
- ⚪ **Gray (UNKNOWN)**: Status cannot be determined (often needs admin privileges)

### Overall Status Logic
- **PASS**: All controls passed, overall score ≥ 85%
- **WARN**: Some controls have warnings, no failures
- **FAIL**: One or more controls failed
- **UNKNOWN**: Cannot determine status (insufficient privileges)

## Usage Examples

### Example 1: Personal Device Scan

1. Launch the GUI: `python run_gui.py`
2. Select **"Standard (Personal/BYOD)"** mode
3. Keep default settings
4. Click **"🔍 Start Scan"**
5. Wait for completion
6. Review results in the **"Results Summary"** tab
7. Check **"Recommendations"** tab for any improvements

### Example 2: Corporate Device Compliance Check

1. Launch the GUI: `python run_gui.py`
2. Select **"Strict (Corporate/Managed)"** mode
3. Check ☑️ **"Generate remediation script"**
4. Enter report name: `corporate_scan.json`
5. Click **"🔍 Start Scan"**
6. Review results - all checks must PASS for compliance
7. If failures exist, use the generated PowerShell script to fix issues

### Example 3: Tracking Changes Over Time

1. Run an initial scan and save as `baseline.json`
2. Make system changes (enable BitLocker, configure MFA, etc.)
3. Run a new scan with the same filename
4. Check ☑️ **"Compare with previous scan"**
5. Review the comparison report showing improvements

## Report Files

After scanning, the GUI creates reports in organized folders:

```
reports/
├── json/
│   ├── report.json           # JSON report
│   └── report_comparison.json # Comparison (if enabled)
└── html/
    └── report.html           # HTML report
```

### Opening Reports

- **JSON reports**: Open with any text editor or JSON viewer
- **HTML reports**: Open in any web browser for a formatted view
- **Comparison reports**: JSON format showing differences between scans

## Remediation Scripts

When you enable **"Generate remediation script"**, the GUI creates an automated fix script:

```
Auto_Fix_Scripts/
└── report_fix.ps1    # PowerShell script to fix detected issues
```

### Using Remediation Scripts (Windows Only)

1. Right-click the `.ps1` file
2. Select **"Run with PowerShell"**
3. Accept the UAC prompt (requires Administrator)
4. The script will automatically fix common issues:
   - Enable Windows Defender Firewall
   - Disable Guest account
   - Configure password policies
   - And more...

5. Re-run the scanner to verify fixes

## Admin Privileges

Some checks require elevated privileges for complete detection:

### Windows
- BitLocker encryption status
- Windows Update hotfix history
- Full NGC/Windows Hello configuration
- Detailed security policies

### Linux/macOS
- Encryption status (FileVault, LUKS)
- System-wide security settings
- MDM enrollment details

### How to Run with Admin Privileges

**Windows:**
```bash
# Right-click Command Prompt or PowerShell
# Select "Run as Administrator"
python run_gui.py
```

**Linux/macOS:**
```bash
sudo python run_gui.py
```

The GUI will indicate if admin privileges are recommended based on the results.

## Troubleshooting

### GUI Won't Start

**Issue**: ImportError or "cannot open shared object file"

**Solution**:
```bash
# Install required system libraries (Linux)
sudo apt-get install libegl1 libxkbcommon0 libdbus-1-3

# Reinstall PySide6
pip install --upgrade --force-reinstall PySide6
```

### All Results Show "UNKNOWN"

**Issue**: Scanner cannot detect system settings

**Cause**: Insufficient privileges

**Solution**: Run the GUI with administrator/sudo privileges

### Scan Hangs or Freezes

**Issue**: GUI becomes unresponsive during scan

**Solution**: 
- Click the **"⏹ Stop"** button
- Close and restart the GUI
- Check system resources (CPU, memory)

### Report Not Generated

**Issue**: No report files created after scan

**Solution**:
- Check write permissions in the `reports/` folder
- Ensure the output path is valid
- Review the "Scan Progress" tab for error messages

### Remediation Script Doesn't Work

**Issue**: PowerShell script errors or no changes applied

**Cause**: Usually permission issues

**Solution**:
- Ensure you ran the script as Administrator
- Check PowerShell execution policy:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- Review script output for specific errors

## Keyboard Shortcuts

The GUI supports standard keyboard shortcuts:

- **Ctrl+Q**: Quit application (may vary by OS)
- **Tab**: Navigate between controls
- **Enter**: Activate focused button
- **Space**: Toggle checkboxes

## Comparison with CLI

The GUI provides all functionality of the command-line interface:

| Feature | CLI | GUI |
|---------|-----|-----|
| Standard/Strict Mode | ✅ | ✅ |
| JSON/HTML Reports | ✅ | ✅ |
| Compare Scans | ✅ | ✅ |
| Remediation Scripts | ✅ | ✅ |
| Real-time Progress | ❌ | ✅ |
| Visual Results | ❌ | ✅ |
| Easy Configuration | ❌ | ✅ |
| Recommendations View | ❌ | ✅ |

### When to Use CLI

Use the command-line interface when:
- Automating scans with scripts
- Running on servers without GUI
- Integrating with CI/CD pipelines
- Remote execution via SSH

### When to Use GUI

Use the graphical interface when:
- Running interactive scans
- Need visual feedback and progress
- Prefer point-and-click over commands
- Want to review results immediately
- Learning the tool for the first time

## Technical Details

### Architecture

The GUI is built using:
- **PySide6**: Qt 6 bindings for Python
- **Threading**: Scans run in background thread to keep UI responsive
- **Signal/Slots**: Qt's event system for communication between threads
- **Scanner Runner**: Reuses the existing `scanner.runner.run_scan()` function

### Code Structure

```
scanner/
├── gui.py              # GUI implementation (main window)
├── runner.py           # Scan execution logic (shared with CLI)
├── main.py             # CLI interface
└── ...

run_gui.py              # GUI launcher script
```

### Integration with Existing Code

The GUI maintains 100% compatibility with existing scanner code:
- Uses the same `run_scan()` function
- Generates identical reports to CLI
- Supports all scanner features
- No changes to core scanning logic

## Advanced Usage

### Custom Styling

The GUI uses Qt stylesheets. You can customize appearance by modifying the `apply_styles()` method in `scanner/gui.py`.

### Embedding in Applications

The GUI can be embedded in other applications:

```python
from PySide6.QtWidgets import QApplication
from scanner.gui import CyberEssentialsGUI

app = QApplication([])
window = CyberEssentialsGUI()
window.show()
app.exec()
```

### Programmatic Control

You can control the GUI programmatically:

```python
window = CyberEssentialsGUI()

# Set configuration
window.mode_combo.setCurrentIndex(1)  # Strict mode
window.compare_checkbox.setChecked(True)

# Start scan
window.start_scan()
```

## Support

For issues, questions, or feature requests:
1. Check this guide first
2. Review the main README.md
3. Check REPORT_GUIDE.md for understanding results
4. Open an issue on the GitHub repository

## Version

GUI Version: 1.0.0  
Compatible with Scanner Version: 0.2.0  
Cyber Essentials Standard: v3.2 (2025)

---

**Note**: The GUI requires a graphical environment. For headless servers, use the CLI interface (`python -m scanner.main`).
