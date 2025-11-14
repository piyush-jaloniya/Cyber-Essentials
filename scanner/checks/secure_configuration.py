from __future__ import annotations
import platform
from scanner.models import ControlResult

def run(osw, mac, lin) -> ControlResult:
    system = platform.system()
    findings, recs, details = [], [], {}
    status = "unknown"
    score = 0.6  # start at warn

    if system == "Windows":
        guest = osw.guest_account_enabled(); details["guest"] = guest
        if guest.get("enabled") is True:
            findings.append("Guest account is enabled")
            recs.append("Disable the Guest account")
            status = "warn"
        
        # Check default accounts
        default_accts = osw.default_accounts_status(); details["default_accounts"] = default_accts
        if default_accts.get("issues"):
            findings.extend(default_accts["issues"])
            recs.append("Disable built-in Administrator and DefaultAccount")
            status = "warn"
        
        rdp = osw.rdp_enabled(); details["rdp"] = rdp
        if rdp.get("enabled") is True:
            findings.append("RDP is enabled")
            recs.append("Disable RDP or restrict to VPN/IP allowlist with MFA")
            status = "warn"
        
        smb1 = osw.smb1_enabled(); details["smb1"] = smb1
        if smb1.get("enabled") is True:
            findings.append("SMBv1 is enabled")
            recs.append("Disable SMBv1 immediately (critical vulnerability)")
            status = "fail"; score = 0.0
        
        # Check screen lock
        screen_lock = osw.screen_lock_policy(); details["screen_lock"] = screen_lock
        timeout = screen_lock.get("screensaver_timeout_minutes", 999)
        if timeout > 15:
            findings.append(f"Screen lock timeout too long ({timeout} minutes)")
            recs.append("Set screen lock timeout to 15 minutes or less")
            status = "warn" if status != "fail" else "fail"
        
        if not findings:
            status, score = "pass", 1.0

    elif system == "Darwin":
        guest = mac.guest_account_enabled(); details["guest"] = guest
        if guest.get("enabled") is True:
            findings.append("Guest login enabled")
            recs.append("Disable Guest login")
        
        rl = mac.remote_login_enabled(); details["remote_login"] = rl
        if rl.get("enabled") is True:
            findings.append("Remote Login (SSH) enabled")
            recs.append("Disable Remote Login unless required; restrict via firewall")
        
        # Check screen lock
        screen_lock = mac.screen_lock_settings(); details["screen_lock"] = screen_lock
        if not screen_lock.get("ask_for_password"):
            findings.append("Screen saver does not require password")
            recs.append("Enable password requirement for screen saver")
        
        if not findings and all(v.get("enabled") is False for v in [guest, rl] if v.get("enabled") is not None):
            status, score = "pass", 1.0
        else:
            status = "warn" if findings else "unknown"

    else:
        ssh = lin.ssh_remote_login(); details["ssh"] = ssh
        if ssh.get("ssh_listening"):
            findings.append("SSH is listening")
            recs.append("Restrict SSH to trusted networks; disable password auth and root login")
        
        # Check default accounts
        default_accts = lin.default_accounts_status(); details["default_accounts"] = default_accts
        if default_accts.get("issues"):
            findings.extend(default_accts["issues"])
            recs.append("Disable root SSH login and remove accounts with empty passwords")
        
        pw = lin.password_policy_markers(); details["password_policy"] = pw
        if not pw.get("pwquality_present"):
            findings.append("PAM password quality module not detected")
            recs.append("Enable pam_pwquality (or cracklib) and enforce minimum length/complexity")
        
        # Check screen lock
        screen_lock = lin.screen_lock_settings(); details["screen_lock"] = screen_lock
        if not screen_lock.get("lock_enabled"):
            findings.append("Screen lock not enabled")
            recs.append("Enable automatic screen lock")
        
        if not findings:
            status, score = "pass", 1.0
        else:
            status = "warn"

    return ControlResult(
        name="secure_configuration",
        status=status,
        score=score,
        findings=findings,
        recommendations=recs,
        details=details
    )