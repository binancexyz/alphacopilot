from __future__ import annotations

from src.analyzers.posture_context import load_portfolio_posture, posture_risk_note
from src.models.schemas import AnalysisBrief


def portfolio_note_for(symbol: str) -> str:
    snapshot = load_portfolio_posture()
    return posture_risk_note(snapshot, symbol)


def append_posture_note_to_brief(brief: AnalysisBrief, symbol: str) -> str:
    note = portfolio_note_for(symbol)
    if not note:
        return ""
    if note not in brief.top_risks:
        brief.top_risks.append(note)
    if brief.why_it_matters and note not in brief.why_it_matters:
        brief.why_it_matters += f" {note}"
    return note
