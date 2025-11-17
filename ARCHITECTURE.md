# Scanner Architecture

## Module Structure

This scanner is organized into **6 control modules** based on Cyber Essentials 2025:

```
scanner/
├── checks/
│   ├── firewall.py              # Control 1: Boundary protection
│   ├── secure_configuration.py   # Control 2: System hardening
│   ├── access_control.py         # Control 3: Authentication & permissions
│   ├── malware_protection.py     # Control 4: Anti-virus & encryption
│   ├── patch_management.py       # Control 5: Updates & OS support
│   └── remote_work_mdm.py        # Control 6: Remote work security (CE 2025)
├── os/
│   ├── windows.py                # Windows-specific detection functions
│   ├── macos.py                  # macOS-specific detection functions
│   └── linux.py                  # Linux-specific detection functions
├── models.py                     # Data structures (ControlResult, Report)
└── main.py                       # Entry point & orchestration

report_schema/                    # JSON schema for report validation
└── schema.json                   # Report structure definition

reports/                          # Default output directory for scan reports
├── .gitkeep                      # Keeps folder in git
└── report.json                   # Default output filename
```

## Why 6 Modules Instead of 5?

### Traditional Cyber Essentials (5 Controls)

The original CE framework has 5 control areas:
1. Firewalls
2. Secure Configuration
3. Access Control
4. Malware Protection
5. Patch Management

### Cyber Essentials 2025 Additions

The 2025 guidance added new requirements:
- ✅ Device encryption (BitLocker/FileVault) → Added to `malware_protection`
- ✅ MFA/2FA mandatory → Added to `access_control`
- ✅ OS EOL checking → Added to `patch_management`
- ✅ 14-day patch rule → Added to `patch_management`
- ⚠️ MDM enrollment → **Doesn't fit existing controls**
- ⚠️ VPN for remote work → **Doesn't fit existing controls**
- ⚠️ Remote wipe capability → **Doesn't fit existing controls**

### Design Decision

We created a **6th module** (`remote_work_mdm`) because:

1. **Separation of Concerns**
   - Access Control = User authentication (passwords, MFA, permissions)
   - Remote Work & MDM = Device management (remote wipe, VPN, enrollment)
   - Mixing these would make `access_control` bloated and confusing

2. **Conditional Enforcement**
   - MDM/VPN are only required for corporate/managed devices
   - Having a separate module makes it easy to enforce in strict mode only
   - Personal devices (standard mode) skip this module entirely

3. **Clearer Reporting**
   - Users see exactly what's being checked for remote work
   - JSON report has 6 distinct control objects
   - Each module has a focused scope

4. **Future-Proof**
   - Remote working requirements will likely expand
   - Easy to add new checks (BYOD policies, cloud security, etc.)
   - Doesn't pollute existing modules

### Compliance Mapping

```
CE Traditional          Scanner Modules         CE 2025 Requirements
─────────────────────   ───────────────────     ────────────────────
1. Firewalls       →    firewall.py             ✅ Same
2. Secure Config   →    secure_configuration.py ✅ + Screen lock, default accounts
3. Access Control  →    access_control.py       ✅ + MFA (mandatory)
4. Malware         →    malware_protection.py   ✅ + Encryption (mandatory)
5. Patch Mgmt      →    patch_management.py     ✅ + OS EOL, 14-day rule
(New for 2025)     →    remote_work_mdm.py      ⚠️ VPN, MDM (conditional)
```

## Mode-Based Enforcement

### Standard Mode (Default)
- Checks controls 1-5 (traditional CE)
- Remote Work & MDM module **not enforced**
- Suitable for personal/BYOD devices

### Strict Mode (`--strict-mode`)
- Checks all 6 controls
- Remote Work & MDM module **fully enforced**
- Suitable for corporate/managed devices

## Summary

The 6-module structure provides:
- ✅ **Clean architecture** - Single responsibility per module
- ✅ **Full CE 2025 compliance** - All requirements covered
- ✅ **Flexible enforcement** - Mode-based checking
- ✅ **Clear reporting** - Distinct control areas
- ✅ **Maintainability** - Easy to extend

The scanner remains **fully compliant** with Cyber Essentials 2025 guidance while providing better code organization and user experience.