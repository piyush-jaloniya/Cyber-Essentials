from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Literal, Dict, Any, Optional

Status = Literal["pass", "warn", "fail", "unknown"]

@dataclass
class ControlResult:
    name: str
    status: Status
    score: float
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OSInfo:
    platform: str
    version: str

@dataclass
class Report:
    scanner_version: str
    timestamp_utc: str
    os: OSInfo
    controls: List[ControlResult]
    overall: Dict[str, Any]

def combine_statuses(statuses: List[Status]) -> Status:
    """
    Determine overall status using intelligent majority voting.
    
    Professional logic for CE compliance:
    - ANY failure (fail) = overall FAIL (CE requirement not met)
    - Multiple warnings or warning + unknown = WARN
    - Mostly passes with 1 unknown = WARN (incomplete assessment)
    - Majority passes (67%+) = PASS
    - Mixed results = WARN (safe default)
    """
    if not statuses:
        return "unknown"
    
    # Count each status type
    counts = {"fail": 0, "warn": 0, "pass": 0, "unknown": 0}
    for s in statuses:
        counts[s] += 1
    
    total = len(statuses)
    
    # CRITICAL: Any failure means CE compliance failure
    if counts["fail"] > 0:
        return "fail"
    
    # Multiple warnings or warning combined with unknown
    if counts["warn"] >= 2 or (counts["warn"] >= 1 and counts["unknown"] >= 1):
        return "warn"
    
    # Single unknown among mostly passes = warn (incomplete assessment)
    if counts["unknown"] >= 1 and counts["pass"] >= total - 1:
        return "warn"
    
    # Strong pass: majority of controls passed (67% threshold)
    if counts["pass"] >= (total * 0.67):
        return "pass"
    
    # All passed
    if counts["pass"] == total:
        return "pass"
    
    # Default to warn for mixed/unclear results
    return "warn"

def average_score(scores: List[float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)