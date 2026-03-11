from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RiskTag:
    name: str
    level: str
    note: Optional[str] = None


@dataclass
class BriefSection:
    title: str
    content: str


@dataclass
class AnalysisBrief:
    entity: str
    quick_verdict: str
    signal_quality: str
    top_risks: list[str] = field(default_factory=list)
    why_it_matters: str = ""
    what_to_watch_next: list[str] = field(default_factory=list)
    risk_tags: list[RiskTag] = field(default_factory=list)
    sections: list[BriefSection] = field(default_factory=list)
    conviction: Optional[str] = None
    beginner_note: Optional[str] = None
    audit_gate: Optional[str] = None
    blocked_reason: Optional[str] = None
