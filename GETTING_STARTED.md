# 🎯 Cyber Essentials 2025 Scanner - Complete Package

## What You Have Now

Your Cyber Essentials System Scanner has been **fully upgraded to v0.2.0** with complete 2025 compliance checking.

---

## 📦 Package Contents

### Core Scanner Files
- ✅ `scanner/main.py` - Main scanner (v0.2.0)
- ✅ `scanner/models.py` - Data models
- ✅ `scanner/utils.py` - Utility functions
- ✅ `scanner/os/windows.py` - Windows checks (9 new functions)
- ✅ `scanner/os/macos.py` - macOS checks (9 new functions)
- ✅ `scanner/os/linux.py` - Linux checks (9 new functions)

### Check Modules (6 total)
- ✅ `scanner/checks/firewall.py` - Firewall verification
- ✅ `scanner/checks/secure_configuration.py` - Enhanced with screen lock & default accounts
- ✅ `scanner/checks/access_control.py` - Enhanced with MANDATORY MFA
- ✅ `scanner/checks/malware_protection.py` - Enhanced with encryption & app control
- ✅ `scanner/checks/patch_management.py` - Updated to 14-day rule
- ✅ `scanner/checks/remote_work_mdm.py` - **NEW** for 2025

### Documentation
- ✅ `README.md` - Updated with 2025 features
- ✅ `CHANGES_2025.md` - Detailed change log
- ✅ `REPORT_GUIDE.md` - How to interpret your results
- ✅ `report_schema/schema.json` - Updated JSON schema

### Tools & Reports
- ✅ `test_report.json` - Your current scan results

---

## 🚀 Quick Start Guide

### 1. Run Basic Scan (Personal Device)
```powershell
# Standard mode - for personal/BYOD devices
python -m scanner.main
# Output: reports/report.json
```

### 2. Run Corporate Scan (Managed Device)
```powershell
# Strict mode - for corporate/managed devices
python -m scanner.main --strict-mode --output reports/corporate_scan.json
```

### 3. Run Without Admin Prompt (Testing)
```powershell
# Skip UAC elevation prompt
python -m scanner.main --no-admin --output reports/test_scan.json
```

### 4. Review Results
Open `REPORT_GUIDE.md` to understand your results and required actions.

**Note:** The scanner will automatically prompt for Administrator privileges on Windows when needed for full detection capabilities (BitLocker, hotfix history, etc.).

---

## 📊 What's Checked (Cyber Essentials 2025)

### 1. Firewalls ✅
- Windows Defender Firewall (all profiles)
- macOS Application Firewall
- Linux firewall (ufw/firewalld/iptables)

### 2. Secure Configuration ✅
- Guest account disabled
- Default accounts (Administrator, DefaultAccount)
- RDP disabled or secured
- SMBv1 disabled
- **Screen lock timeout ≤ 15 minutes** (NEW)
- **Default password changes** (NEW)

### 3. Access Control ✅
- Limited admin users (≤3 recommended)
- Password complexity enabled
- **MANDATORY MFA/Windows Hello** (NEW)
- **Cloud MFA for Microsoft 365/Azure AD** (NEW)
- Touch ID/biometric authentication (macOS)

### 4. Malware Protection ✅
- Antivirus installed and active
- Real-time protection enabled
- **MANDATORY device encryption** (NEW)
  - BitLocker (Windows)
  - FileVault (macOS)
  - LUKS (Linux)
- **Application whitelisting** (NEW)
  - AppLocker/WDAC (Windows)
  - Gatekeeper (macOS)
  - AppArmor/SELinux (Linux)

### 5. Patch Management ✅
- **14-day rule for CVSS 7+ vulnerabilities** (NEW - was 30 days)
- **Supported OS version only** (NEW)
- Pending updates detection
- Auto-update enabled

### 6. Remote Work & MDM ✅ (NEW)
- **MDM enrollment** (Intune, Jamf, etc.)
- **Remote wipe capability**
- **VPN configuration** for remote access
- Azure AD/cloud join status

---

## 🎯 Example Scan Results

### Standard Mode (Personal Device)
Typical results for a well-maintained personal device:

| Control Area | Status | Score | Notes |
|--------------|--------|-------|-------|
| Firewalls | ✅ PASS | 1.0 | All profiles enabled |
| Secure Configuration | ✅ PASS | 1.0 | Screen lock configured |
| Access Control | ✅ PASS | 1.0 | PIN/Windows Hello enabled |
| Malware Protection | ⚠️ WARN | 0.8 | AV active, BitLocker warning |
| Patch Management | ✅ PASS | 1.0 | Up to date |
| Remote Work & MDM | ⚠️ WARN | 0.8 | VPN/MDM warnings (OK) |

**Overall: WARN (0.88/1.0)** - Good for personal device!

### Strict Mode (Corporate Device)
Same device scanned with `--strict-mode`:

| Control Area | Status | Score | Notes |
|--------------|--------|-------|-------|
| Firewalls | ✅ PASS | 1.0 | All profiles enabled |
| Secure Configuration | ✅ PASS | 1.0 | Screen lock configured |
| Access Control | ✅ PASS | 1.0 | PIN/Windows Hello enabled |
| Malware Protection | ❌ FAIL | 0.6 | **BitLocker required** |
| Patch Management | ✅ PASS | 1.0 | Up to date |
| Remote Work & MDM | ❌ FAIL | 0.4 | **VPN/MDM required** |

**Overall: FAIL (0.72/1.0)** - Needs corporate compliance fixes

### Key Differences
- **Standard Mode:** BitLocker/VPN/MDM are warnings (not failures)
- **Strict Mode:** BitLocker/VPN/MDM failures block certification
- Use Standard Mode unless you're certifying a corporate/managed device

---

## 📋 Action Plan

### This Week (CRITICAL)
- [ ] Enable Windows Hello PIN on all devices
- [ ] Plan Windows 11 upgrade (Win 10 is EOL)
- [ ] Apply security fixes based on scan results
- [ ] Re-run scanner as Administrator

### This Month (HIGH PRIORITY)
- [ ] Complete Windows 11 upgrade
- [ ] Enable MFA for all cloud services (Microsoft 365, etc.)
- [ ] Enroll devices in MDM (Intune)
- [ ] Configure VPN for remote workers

### This Quarter (RECOMMENDED)
- [ ] Enable BitLocker on all devices
- [ ] Configure AppLocker/application whitelisting
- [ ] Join devices to Azure AD
- [ ] Schedule monthly compliance scans

---

## 📖 Understanding Compliance Modes

### Standard Mode (Default)
**Use for:** Personal devices, BYOD, home users

```powershell
python -m scanner.main --output report.json
```

**What's checked:**
- ✅ Firewall, AV, patches (mandatory)
- ✅ Password policy, MFA (mandatory)
- ⚠️ BitLocker (warning if disabled)
- ⚠️ VPN, MDM (warning if missing)

**Result:** More lenient scoring for personal devices

### Strict Mode (`--strict-mode`)
**Use for:** Corporate devices, managed workstations, compliance-critical

```powershell
python -m scanner.main --strict-mode --output report_corporate.json
```

**What's checked:**
- ✅ Everything from Standard Mode
- ❌ BitLocker REQUIRED (fail if disabled)
- ❌ VPN REQUIRED (fail if missing)
- ❌ MDM REQUIRED (fail if not enrolled)

**Result:** Stricter scoring for corporate compliance

### When to Use Each Mode

| Your Device | Use Mode | Why |
|-------------|----------|-----|
| Personal laptop at home | Standard | BitLocker/VPN not expected |
| Work-from-home BYOD | Standard | Employee-owned device |
| Company-issued laptop | Strict | Corporate security required |
| Office workstation | Strict | Full management expected |
| Developer machine | Standard | Unless policy requires strict |

### 🔧 Scanner Commands

```powershell
# Personal device scan (default output: reports/report.json)
python -m scanner.main

# Corporate device scan with custom name
python -m scanner.main --strict-mode --output reports/corporate_scan.json

# Skip admin prompt (testing)
python -m scanner.main --no-admin --output reports/test_scan.json

# Output to console (no file)
python -m scanner.main --output -

# Custom location outside reports folder
python -m scanner.main --output my_custom_report.json
```

### Understanding Reports
See `REPORT_GUIDE.md` for:
- Compliance mode differences (Standard vs Strict)
- Status meanings (PASS/WARN/FAIL/UNKNOWN)
- How to interpret findings
- Specific remediation steps
- Priority recommendations
- Compliance score calculation

---

## 📈 Success Criteria

To achieve Cyber Essentials 2025 certification:

✅ **PASS Required:**
- All control areas must be PASS or WARN (no FAIL)
- Overall score ≥ 0.85 (85%)
- All MANDATORY items completed:
  - ✅ MFA for all users
  - ✅ Device encryption
  - ✅ Supported OS only (no EOL systems)
  - ✅ Patches within 14 days
  - ✅ MDM enrollment (mobile devices)

**Your Path to Compliance:**
1. Fix Access Control (0.3 → 1.0) = Enable MFA
2. Fix Patch Management (0.0 → 1.0) = Upgrade OS + apply patches
3. Improve Secure Config (0.6 → 1.0) = Fix screen lock
4. Improve Remote Work (0.7 → 1.0) = Add MDM + VPN

**Projected Score: 0.95/1.0 (95%)** ✅

---

## 🆘 Troubleshooting

### "Cannot determine BitLocker status"
**Solution:** 
- Windows will prompt for Administrator privileges automatically
- Or run: `python -m scanner.main` (allow UAC prompt)
- Manual: Right-click PowerShell → Run as Administrator

### "MFA not detected" but I have PIN set up
**Solution:** 
1. Verify in Settings → Accounts → Sign-in options
2. Allow admin elevation when scanner prompts
3. Check Windows Hello is configured (not just PIN option shown)
4. Re-run scanner: `python -m scanner.main`

### "Unsupported OS" for Windows 10
**Solution:** 
- Windows 10 EOL was October 14, 2025
- Upgrade to Windows 11 is **MANDATORY** for CE 2025
- Check hardware compatibility first

### Scanner runs but shows all "unknown" status
**Solution:** 
- Allow UAC elevation prompt when it appears
- Or use: `python -m scanner.main` (don't use --no-admin flag)
- Ensure you're running from correct directory

### "Device not enrolled in MDM" - Should I worry?
**Solution:**
- **Standard Mode:** This is just a warning, not a failure
- **Strict Mode:** This is mandatory for corporate devices
- Personal devices: MDM enrollment is optional
- Corporate devices: Contact IT for Intune/MDM enrollment

### "BitLocker not enabled" - Different results by mode
**Explanation:**
- **Standard Mode:** Shows as WARNING (recommended but not required)
- **Strict Mode:** Shows as FAILURE (mandatory for corporate)
- This is expected behavior, not a bug
- Use the appropriate mode for your device type

---

## 📚 Additional Resources

### Official Documentation
- [Cyber Essentials Requirements v3.2](https://www.ncsc.gov.uk/cyberessentials/overview)
- [IASME Certification Body](https://iasme.co.uk/)
- [NCSC Guidance](https://www.ncsc.gov.uk/)

### Windows Configuration
- [Windows Hello Setup](https://support.microsoft.com/windows/hello)
- [BitLocker Encryption](https://support.microsoft.com/bitlocker)
- [Windows 11 Upgrade](https://www.microsoft.com/windows/windows-11)
- [Azure AD Join](https://docs.microsoft.com/azure/active-directory)

### Internal Documentation
- `README.md` - Scanner overview and features
- `CHANGES_2025.md` - Detailed change log
- `REPORT_GUIDE.md` - Report interpretation guide

---

## ✅ Verification Checklist

### For Standard Mode (Personal/BYOD)
- [ ] Run: `python -m scanner.main --output report.json`
- [ ] Overall status is PASS or WARN (no FAIL)
- [ ] Firewall enabled on all profiles
- [ ] Antivirus active and updated
- [ ] MFA/Windows Hello/PIN enabled
- [ ] Supported OS (Windows 11, macOS 13+, etc.)
- [ ] Patches applied within last 14 days
- [ ] Screen lock timeout ≤ 15 minutes
- [ ] Default/guest accounts disabled
- [ ] Password policy (min length ≥8)

**Optional but recommended:**
- [ ] BitLocker/FileVault enabled
- [ ] VPN configured (if working remotely)

### For Strict Mode (Corporate/Managed)
- [ ] Run: `python -m scanner.main --strict-mode --output report.json`
- [ ] All Standard Mode items above
- [ ] **BitLocker/FileVault REQUIRED** (mandatory)
- [ ] **MDM enrollment REQUIRED** (Intune/Jamf)
- [ ] **VPN configuration REQUIRED**
- [ ] **Azure AD join REQUIRED** (managed devices)
- [ ] Application control enabled (AppLocker/Gatekeeper)
- [ ] Overall status is PASS (no FAIL or WARN)

---

## 🎉 You're Ready!

You now have a **complete Cyber Essentials 2025 compliance toolkit**:

✅ Automated scanning for all CE 2025 requirements  
✅ Detailed reports with specific findings  
✅ Actionable recommendations  
✅ Comprehensive documentation  

**Next Step:** Run the scanner and follow the recommendations to fix issues!

---

**Questions or Issues?**
Review `REPORT_GUIDE.md` for detailed explanations and remediation steps.

**Scanner Version:** 0.2.0  
**Compliance Standard:** UK Cyber Essentials v3.2 (2025)  
**Last Updated:** November 14, 2025
