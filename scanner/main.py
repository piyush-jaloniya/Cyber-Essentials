from __future__ import annotations
import argparse
import json
import datetime
import platform

from scanner.models import Report, OSInfo, combine_statuses, average_score
from scanner.utils import get_os_info

# OS adapters
from scanner.os import windows as osw
from scanner.os import macos as osm
from scanner.os import linux as osl

# Checks
from scanner.checks import firewall, secure_configuration, access_control, malware_protection, patch_management, remote_work_mdm

SCANNER_VERSION = "0.2.0"  # Updated for Cyber Essentials 2025 compliance

def main():
    parser = argparse.ArgumentParser(description="Cyber Essentials System Scanner")
    parser.add_argument("--output", "-o", type=str, default="-", help="Output file path or - for stdout")
    args = parser.parse_args()

    system, version = get_os_info()
    os_info = OSInfo(platform=system, version=version)

    # Select adapters
    w, m, l = osw, osm, osl

    results = []
    for check in [firewall, secure_configuration, access_control, malware_protection, patch_management, remote_work_mdm]:
        try:
            res = check.run(w, m, l)
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