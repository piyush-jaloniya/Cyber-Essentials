from __future__ import annotations
from scanner.utils import run_cmd

def app_firewall() -> dict:
    code, out, _ = run_cmd('/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate')
    if code == 0:
        enabled = "enabled" in out.lower()
        return {"enabled": enabled, "raw": out}
    return {"enabled": None, "raw": out}

def guest_account_enabled() -> dict:
    code, out, _ = run_cmd('defaults read /Library/Preferences/com.apple.loginwindow GuestEnabled')
    if code == 0:
        enabled = out.strip() == "1" or out.strip().lower() == "true"
        return {"enabled": enabled}
    return {"enabled": None}

def remote_login_enabled() -> dict:
    code, out, _ = run_cmd('systemsetup -getremotelogin 2>/dev/null')
    if code == 0:
        enabled = "On" in out
        return {"enabled": enabled, "raw": out}
    # Fallback: check ssh daemon
    code2, out2, _ = run_cmd('systemctl is-active ssh || launchctl list | grep sshd')
    if code2 == 0 and out2:
        return {"enabled": True}
    return {"enabled": None}

def admin_users() -> dict:
    code, out, _ = run_cmd("dscl . -read /Groups/admin GroupMembership")
    members = []
    if code == 0 and out:
        parts = out.split(":")
        if len(parts) > 1:
            members = [m.strip() for m in parts[1].split() if m.strip()]
    return {"members": members, "count": len(members)}

def gatekeeper_status() -> dict:
    code, out, _ = run_cmd("spctl --status")
    if code == 0:
        enabled = "assessments enabled" in out.lower()
        return {"enabled": enabled, "raw": out}
    return {"enabled": None}

def pending_updates() -> dict:
    code, out, _ = run_cmd("softwareupdate -l 2>&1")
    if code == 0 or "Software Update found the following" in out or "No new software available" in out:
        pending = "No new software available" not in out
        return {"pending": pending, "raw": out}
    return {"pending": None}

def xprotect_history() -> dict:
    code, out, _ = run_cmd("softwareupdate --history | grep -i xprotect | tail -n 1")
    if out:
        return {"last_xprotect_event": out}
    return {"last_xprotect_event": None}

def filevault_status() -> dict:
    """Check FileVault encryption status"""
    code, out, _ = run_cmd("fdesetup status")
    if code == 0:
        enabled = "FileVault is On" in out
        return {"enabled": enabled, "raw": out}
    return {"enabled": None}

def screen_lock_settings() -> dict:
    """Check screen lock timeout and requirements"""
    results = {}
    
    # Check screen saver timeout
    code, out, _ = run_cmd("defaults read com.apple.screensaver idleTime 2>/dev/null")
    if code == 0 and out.strip():
        try:
            results["idle_time_seconds"] = int(out.strip())
        except ValueError:
            pass
    
    # Check if password is required after screen saver
    code2, out2, _ = run_cmd("defaults read com.apple.screensaver askForPassword 2>/dev/null")
    if code2 == 0:
        results["ask_for_password"] = out2.strip() == "1"
    
    # Check delay before password prompt
    code3, out3, _ = run_cmd("defaults read com.apple.screensaver askForPasswordDelay 2>/dev/null")
    if code3 == 0 and out3.strip():
        try:
            results["password_delay_seconds"] = int(out3.strip())
        except ValueError:
            pass
    
    return results

def mdm_enrollment() -> dict:
    """Check MDM enrollment status"""
    code, out, _ = run_cmd("profiles status -type enrollment 2>/dev/null")
    enrolled = "Enrolled via DEP: Yes" in out or "MDM enrollment: Yes" in out
    
    return {"mdm_enrolled": enrolled, "raw": out[:500] if out else ""}

def os_support_status() -> dict:
    """Check macOS version support status"""
    import platform
    import datetime
    
    version = platform.mac_ver()[0]
    major_version = int(version.split('.')[0]) if version else 0
    
    # macOS support lifecycle (simplified - typically 3 years of security updates)
    current_year = datetime.datetime.now().year
    eol_year = {
        15: 2027,  # Sequoia
        14: 2026,  # Sonoma
        13: 2025,  # Ventura
        12: 2024,  # Monterey
    }
    
    supported = None
    eol_date = None
    
    if major_version in eol_year:
        eol_date = f"{eol_year[major_version]}-09-01"
        supported = current_year < eol_year[major_version]
    
    return {
        "os_version": f"macOS {version}",
        "supported": supported,
        "eol_date": eol_date
    }

def mfa_biometric_status() -> dict:
    """Check Touch ID and biometric authentication"""
    # Check if Touch ID is available
    code, out, _ = run_cmd("bioutil -r 2>/dev/null")
    touch_id_available = code == 0 and "Touch ID" in out
    
    return {
        "touch_id_available": touch_id_available,
        "note": "Cloud MFA requires checking Apple Business Manager or iCloud settings"
    }

def default_accounts_status() -> dict:
    """Check for default/system accounts"""
    code, out, _ = run_cmd("dscl . list /Users | grep -v '^_'")
    users = out.strip().split('\n') if code == 0 and out else []
    
    # Filter out common system accounts
    non_system = [u for u in users if u and not u.startswith('_')]
    
    return {
        "user_accounts": non_system,
        "count": len(non_system)
    }

def vpn_status() -> dict:
    """Check VPN configuration"""
    code, out, _ = run_cmd("scutil --nc list")
    vpn_configured = code == 0 and out and len(out.strip()) > 0
    
    return {
        "vpn_configured": vpn_configured,
        "raw": out[:500] if out else ""
    }

def application_control_status() -> dict:
    """Check Gatekeeper and other app security features"""
    results = {}
    
    # Gatekeeper
    code, out, _ = run_cmd("spctl --status")
    results["gatekeeper"] = "enabled" if "assessments enabled" in out.lower() else "disabled"
    
    # Check for third-party app control
    code2, out2, _ = run_cmd("system_profiler SPApplicationsDataType | grep -i 'santa\\|jamf protect' | head -n 1")
    results["third_party_control"] = bool(out2.strip())
    
    return results