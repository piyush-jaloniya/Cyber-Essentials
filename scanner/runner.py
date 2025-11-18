import os
import datetime
import json
import logging
from typing import Callable, Dict, Any

from scanner.models import Report, OSInfo, combine_statuses, average_score
from scanner.utils import get_os_info
from scanner.report_generator import generate_html_report
from scanner.comparison import load_previous_scan, compare_reports, save_comparison_report
from scanner.remediation import generate_remediation_script

# OS adapters
from scanner.os import windows as osw
from scanner.os import macos as osm
from scanner.os import linux as osl

# Checks
from scanner.checks import (
    firewall, secure_configuration, access_control,
    malware_protection, patch_management, remote_work_mdm
)

logger = logging.getLogger(__name__)


def run_scan(
    output_path: str = "reports/report.json",
    output_format: str = "both",
    strict_mode: bool = False,
    compare: bool = False,
    generate_fix: bool = False,
    skip_admin: bool = True,
    progress_callback: Callable[[str], None] | None = None,
) -> Dict[str, Any]:
    """
    Programmatic scan runner. Returns a dictionary with report paths and the final 'doc'.

    Args:
        output_path: Path to JSON report (written to reports/json)
        output_format: json, html, or both
        strict_mode: boolean to enable strict compliance mode
        compare: perform comparison with previous scan
        generate_fix: create remediation script for Windows
        skip_admin: skip elevation check
        progress_callback: optional function called with raw message lines
    """

    def _log(msg: str):
        if progress_callback:
            try:
                progress_callback(msg)
            except Exception:
                logger.debug("progress_callback failed", exc_info=True)

    _log("Starting programmatic scan...")

    system, version = get_os_info()
    os_info = OSInfo(platform=system, version=version)

    # Check modules
    results = []
    check_modules = [
        ("Firewalls", firewall),
        ("Secure Configuration", secure_configuration),
        ("Access Control", access_control),
        ("Malware Protection", malware_protection),
        ("Patch Management", patch_management),
        ("Remote Work & MDM", remote_work_mdm),
    ]

    total_checks = len(check_modules)
    for idx, (check_name, check) in enumerate(check_modules, 1):
        try:
            _log(f"[{idx}/{total_checks}] Checking {check_name}...")
            res = check.run(osw, osm, osl, strict_mode=strict_mode)
            _log(f"{check_name} => {res.status}")
        except Exception as e:
            _log(f"{check_name} => ERROR: {e}")
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
        scanner_version="0.2.0",
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
        "overall": report.overall,
    }

    # Save JSON
    root_reports = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    json_dir = os.path.join(root_reports, "json")
    html_dir = os.path.join(root_reports, "html")
    os.makedirs(json_dir, exist_ok=True)
    os.makedirs(html_dir, exist_ok=True)

    base_name = os.path.basename(output_path)
    json_path = os.path.join(json_dir, base_name)
    html_path = os.path.join(html_dir, base_name.replace('.json', '.html'))

    if output_format in ("json", "both"):
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2)
        _log(f"JSON saved to: {json_path}")

    if output_format in ("html", "both"):
        html_content = generate_html_report(doc)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        _log(f"HTML saved to: {html_path}")

    if compare:
        previous = load_previous_scan(json_path)
        comparison = compare_reports(doc, previous)
        if comparison.get("has_previous"):
            comparison_path = os.path.join(json_dir, base_name.replace('.json', '_comparison.json'))
            save_comparison_report(comparison, comparison_path)
            _log(f"Comparison saved to: {comparison_path}")

    if generate_fix and os.name == 'nt':
        fix_scripts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Auto_Fix_Scripts")
        os.makedirs(fix_scripts_dir, exist_ok=True)
        remediation_script = os.path.join(fix_scripts_dir, f"{os.path.splitext(base_name)[0]}_fix.ps1")
        script_path = generate_remediation_script(doc, remediation_script)
        _log(f"Remediation script: {script_path}")

    _log("Scan finished")
    _log(f"Overall Status: {overall_status.upper()} (Score: {overall_score:.1f}/100)")

    return {"doc": doc, "json_path": json_path, "html_path": html_path}
