from __future__ import annotations
import platform
from scanner.models import ControlResult

def run(osw, mac, lin, strict_mode=False) -> ControlResult:
    """
    Remote Work & MDM Security (NEW for Cyber Essentials 2025)
    - VPN configuration for remote work
    - MDM enrollment and remote wipe capability
    CONDITIONAL: Only enforced in strict mode (corporate/managed devices)
    """
    system = platform.system()
    findings, recs, details = [], [], {}
    status = "unknown"; score = 0.7

    if system == "Windows":
        # Check MDM enrollment (CONDITIONAL - only for managed devices)
        mdm = osw.mdm_enrollment(); details["mdm"] = mdm
        if not mdm.get("mdm_enrolled"):
            if strict_mode:
                findings.append("Device not enrolled in MDM (Intune/other)")
                recs.append("Enroll device in MDM for remote wipe capability (REQUIRED for managed devices)")
                status = "warn"
        else:
            score = 1.0
        
        if not mdm.get("azure_ad_joined"):
            if strict_mode:
                findings.append("Device not joined to Azure AD")
                recs.append("Join device to Azure AD for centralized management (REQUIRED for corporate devices)")
        
        # Check VPN configuration (CONDITIONAL - only if device accesses corporate resources)
        vpn = osw.vpn_status(); details["vpn"] = vpn
        if not vpn.get("vpn_configured"):
            if strict_mode:
                findings.append("No VPN configured for remote work")
                recs.append("Configure VPN for secure remote access (REQUIRED for remote corporate access)")
                status = "warn"
        
        if not findings or not strict_mode:
            status, score = "pass", 1.0

    elif system == "Darwin":
        # Check MDM enrollment (CONDITIONAL)
        mdm = mac.mdm_enrollment(); details["mdm"] = mdm
        if not mdm.get("mdm_enrolled"):
            if strict_mode:
                findings.append("Device not enrolled in MDM (Jamf/other)")
                recs.append("Enroll device in MDM for remote wipe capability (REQUIRED for managed devices)")
                status = "warn"
        else:
            score = 1.0
        
        # Check VPN configuration (CONDITIONAL)
        vpn = mac.vpn_status(); details["vpn"] = vpn
        if not vpn.get("vpn_configured"):
            if strict_mode:
                findings.append("No VPN configured for remote work")
                recs.append("Configure VPN for secure remote access (REQUIRED for remote corporate access)")
                status = "warn"
        
        if not findings or not strict_mode:
            status, score = "pass", 1.0

    else:
        # Check for MDM/fleet management tools (CONDITIONAL)
        mdm = lin.mdm_enrollment(); details["mdm"] = mdm
        if not mdm.get("enrolled"):
            if strict_mode:
                findings.append("No MDM/fleet management detected")
                recs.append("Deploy fleet management tools (Landscape, Fleet, etc.) for managed devices")
                status = "warn"
        else:
            score = 1.0
        
        # Check VPN configuration (CONDITIONAL)
        vpn = lin.vpn_status(); details["vpn"] = vpn
        if not vpn.get("vpn_configured"):
            if strict_mode:
                findings.append("No VPN configured for remote work")
                recs.append("Configure VPN (OpenVPN, WireGuard, etc.) for secure remote access")
                status = "warn"
        
        if not findings or not strict_mode:
            status, score = "pass", 1.0

    return ControlResult(
        name="remote_work_mdm",
        status=status,
        score=score,
        findings=findings,
        recommendations=recs,
        details=details
    )
