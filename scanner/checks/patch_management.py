from __future__ import annotations
import platform
from scanner.models import ControlResult

def run(osw, mac, lin) -> ControlResult:
    system = platform.system()
    findings, recs, details = [], [], {}
    status = "unknown"; score = 0.7

    if system == "Windows":
        # Check OS support status (REQUIRED for CE 2025)
        os_support = osw.os_support_status(); details["os_support"] = os_support
        if os_support.get("supported") is False:
            findings.append(f"Unsupported OS: {os_support.get('os_version')} (EOL: {os_support.get('eol_date')})")
            recs.append("Upgrade to a supported Windows version immediately (MANDATORY)")
            status = "fail"; score = 0.0
        elif os_support.get("supported") is None:
            findings.append("Cannot determine OS support status")
            recs.append("Verify OS version is within vendor support lifecycle")
        
        # Check patch status - 14-DAY RULE for CE 2025
        hf = osw.latest_hotfix_days(); details["latest_hotfix"] = hf
        days = hf.get("latest_hotfix_days")
        if days is None:
            status = "unknown" if status != "fail" else "fail"
            recs.append("Run as Administrator to read hotfix history")
        elif days <= 14:
            status, score = "pass" if status != "fail" else "fail", 1.0 if status != "fail" else 0.0
        else:
            status = "fail"; score = 0.0
            findings.append(f"Latest hotfix older than 14 days ({days} days) - FAILS CE 2025 requirement")
            recs.append("Apply security updates within 14 days (MANDATORY for CVSS 7+ vulnerabilities)")
        
        if not findings:
            status, score = "pass", 1.0
            
    elif system == "Darwin":
        # Check OS support status
        os_support = mac.os_support_status(); details["os_support"] = os_support
        if os_support.get("supported") is False:
            findings.append(f"Unsupported OS: {os_support.get('os_version')} (EOL: {os_support.get('eol_date')})")
            recs.append("Upgrade to a supported macOS version (MANDATORY)")
            status = "fail"; score = 0.0
        
        pu = mac.pending_updates(); details["pending_updates"] = pu
        if pu.get("pending") is False:
            status, score = "pass" if status != "fail" else "fail", 1.0 if status != "fail" else 0.0
        elif pu.get("pending") is True:
            status = "fail"; score = 0.0
            findings.append("Pending macOS updates available - must apply within 14 days")
            recs.append("Apply available updates immediately (14-day rule for CE 2025)")
        else:
            status = "unknown" if status != "fail" else "fail"
            recs.append("Grant permissions or run with sudo to check updates")
            
    else:
        # Check OS support status
        os_support = lin.os_support_status(); details["os_support"] = os_support
        if os_support.get("supported") is False:
            findings.append(f"Unsupported OS: {os_support.get('os_version')}")
            recs.append("Upgrade to a supported Linux distribution (MANDATORY)")
            status = "fail"; score = 0.0
        
        pu = lin.pending_updates(); details["pending_updates"] = pu
        count = pu.get("pending_count")
        if count is None:
            status = "unknown" if status != "fail" else "fail"
            recs.append("Run with sudo to detect pending updates")
        elif count == 0:
            status, score = "pass" if status != "fail" else "fail", 1.0 if status != "fail" else 0.0
        else:
            status = "fail"; score = 0.0
            findings.append(f"{count} pending updates found - apply within 14 days for critical vulnerabilities")
            recs.append("Apply updates immediately and enable auto-updates (14-day rule for CE 2025)")

    return ControlResult(
        name="patch_management",
        status=status,
        score=score,
        findings=findings,
        recommendations=recs,
        details=details
    )