from __future__ import annotations
from scanner.utils import run_cmd

def firewall_enabled() -> dict:
    # Prefer PowerShell if available
    code, out, _ = run_cmd('powershell -NoProfile -Command "Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json"')
    if code == 0 and out:
        try:
            import json
            profiles = json.loads(out)
            if isinstance(profiles, dict):
                profiles = [profiles]
            enabled = all(p.get("Enabled") for p in profiles)
            return {"enabled": enabled, "profiles": profiles}
        except Exception:
            pass
    # Fallback: netsh parsing
    code, out, _ = run_cmd('netsh advfirewall show allprofiles')
    enabled = "State ON" in out or "ON" in out.upper()
    return {"enabled": enabled, "raw": out}

def guest_account_enabled() -> dict:
    # Guest account status via Net User Guest
    code, out, _ = run_cmd('net user guest')
    if code == 0 and out:
        enabled = "Account active               Yes" in out or "Active               Yes" in out
        return {"enabled": enabled, "raw": out}
    return {"enabled": None, "raw": out}

def rdp_enabled() -> dict:
    # Query RDP status via registry
    cmd = r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections'
    code, out, _ = run_cmd(cmd)
    if code == 0 and "0x0" in out:
        return {"enabled": True}
    if code == 0 and "0x1" in out:
        return {"enabled": False}
    return {"enabled": None}

def smb1_enabled() -> dict:
    # SMBv1 client setting
    cmd = r'reg query "HKLM\SYSTEM\CurrentControlSet\Services\LanmanWorkstation\Parameters" /v SMB1'
    code, out, _ = run_cmd(cmd)
    if code == 0 and "0x0" in out:
        return {"enabled": False}
    if code == 0 and "0x1" in out:
        return {"enabled": True}
    # Server side
    cmd2 = r'reg query "HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters" /v SMB1'
    code2, out2, _ = run_cmd(cmd2)
    if code2 == 0 and "0x0" in out2:
        return {"enabled": False}
    if code2 == 0 and "0x1" in out2:
        return {"enabled": True}
    return {"enabled": None}

def local_admins() -> dict:
    code, out, _ = run_cmd('net localgroup administrators')
    members = []
    if code == 0 and out:
        lines = out.splitlines()
        start = False
        for line in lines:
            if "----" in line:
                start = True
                continue
            if start:
                if line.strip() and "command completed" not in line.lower():
                    members.append(line.strip())
    return {"members": members, "count": len(members)}

def password_policy() -> dict:
    # net accounts provides a subset
    code, out, _ = run_cmd('net accounts')
    policy = {"raw": out}
    if code == 0 and out:
        import re
        def grab(pattern, key):
            m = re.search(pattern, out, flags=re.IGNORECASE)
            if m:
                policy[key] = m.group(1).strip()
        grab(r"Minimum password length\s+(\d+)", "min_length")
        grab(r"Maximum password age\s+(.+)", "max_age")
        grab(r"Minimum password age\s+(.+)", "min_age")
        grab(r"Lockout threshold\s+(\d+)", "lockout_threshold")
    # Complexity via registry
    code2, out2, _ = run_cmd(r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Lsa" /v "PasswordComplexity"')
    if code2 == 0:
        policy["complexity"] = "enabled" if "0x1" in out2 else "disabled" if "0x0" in out2 else "unknown"
    return policy

def av_status() -> dict:
    # WMI SecurityCenter2: requires PowerShell and permissions
    ps = 'powershell -NoProfile -Command "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName,productState | ConvertTo-Json"'
    code, out, err = run_cmd(ps)
    if code == 0 and out:
        try:
            import json
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            # productState is a bitmask; high-level naive mapping:
            # Real-time on often encoded by certain bits; here we only echo raw state.
            return {"products": data}
        except Exception:
            pass
    return {"products": [], "note": "Unable to query SecurityCenter2"}

def latest_hotfix_days() -> dict:
    # Heuristic: Get-HotFix newest InstalledOn date
    ps = 'powershell -NoProfile -Command "(Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 1 | Select-Object InstalledOn) | ConvertTo-Json"'
    code, out, _ = run_cmd(ps)
    if code == 0 and out:
        try:
            import json, datetime
            data = json.loads(out)
            date_str = data.get("InstalledOn")
            if date_str:
                try:
                    installed = datetime.datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                except Exception:
                    installed = None
                if installed:
                    days = (datetime.datetime.utcnow().replace(tzinfo=installed.tzinfo) - installed).days
                    return {"latest_hotfix_days": days, "latest_installed_on": date_str}
        except Exception:
            pass
    return {"latest_hotfix_days": None}

def mfa_status() -> dict:
    """Check MFA/Windows Hello status"""
    results = {"windows_hello": None, "biometric": None, "pin": None}
    
    # Method 1: Check NGC (Next Generation Credentials) folder
    ps = 'powershell -NoProfile -Command "Test-Path \'$env:WINDIR\\ServiceProfiles\\LocalService\\AppData\\Local\\Microsoft\\Ngc\' -or (Test-Path \'$env:LOCALAPPDATA\\Microsoft\\Ngc\')"'
    code, out, _ = run_cmd(ps)
    ngc_exists = code == 0 and "True" in out
    
    # Method 2: Check Windows Hello for Business registry
    ps2_cmd = 'powershell -NoProfile -Command "Get-ItemProperty -Path \'HKLM:\\SOFTWARE\\Policies\\Microsoft\\PassportForWork\' -ErrorAction SilentlyContinue | ConvertTo-Json"'
    code2, out2, _ = run_cmd(ps2_cmd)
    hello_policy = False
    if code2 == 0 and out2 and out2.strip() not in ["", "null"]:
        try:
            import json
            data = json.loads(out2)
            if isinstance(data, dict) and data:
                hello_policy = True
        except Exception:
            pass
    
    # Method 3: Check credential provider for PIN
    code3, out3, _ = run_cmd('reg query "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Authentication\\Credential Providers\\{60b78e88-ead8-445c-9cfd-0b87f74ea6cd}" /v Disabled')
    pin_provider_enabled = code3 != 0 or "0x0" in out3
    
    # Method 4: Check user has NGC keys (actual PIN configured)
    ps4_cmd = 'powershell -NoProfile -Command "Get-ChildItem \'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Authentication\\Credential Providers\' -Recurse | Where-Object {$_.Name -like \'*NGC*\'} | Measure-Object | Select-Object -ExpandProperty Count"'
    code4, out4, _ = run_cmd(ps4_cmd)
    ngc_providers = code4 == 0 and out4.strip().isdigit() and int(out4.strip()) > 0
    
    # Determine if Windows Hello/PIN is actually configured
    results["windows_hello"] = "enabled" if (ngc_exists or hello_policy or ngc_providers) else "not_detected"
    results["pin"] = ngc_exists or pin_provider_enabled
    
    # Check for biometric devices
    ps5_cmd = 'powershell -NoProfile -Command "(Get-PnpDevice -Class Biometric -Status OK -ErrorAction SilentlyContinue | Measure-Object).Count"'
    code5, out5, _ = run_cmd(ps5_cmd)
    if code5 == 0 and out5.strip().isdigit():
        results["biometric"] = int(out5.strip()) > 0
    
    return results

def bitlocker_status() -> dict:
    """Check BitLocker encryption status"""
    ps = 'powershell -NoProfile -Command "Get-BitLockerVolume | Select-Object MountPoint,VolumeStatus,EncryptionPercentage,ProtectionStatus | ConvertTo-Json"'
    code, out, _ = run_cmd(ps)
    if code == 0 and out:
        try:
            import json
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            
            volumes = []
            all_encrypted = True
            for vol in data:
                mount = vol.get("MountPoint", "")
                status = vol.get("VolumeStatus", "")
                encrypted = status in ["FullyEncrypted", "EncryptionInProgress"]
                volumes.append({
                    "mount": mount,
                    "status": status,
                    "encrypted": encrypted
                })
                if not encrypted:
                    all_encrypted = False
            
            return {"enabled": all_encrypted, "volumes": volumes}
        except Exception:
            pass
    return {"enabled": None, "volumes": []}

def screen_lock_policy() -> dict:
    """Check screen lock timeout settings"""
    results = {}
    
    # Check screen saver timeout (in seconds)
    code, out, _ = run_cmd(r'reg query "HKCU\Control Panel\Desktop" /v ScreenSaveTimeOut')
    if code == 0 and "ScreenSaveTimeOut" in out:
        import re
        match = re.search(r"ScreenSaveTimeOut\s+REG_SZ\s+(\d+)", out)
        if match:
            timeout_sec = int(match.group(1))
            results["screensaver_timeout_minutes"] = timeout_sec / 60
    
    # Check if screen saver is password protected
    code2, out2, _ = run_cmd(r'reg query "HKCU\Control Panel\Desktop" /v ScreenSaverIsSecure')
    if code2 == 0 and "ScreenSaverIsSecure" in out2:
        results["screensaver_password"] = "0x1" in out2
    
    # Check power settings for screen timeout
    ps = 'powershell -NoProfile -Command "powercfg /query SCHEME_CURRENT SUB_VIDEO VIDEOIDLE | Select-String \'Current AC Power Setting Index:\'"'
    code3, out3, _ = run_cmd(ps)
    if code3 == 0 and out3:
        import re
        match = re.search(r"0x([0-9a-fA-F]+)", out3)
        if match:
            timeout_sec = int(match.group(1), 16)
            results["screen_timeout_minutes"] = timeout_sec / 60
    
    return results

def mdm_enrollment() -> dict:
    """Check MDM enrollment status"""
    # Check Intune/MDM enrollment
    code, out, _ = run_cmd(r'reg query "HKLM\SOFTWARE\Microsoft\Enrollments" /s')
    enrolled = "Enrollments" in out and "UPN" in out
    
    # Check Azure AD join status
    ps = 'powershell -NoProfile -Command "dsregcmd /status | Select-String \'AzureAdJoined\'"'
    code2, out2, _ = run_cmd(ps)
    azure_joined = "YES" in out2.upper() if code2 == 0 else False
    
    return {
        "mdm_enrolled": enrolled,
        "azure_ad_joined": azure_joined,
        "raw": out[:500] if out else ""
    }

def os_support_status() -> dict:
    """Check if Windows version is supported"""
    import platform
    import datetime
    
    version = platform.version()
    
    # Get actual Windows version name (11 vs 10) using wmic
    code, out, _ = run_cmd('wmic os get Caption /value')
    os_name = "Windows 10"  # Default fallback
    if code == 0 and "Caption=" in out:
        for line in out.splitlines():
            if line.startswith("Caption="):
                caption = line.split("=", 1)[1].strip()
                if "Windows 11" in caption:
                    os_name = "Windows 11"
                elif "Windows 10" in caption:
                    os_name = "Windows 10"
                break
    
    # Windows support lifecycle (simplified)
    eol_dates = {
        "Windows 10": datetime.datetime(2025, 10, 14),
        "Windows 11": datetime.datetime(2031, 10, 10),
    }
    
    supported = None
    eol_date = None
    
    if os_name in eol_dates:
        eol_date = eol_dates[os_name].strftime("%Y-%m-%d")
        supported = datetime.datetime.now() < eol_dates[os_name]
    
    return {
        "os_version": os_name,
        "supported": supported,
        "eol_date": eol_date,
        "build": version
    }

def default_accounts_status() -> dict:
    """Check for default/common accounts beyond Guest"""
    accounts = []
    issues = []
    
    # Check Administrator account
    code, out, _ = run_cmd('net user Administrator')
    if code == 0 and out:
        enabled = "Account active               Yes" in out or "Active               Yes" in out
        if enabled:
            issues.append("Built-in Administrator account is enabled")
        accounts.append({"name": "Administrator", "enabled": enabled})
    
    # Check DefaultAccount
    code2, out2, _ = run_cmd('net user DefaultAccount')
    if code2 == 0 and out2:
        enabled2 = "Account active               Yes" in out2 or "Active               Yes" in out2
        if enabled2:
            issues.append("DefaultAccount is enabled")
        accounts.append({"name": "DefaultAccount", "enabled": enabled2})
    
    return {"accounts": accounts, "issues": issues}

def cloud_mfa_status() -> dict:
    """Check Azure AD MFA status (if Azure AD joined)"""
    # This requires Azure AD connection - limited local check
    ps = 'powershell -NoProfile -Command "dsregcmd /status | Select-String \'Ngc\'"'
    code, out, _ = run_cmd(ps)
    
    ngc_enabled = "YES" in out.upper() if code == 0 else None
    
    return {
        "windows_hello_cloud": ngc_enabled,
        "note": "Full cloud MFA status requires Azure AD PowerShell module"
    }

def vpn_status() -> dict:
    """Check VPN configuration"""
    ps = 'powershell -NoProfile -Command "Get-VpnConnection | Select-Object Name,ConnectionStatus | ConvertTo-Json"'
    code, out, _ = run_cmd(ps)
    
    vpn_configured = False
    connections = []
    
    if code == 0 and out:
        try:
            import json
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            vpn_configured = len(data) > 0
            connections = [{"name": c.get("Name"), "status": c.get("ConnectionStatus")} for c in data]
        except Exception:
            pass
    
    return {
        "vpn_configured": vpn_configured,
        "connections": connections
    }

def application_control_status() -> dict:
    """Check AppLocker and WDAC status"""
    results = {"applocker": None, "wdac": None}
    
    # Check AppLocker service
    code, out, _ = run_cmd('sc query appidsvc')
    if code == 0:
        results["applocker"] = "RUNNING" in out
    
    # Check for WDAC policies
    ps = 'powershell -NoProfile -Command "Get-CIPolicy -ErrorAction SilentlyContinue | ConvertTo-Json"'
    code2, out2, _ = run_cmd(ps)
    if code2 == 0 and out2 and out2.strip() not in ["", "null"]:
        results["wdac"] = True
    else:
        results["wdac"] = False
    
    return results