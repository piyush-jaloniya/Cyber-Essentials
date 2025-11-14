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
    # fail > warn > unknown > pass
    if any(s == "fail" for s in statuses):
        return "fail"
    if any(s == "warn" for s in statuses):
        return "warn"
    if any(s == "unknown" for s in statuses):
        return "unknown"
    return "pass"

def average_score(scores: List[float]) -> float:
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)