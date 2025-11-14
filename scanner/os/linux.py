from __future__ import annotations
from scanner.utils import run_cmd

def firewall_status() -> dict:
    # Try ufw
    code, out, _ = run_cmd("ufw status 2>/dev/null")
    if code == 0 and out:
        enabled = "Status: active" in out
        return {"enabled": enabled, "tool": "ufw", "raw": out}
    # Try firewalld
    code, out, _ = run_cmd("systemctl is-active firewalld")
    if code == 0 and "active" in out:
        return {"enabled": True, "tool": "firewalld"}
    # nftables/iptables presence (heuristic)
    code, out, _ = run_cmd("nft list ruleset 2>/dev/null | head -n 2")
    if out:
        return {"enabled": True, "tool": "nftables"}
    code, out, _ = run_cmd("iptables -S 2>/dev/null | wc -l")
    if code == 0 and out and out.strip().isdigit() and int(out.strip()) > 0:
        return {"enabled": True, "tool": "iptables"}
    return {"enabled": None}

def sudo_wheel_members() -> dict:
    # sudo or wheel
    code, out, _ = run_cmd("getent group sudo || getent group wheel")
    members = []
    if code == 0 and out:
        parts = out.split(":")
        if len(parts) >= 4:
            members = [m.strip() for m in parts[3].split(",") if m.strip()]
    return {"members": members, "count": len(members)}

def password_policy_markers() -> dict:
    # login.defs
    policy = {}
    code, out, _ = run_cmd("grep -E 'PASS_MIN_LEN|PASS_MAX_DAYS' /etc/login.defs 2>/dev/null")
    if out:
        for line in out.splitlines():
            kv = line.strip().split()
            if len(kv) >= 2:
                policy[kv[0]] = kv[1]
    # PAM quality
    code2, out2, _ = run_cmd("grep -E 'pam_pwquality|pam_cracklib' /etc/pam.d/* 2>/dev/null | head -n 1")
    policy["pwquality_present"] = bool(out2)
    return policy

def ssh_remote_login() -> dict:
    # Check PermitRootLogin and PasswordAuthentication basics
    code, out, _ = run_cmd("ss -tulpn | grep ':22 ' || ss -tulpn | grep 'ssh'")
    ssh_listening = (code == 0 and out != "")
    code2, out2, _ = run_cmd("grep -E '^(PermitRootLogin|PasswordAuthentication)' /etc/ssh/sshd_config 2>/dev/null")
    return {"ssh_listening": ssh_listening, "config": out2}

def clamav_status() -> dict:
    code, out, _ = run_cmd("clamscan --version 2>/dev/null")
    installed = (code == 0 and bool(out))
    code2, out2, _ = run_cmd("systemctl is-active clamav-daemon || systemctl is-active clamd || echo inactive")
    active = installed and ("active" in out2)
    return {"installed": installed, "active": active, "raw": out or ""}

def pending_updates() -> dict:
    # Try apt
    code, _, _ = run_cmd("which apt 2>/dev/null")
    if code == 0:
        code2, out2, _ = run_cmd("apt list --upgradeable 2>/dev/null | wc -l")
        if code2 == 0 and out2.strip().isdigit():
            count = int(out2.strip())
            return {"pending_count": max(0, count - 1), "manager": "apt"}  # header line
    # dnf/yum
    code, _, _ = run_cmd("which dnf 2>/dev/null")
    if code == 0:
        code2, out2, _ = run_cmd("dnf check-update -q | grep -v '^Last metadata expiration' | wc -l")
        if code2 == 0 and out2.strip().isdigit():
            return {"pending_count": int(out2.strip()), "manager": "dnf"}
    code, _, _ = run_cmd("which yum 2>/dev/null")
    if code == 0:
        code2, out2, _ = run_cmd("yum check-update -q | wc -l")
        if code2 == 0 and out2.strip().isdigit():
            return {"pending_count": int(out2.strip()), "manager": "yum"}
    # zypper
    code, _, _ = run_cmd("which zypper 2>/dev/null")
    if code == 0:
        code2, out2, _ = run_cmd("zypper lu -t patch | tail -n +3 | wc -l")
        if code2 == 0 and out2.strip().isdigit():
            return {"pending_count": int(out2.strip()), "manager": "zypper"}
    return {"pending_count": None}

def disk_encryption_status() -> dict:
    """Check LUKS encryption status"""
    code, out, _ = run_cmd("lsblk -o NAME,FSTYPE | grep crypto_LUKS")
    encrypted = code == 0 and bool(out)
    
    # Count encrypted volumes
    encrypted_volumes = len(out.strip().split('\n')) if encrypted and out else 0
    
    return {
        "encrypted": encrypted,
        "encrypted_volumes": encrypted_volumes,
        "raw": out[:500] if out else ""
    }

def screen_lock_settings() -> dict:
    """Check screen lock timeout settings"""
    results = {}
    
    # GNOME
    code, out, _ = run_cmd("gsettings get org.gnome.desktop.session idle-delay 2>/dev/null")
    if code == 0 and out.strip():
        try:
            # Output format: uint32 300
            timeout = out.strip().split()[-1]
            results["idle_timeout_seconds"] = int(timeout)
        except (ValueError, IndexError):
            pass
    
    # Check screen lock enabled
    code2, out2, _ = run_cmd("gsettings get org.gnome.desktop.screensaver lock-enabled 2>/dev/null")
    if code2 == 0:
        results["lock_enabled"] = "true" in out2.lower()
    
    return results

def mdm_enrollment() -> dict:
    """Check for MDM/fleet management tools"""
    tools_found = []
    
    # Check for common Linux MDM tools
    for tool in ["landscape-client", "fleet", "osquery", "puppet", "ansible"]:
        code, _, _ = run_cmd(f"which {tool} 2>/dev/null")
        if code == 0:
            tools_found.append(tool)
    
    return {
        "mdm_tools": tools_found,
        "enrolled": len(tools_found) > 0
    }

def os_support_status() -> dict:
    """Check Linux distribution support status"""
    import datetime
    
    # Try to get OS release info
    code, out, _ = run_cmd("cat /etc/os-release 2>/dev/null")
    
    os_name = "Unknown"
    version = "Unknown"
    supported = None
    
    if code == 0 and out:
        for line in out.splitlines():
            if line.startswith("NAME="):
                os_name = line.split("=", 1)[1].strip('"')
            elif line.startswith("VERSION_ID="):
                version = line.split("=", 1)[1].strip('"')
    
    # Simple support check for major distributions
    # This is a simplified version - real implementation would need comprehensive database
    current_year = datetime.datetime.now().year
    
    return {
        "os_version": f"{os_name} {version}",
        "supported": supported,
        "note": "Support status requires distribution-specific lifecycle database"
    }

def default_accounts_status() -> dict:
    """Check for common default accounts"""
    issues = []
    
    # Check if root login is enabled
    code, out, _ = run_cmd("grep '^PermitRootLogin yes' /etc/ssh/sshd_config 2>/dev/null")
    if code == 0 and out:
        issues.append("Root SSH login is permitted")
    
    # Check for accounts with empty passwords
    code2, out2, _ = run_cmd("awk -F: '($2 == \"\") {print $1}' /etc/shadow 2>/dev/null")
    if code2 == 0 and out2.strip():
        issues.append(f"Accounts with empty passwords: {out2.strip()}")
    
    return {"issues": issues}

def vpn_status() -> dict:
    """Check VPN configuration"""
    vpn_tools = []
    
    for tool in ["openvpn", "wireguard", "strongswan", "networkmanager-vpn"]:
        code, _, _ = run_cmd(f"which {tool} 2>/dev/null || systemctl list-units | grep {tool}")
        if code == 0:
            vpn_tools.append(tool)
    
    return {
        "vpn_configured": len(vpn_tools) > 0,
        "vpn_tools": vpn_tools
    }

def application_control_status() -> dict:
    """Check AppArmor, SELinux status"""
    results = {}
    
    # AppArmor
    code, out, _ = run_cmd("aa-status 2>/dev/null | head -n 1")
    if code == 0:
        results["apparmor"] = "loaded" if "profiles are loaded" in out else "not loaded"
    
    # SELinux
    code2, out2, _ = run_cmd("getenforce 2>/dev/null")
    if code2 == 0:
        results["selinux"] = out2.strip()
    
    return results