"""
Scan Comparison Module
Compares current scan results with previous scans to show changes.
"""

import json
import os
from typing import Dict, List, Tuple, Any
from datetime import datetime

def load_previous_scan(report_path: str) -> Dict[str, Any]:
    """Load the most recent scan report"""
    if not os.path.exists(report_path):
        return {}
    
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def compare_control_status(current: str, previous: str) -> Tuple[str, str]:
    """
    Compare control statuses and return (change_indicator, description).
    
    Returns:
        - ("→", "no change") if status is the same
        - ("↑", "improved") if status improved
        - ("↓", "degraded") if status worsened
    """
    status_rank = {"fail": 0, "unknown": 1, "warn": 2, "pass": 3}
    
    current_rank = status_rank.get(current.lower(), 1)
    previous_rank = status_rank.get(previous.lower(), 1)
    
    if current_rank > previous_rank:
        return ("↑", "improved")
    elif current_rank < previous_rank:
        return ("↓", "degraded")
    else:
        return ("→", "no change")

def compare_reports(current_report: Dict[str, Any], previous_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two scan reports and generate comparison data.
    
    Args:
        current_report: Current scan data
        previous_report: Previous scan data
    
    Returns:
        Dictionary with comparison results
    """
    if not previous_report:
        return {
            "has_previous": False,
            "message": "No previous scan found for comparison"
        }
    
    # Extract data
    current_controls = {c["name"]: c for c in current_report.get("controls", [])}
    previous_controls = {c["name"]: c for c in previous_report.get("controls", [])}
    
    current_overall = current_report.get("overall", {})
    previous_overall = previous_report.get("overall", {})
    
    # Compare each control
    control_changes = []
    for name, current_ctrl in current_controls.items():
        if name in previous_controls:
            previous_ctrl = previous_controls[name]
            
            current_status = current_ctrl.get("status", "unknown")
            previous_status = previous_ctrl.get("status", "unknown")
            current_score = current_ctrl.get("score", 0)
            previous_score = previous_ctrl.get("score", 0)
            
            indicator, description = compare_control_status(current_status, previous_status)
            score_change = current_score - previous_score
            
            control_changes.append({
                "name": name,
                "current_status": current_status,
                "previous_status": previous_status,
                "status_change": description,
                "change_indicator": indicator,
                "current_score": current_score,
                "previous_score": previous_score,
                "score_change": score_change
            })
    
    # Overall comparison
    overall_indicator, overall_description = compare_control_status(
        current_overall.get("status", "unknown"),
        previous_overall.get("status", "unknown")
    )
    
    overall_score_change = current_overall.get("score", 0) - previous_overall.get("score", 0)
    
    # Count changes
    improved_count = sum(1 for c in control_changes if c["status_change"] == "improved")
    degraded_count = sum(1 for c in control_changes if c["status_change"] == "degraded")
    unchanged_count = sum(1 for c in control_changes if c["status_change"] == "no change")
    
    return {
        "has_previous": True,
        "previous_scan_time": previous_report.get("timestamp_utc", "Unknown"),
        "current_scan_time": current_report.get("timestamp_utc", "Unknown"),
        "overall": {
            "current_status": current_overall.get("status", "unknown"),
            "previous_status": previous_overall.get("status", "unknown"),
            "status_change": overall_description,
            "change_indicator": overall_indicator,
            "current_score": current_overall.get("score", 0),
            "previous_score": previous_overall.get("score", 0),
            "score_change": overall_score_change
        },
        "controls": control_changes,
        "summary": {
            "improved": improved_count,
            "degraded": degraded_count,
            "unchanged": unchanged_count,
            "total": len(control_changes)
        }
    }

def print_comparison(comparison: Dict[str, Any]):
    """Print comparison results to console"""
    if not comparison.get("has_previous"):
        print(f"\nℹ️  {comparison.get('message', 'No comparison available')}\n")
        return
    
    print("\n" + "=" * 60)
    print("📊 SCAN COMPARISON")
    print("=" * 60)
    
    # Timestamps
    prev_time = comparison["previous_scan_time"]
    curr_time = comparison["current_scan_time"]
    print(f"Previous: {prev_time}")
    print(f"Current:  {curr_time}\n")
    
    # Overall change
    overall = comparison["overall"]
    indicator = overall["change_indicator"]
    print(f"Overall Status: {overall['previous_status'].upper()} → {overall['current_status'].upper()} {indicator}")
    print(f"Overall Score:  {overall['previous_score']:.1f} → {overall['current_score']:.1f} "
          f"({overall['score_change']:+.1f})\n")
    
    # Summary
    summary = comparison["summary"]
    print(f"Control Changes:")
    print(f"  ↑ Improved:  {summary['improved']}")
    print(f"  ↓ Degraded:  {summary['degraded']}")
    print(f"  → Unchanged: {summary['unchanged']}\n")
    
    # Show detailed changes (only those that changed)
    changed_controls = [c for c in comparison["controls"] if c["status_change"] != "no change"]
    if changed_controls:
        print("Detailed Changes:")
        print("-" * 60)
        for ctrl in changed_controls:
            indicator = ctrl["change_indicator"]
            print(f"{indicator} {ctrl['name']}")
            print(f"   Status: {ctrl['previous_status']} → {ctrl['current_status']}")
            print(f"   Score:  {ctrl['previous_score']:.0f} → {ctrl['current_score']:.0f} "
                  f"({ctrl['score_change']:+.0f})")
    else:
        print("No significant changes detected.")
    
    print("=" * 60 + "\n")

def save_comparison_report(comparison: Dict[str, Any], output_path: str):
    """Save comparison data to JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2)
