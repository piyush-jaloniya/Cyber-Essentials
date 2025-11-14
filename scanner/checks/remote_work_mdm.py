from __future__ import annotations
import platform
from scanner.models import ControlResult

def run(osw, mac, lin) -> ControlResult:
    """
    Remote Work & MDM Security (NEW for Cyber Essentials 2025)
    - VPN configuration for remote work
    - MDM enrollment and remote wipe capability
    """
    system = platform.system()
    findings, recs, details = [], [], {}
    status = "unknown"; score = 0.7

    if system == "Windows":
        # Check MDM enrollment
        mdm = osw.mdm_enrollment(); details["mdm"] = mdm
        if not mdm.get("mdm_enrolled"):
            findings.append("Device not enrolled in MDM (Intune/other)")
            recs.append("Enroll device in MDM for remote wipe capability (REQUIRED for CE 2025)")
            status = "warn"
        else:
            score = 1.0
        
        if not mdm.get("azure_ad_joined"):
            findings.append("Device not joined to Azure AD")
            recs.append("Join device to Azure AD for centralized management")
        
        # Check VPN configuration
        vpn = osw.vpn_status(); details["vpn"] = vpn
        if not vpn.get("vpn_configured"):
            findings.append("No VPN configured for remote work")
            recs.append("Configure VPN for secure remote access (REQUIRED for CE 2025)")
            status = "warn"
        
        if not findings:
            status, score = "pass", 1.0

    elif system == "Darwin":
        # Check MDM enrollment
        mdm = mac.mdm_enrollment(); details["mdm"] = mdm
        if not mdm.get("mdm_enrolled"):
            findings.append("Device not enrolled in MDM (Jamf/other)")
            recs.append("Enroll device in MDM for remote wipe capability (REQUIRED for CE 2025)")
            status = "warn"
        else:
            score = 1.0
        
        # Check VPN configuration
        vpn = mac.vpn_status(); details["vpn"] = vpn
        if not vpn.get("vpn_configured"):
            findings.append("No VPN configured for remote work")
            recs.append("Configure VPN for secure remote access")
            status = "warn"
        
        if not findings:
            status, score = "pass", 1.0

    else:
        # Check for MDM/fleet management tools
        mdm = lin.mdm_enrollment(); details["mdm"] = mdm
        if not mdm.get("enrolled"):
            findings.append("No MDM/fleet management detected")
            recs.append("Consider deploying fleet management tools (Landscape, Fleet, etc.)")
            status = "warn"
        else:
            score = 1.0
        
        # Check VPN configuration
        vpn = lin.vpn_status(); details["vpn"] = vpn
        if not vpn.get("vpn_configured"):
            findings.append("No VPN configured for remote work")
            recs.append("Configure VPN (OpenVPN, WireGuard, etc.) for secure remote access")
            status = "warn"
        
        if not findings:
            status, score = "pass", 1.0

    return ControlResult(
        name="remote_work_mdm",
        status=status,
        score=score,
        findings=findings,
        recommendations=recs,
        details=details
    )
