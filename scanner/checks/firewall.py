from __future__ import annotations
import platform
from scanner.models import ControlResult

def run(osw, mac, lin) -> ControlResult:
    system = platform.system()
    findings, recs, details = [], [], {}
    status = "unknown"
    score = 0.0

    if system == "Windows":
        d = osw.firewall_enabled()
        details.update(d)
        if d.get("enabled") is True:
            status, score = "pass", 1.0
        elif d.get("enabled") is False:
            status, score = "fail", 0.0
            recs.append("Enable Windows Defender Firewall for all profiles")
        else:
            recs.append("Run as Administrator to verify firewall profiles")
    elif system == "Darwin":
        d = mac.app_firewall()
        details.update(d)
        if d.get("enabled") is True:
            status, score = "pass", 1.0
        elif d.get("enabled") is False:
            status, score = "fail", 0.0
            recs.append("Enable macOS Application Firewall")
        else:
            recs.append("Grant permissions to read firewall status")
    else:
        d = lin.firewall_status()
        details.update(d)
        enabled = d.get("enabled")
        if enabled is True:
            status, score = "pass", 1.0
        elif enabled is False:
            status, score = "fail", 0.0
            recs.append("Enable and configure ufw/firewalld or nftables/iptables")
        else:
            status = "unknown"
            recs.append("Install and enable a host firewall (ufw/firewalld)")

    return ControlResult(
        name="firewalls",
        status=status,
        score=score,
        findings=findings,
        recommendations=recs,
        details=details
    )