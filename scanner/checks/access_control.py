from __future__ import annotations
import platform
from scanner.models import ControlResult

def run(osw, mac, lin) -> ControlResult:
    system = platform.system()
    findings, recs, details = [], [], {}
    status = "unknown"; score = 0.7

    if system == "Windows":
        admins = osw.local_admins(); details["local_admins"] = admins
        if admins.get("count", 0) > 3:
            findings.append(f"Large Administrators group: {admins['count']}")
            recs.append("Limit local administrators to least privilege")
            status = "warn"
        
        policy = osw.password_policy(); details["password_policy"] = policy
        complexity = policy.get("complexity")
        if complexity == "disabled":
            findings.append("Password complexity disabled")
            recs.append("Enable password complexity policy")
            status, score = "fail", 0.0
        
        # Check MFA/Windows Hello - CRITICAL for 2025 CE
        mfa = osw.mfa_status(); details["mfa"] = mfa
        if not mfa.get("biometric") and not mfa.get("pin"):
            findings.append("MFA/Windows Hello not detected (REQUIRED for Cyber Essentials 2025)")
            recs.append("Enable Windows Hello with PIN or biometric authentication (MANDATORY)")
            status = "fail" if status != "fail" else "fail"
            score = min(score, 0.3)
        
        # Cloud MFA
        cloud_mfa = osw.cloud_mfa_status(); details["cloud_mfa"] = cloud_mfa
        if cloud_mfa.get("windows_hello_cloud") is False:
            findings.append("Cloud MFA not enabled")
            recs.append("Enable MFA for all cloud services (Microsoft 365, Azure AD, etc.)")
        
        if not findings:
            status, score = "pass", 1.0

    elif system == "Darwin":
        admins = mac.admin_users(); details["admins"] = admins
        if admins.get("count", 0) > 2:
            findings.append(f"Many admin users: {admins['count']}")
            recs.append("Reduce admin group membership")
            status = "warn"
        
        # Check biometric authentication
        mfa = mac.mfa_biometric_status(); details["mfa"] = mfa
        if not mfa.get("touch_id_available"):
            findings.append("Touch ID/biometric authentication not available or configured")
            recs.append("Enable Touch ID or configure MFA for all users (MANDATORY for CE 2025)")
            status = "warn"
        
        if not findings:
            status, score = "pass", 1.0

    else:
        admins = lin.sudo_wheel_members(); details["sudo_wheel"] = admins
        if admins.get("count", 0) > 2:
            findings.append(f"Many sudo/wheel users: {admins['count']}")
            recs.append("Limit sudo access; prefer per-command sudoers rules")
            status = "warn"
        
        # Note: Linux MFA typically requires PAM modules
        findings.append("MFA status cannot be determined - verify PAM configuration manually")
        recs.append("Configure PAM MFA modules (Google Authenticator, Duo, etc.) for all users")
        
        if not findings:
            status, score = "pass", 1.0

    return ControlResult(
        name="access_control",
        status=status,
        score=score,
        findings=findings,
        recommendations=recs,
        details=details
    )