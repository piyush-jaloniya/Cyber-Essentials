from __future__ import annotations
import argparse
import json
import datetime
import platform
import sys
import os
import ctypes
import logging

from scanner.models import Report, OSInfo, combine_statuses, average_score
from scanner.utils import get_os_info
from scanner.report_generator import generate_html_report
from scanner.comparison import load_previous_scan, compare_reports, print_comparison, save_comparison_report
from scanner.remediation import generate_remediation_script

# OS adapters
from scanner.os import windows as osw
from scanner.os import macos as osm
from scanner.os import linux as osl

# Checks
from scanner.checks import firewall, secure_configuration, access_control, malware_protection, patch_management, remote_work_mdm

SCANNER_VERSION = "0.2.0"  # Updated for Cyber Essentials 2025 compliance

def load_config(config_path: str = "ce-config.json") -> dict:
    """Load configuration from JSON file if it exists"""
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
    return {}

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
    # Load config file first (can be overridden by CLI args)
    config = load_config()
    
    parser = argparse.ArgumentParser(description="Cyber Essentials System Scanner")
    parser.add_argument("--config", "-c", type=str, help="Path to configuration file (default: ce-config.json)")
    parser.add_argument("--output", "-o", type=str, help="Output file path or - for stdout")
    parser.add_argument("--format", "-f", type=str, choices=["json", "html", "both"], help="Output format: json, html, or both")
    parser.add_argument("--compare", action="store_true", help="Compare with previous scan results")
    parser.add_argument("--generate-fix", action="store_true", help="Generate remediation PowerShell script (Windows only)")
    parser.add_argument("--no-admin", action="store_true", help="Skip admin privilege check")
    parser.add_argument("--strict-mode", action="store_true", help="Enable strict mode (corporate/managed device compliance)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging for debugging")
    args = parser.parse_args()
    
    # Load custom config if specified
    if args.config:
        config = load_config(args.config)
    
    # Merge config with CLI args (CLI args take precedence)
    output_path = args.output if args.output else config.get("output", {}).get("path", "reports/report.json")
    output_format = args.format if args.format else config.get("output", {}).get("format", "json")
    strict_mode = args.strict_mode if args.strict_mode else config.get("compliance_mode", "standard") == "strict"
    skip_admin = args.no_admin if args.no_admin else config.get("skip_admin_check", False)
    
    # Configure logging
    log_level_str = config.get("logging", {}).get("level", "INFO")
    if args.verbose:
        log_level_str = "DEBUG"
    log_level = getattr(logging, log_level_str, logging.INFO)
    
    log_file = config.get("logging", {}).get("file")
    if log_file:
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S',
            filename=log_file,
            filemode='a'
        )
    else:
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Cyber Essentials Scanner v0.2.0")
    logger.info("=" * 60)
    
    # Ensure reports directory exists
    if output_path != "-" and output_path != "":
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

    # Check for admin privileges
    if not skip_admin and not is_admin():
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

    logger.info(f"Compliance Mode: {'Strict (Corporate/Managed)' if strict_mode else 'Standard (Personal/BYOD)'}")
    
    print("\n🔍 Starting Cyber Essentials compliance scan...")
    print(f"Mode: {'Strict' if strict_mode else 'Standard'}\n")
    
    system, version = get_os_info()
    os_info = OSInfo(platform=system, version=version)
    print(f"Detected: {system} {version}\n")

    # Select adapters
    w, m, l = osw, osm, osl

    results = []
    check_modules = [
        ("Firewalls", firewall),
        ("Secure Configuration", secure_configuration),
        ("Access Control", access_control),
        ("Malware Protection", malware_protection),
        ("Patch Management", patch_management),
        ("Remote Work & MDM", remote_work_mdm)
    ]
    
    total_checks = len(check_modules)
    for idx, (check_name, check) in enumerate(check_modules, 1):
        try:
            print(f"[{idx}/{total_checks}] Checking {check_name}...", end=" ", flush=True)
            logger.info(f"Running check: {check_name}")
            res = check.run(w, m, l, strict_mode=strict_mode)
            
            # Display result status
            status_icon = {"pass": "✓", "fail": "✗", "warn": "⚠", "unknown": "?"}.get(res.status, "?")
            print(f"{status_icon} {res.status.upper()}")
            logger.info(f"Check '{check_name}' completed with status: {res.status}")
        except Exception as e:
            # Defensive: no single check should crash the run
            print(f"✗ ERROR")
            logger.error(f"Check '{check_name}' failed with exception: {e}", exc_info=True)
            res = check.__name__, {
                "name": check_name,
                "status": "unknown",
                "score": 0.0,
                "findings": [f"Check error: {str(e)}"],
                "recommendations": ["Re-run with elevated privileges or contact support"],
                "details": {"error": str(e)}
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

    # Generate and save reports based on format
    if output_path == "-" or output_path == "":
        # Stdout: JSON only
        payload = json.dumps(doc, indent=2)
        print(payload)
    else:
        # File output: support JSON, HTML, or both
        # Organize reports into separate folders
        base_name = os.path.basename(output_path)
        
        # JSON path: reports/json/filename.json
        json_dir = os.path.join(os.path.dirname(output_path), "json")
        os.makedirs(json_dir, exist_ok=True)
        json_path = os.path.join(json_dir, base_name)
        
        # HTML path: reports/html/filename.html
        html_dir = os.path.join(os.path.dirname(output_path), "html")
        os.makedirs(html_dir, exist_ok=True)
        html_path = os.path.join(html_dir, base_name.replace('.json', '.html'))
        
        if output_format in ["json", "both"]:
            payload = json.dumps(doc, indent=2)
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(payload)
            print(f"\n✓ JSON report saved to: {json_path}")
            logger.info(f"JSON report written to {json_path}")
        
        if output_format in ["html", "both"]:
            html_content = generate_html_report(doc)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✓ HTML report saved to: {html_path}")
            logger.info(f"HTML report written to {html_path}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"Overall Status: {overall_status.upper()} (Score: {overall_score:.1f}/100)")
    print(f"{'=' * 60}\n")
    logger.info(f"Scan completed. Overall status: {overall_status}, score: {overall_score}")
    
    # Comparison with previous scan
    if args.compare and output_path != "-":
        previous_report = load_previous_scan(output_path)
        comparison = compare_reports(doc, previous_report)
        print_comparison(comparison)
        
        # Optionally save comparison data in json subfolder
        if comparison.get("has_previous"):
            # Save comparison in json folder
            base_name = os.path.basename(output_path).replace('.json', '_comparison.json')
            json_dir = os.path.join(os.path.dirname(output_path), "json")
            comparison_path = os.path.join(json_dir, base_name)
            save_comparison_report(comparison, comparison_path)
            logger.info(f"Comparison report saved to {comparison_path}")
    
    # Generate remediation script
    if args.generate_fix:
        if platform.system() == "Windows":
            try:
                # Create Auto_Fix_Scripts folder if it doesn't exist
                fix_scripts_dir = "Auto_Fix_Scripts"
                if not os.path.exists(fix_scripts_dir):
                    os.makedirs(fix_scripts_dir, exist_ok=True)
                
                # Generate script name based on report name
                if output_path != "-" and output_path != "":
                    # Extract base filename without path and extension
                    base_name = os.path.basename(output_path).replace('.json', '')
                    remediation_script = os.path.join(fix_scripts_dir, f"{base_name}_fix.ps1")
                else:
                    remediation_script = os.path.join(fix_scripts_dir, "report_fix.ps1")
                
                script_path = generate_remediation_script(doc, remediation_script)
                print(f"\n🔧 Remediation script generated: {script_path}")
                print(f"   Run as Administrator to apply automated fixes:")
                print(f"   Right-click '{script_path}' -> Run with PowerShell\n")
                logger.info(f"Remediation script generated: {script_path}")
            except Exception as e:
                print(f"\n⚠️  Failed to generate remediation script: {e}")
                logger.error(f"Remediation script generation failed: {e}")
        else:
            print(f"\n⚠️  Remediation scripts are only available for Windows systems.")
            logger.warning("Remediation script requested on non-Windows platform")

if __name__ == "__main__":
    main()