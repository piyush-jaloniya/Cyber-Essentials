from __future__ import annotations
import argparse
import json
import datetime
import platform
import sys
import os
import ctypes

from scanner.models import Report, OSInfo, combine_statuses, average_score
from scanner.utils import get_os_info

# OS adapters
from scanner.os import windows as osw
from scanner.os import macos as osm
from scanner.os import linux as osl

# Checks
from scanner.checks import firewall, secure_configuration, access_control, malware_protection, patch_management, remote_work_mdm

SCANNER_VERSION = "0.2.0"  # Updated for Cyber Essentials 2025 compliance

def is_admin():
    """Check if running with administrator privileges"""
    try:
        if platform.system() == "Windows":
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception:
        return False

def request_admin_elevation():
    """Request administrator privileges on Windows"""
    if platform.system() == "Windows":
        try:
            # Get the current working directory
            cwd = os.getcwd()
            
            # Add --no-admin to prevent infinite loop
            params = ' '.join([f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
            params += ' --no-admin'
            
            # Create a wrapper command that keeps window open
            # Use -m scanner.main to run as module with correct path
            cmd = f'cd /d "{cwd}" & "{sys.executable}" -m scanner.main {params} & echo. & echo Scan complete! Press any key to close... & pause > nul'
            
            # Use ShellExecute to run as admin
            ctypes.windll.shell32.ShellExecuteW(
                None, 
                "runas", 
                "cmd.exe",
                f'/k "{cmd}"',
                None, 
                1
            )
            sys.exit(0)
        except Exception as e:
            print(f"Failed to elevate privileges: {e}", file=sys.stderr)
            return False
    return False

def main():
    parser = argparse.ArgumentParser(description="Cyber Essentials System Scanner")
    parser.add_argument("--output", "-o", type=str, default="reports/report.json", help="Output file path or - for stdout (default: reports/report.json)")
    parser.add_argument("--no-admin", action="store_true", help="Skip admin privilege check")
    parser.add_argument("--strict-mode", action="store_true", help="Enable strict mode (corporate/managed device compliance - checks all conditional requirements)")
    args = parser.parse_args()
    
    # Ensure reports directory exists
    if args.output != "-" and args.output != "":
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    # Check for admin privileges
    if not args.no_admin and not is_admin():
        print("⚠️  WARNING: Not running as Administrator")
        print("Some checks require elevated privileges for complete results:")
        print("  • BitLocker encryption status")
        print("  • Windows Update hotfix history")
        print("  • Full NGC/Windows Hello configuration")
        print()
        
        response = input("Run as Administrator now? [Y/n]: ").strip().lower()
        if response in ['', 'y', 'yes']:
            print("Requesting administrator privileges...")
            request_admin_elevation()
            return
        else:
            print("Continuing without administrator privileges (results may be incomplete)...")
            print()

    system, version = get_os_info()
    os_info = OSInfo(platform=system, version=version)

    # Select adapters
    w, m, l = osw, osm, osl

    results = []
    strict_mode = args.strict_mode
    for check in [firewall, secure_configuration, access_control, malware_protection, patch_management, remote_work_mdm]:
        try:
            res = check.run(w, m, l, strict_mode=strict_mode)
        except Exception as e:
            # Defensive: no single check should crash the run
            res = check.__name__, {
                "name": check.__name__,
                "status": "unknown",
                "score": 0.0,
                "findings": [f"Check error: {e}"],
                "recommendations": ["Re-run with elevated privileges or contact support"],
                "details": {}
            }
        results.append(res)

    overall_status = combine_statuses([r.status for r in results])  # type: ignore
    overall_score = average_score([r.score for r in results])  # type: ignore

    report = Report(
        scanner_version=SCANNER_VERSION,
        timestamp_utc=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        os=os_info,
        controls=results,  # type: ignore
        overall={"status": overall_status, "score": overall_score}
    )

    doc = {
        "scanner_version": report.scanner_version,
        "timestamp_utc": report.timestamp_utc,
        "compliance_mode": "strict" if strict_mode else "standard",
        "os": {"platform": report.os.platform, "version": report.os.version},
        "controls": [r.__dict__ for r in report.controls],
        "overall": report.overall
    }

    payload = json.dumps(doc, indent=2)
    if args.output == "-" or args.output == "":
        print(payload)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(payload)
        print(f"Wrote {args.output}")

if __name__ == "__main__":
    main()