from __future__ import annotations

from src.models.schemas import AnalysisBrief


def format_brief(brief: AnalysisBrief) -> str:
    parts: list[str] = []
    parts.append(f"**{brief.entity}**")
    parts.append("")
    parts.append("**Quick Verdict**")
    parts.append(brief.quick_verdict)
    parts.append("")
    parts.append("**Signal Quality**")
    parts.append(brief.signal_quality)
    parts.append("")
    parts.append("**Top Risks**")
    if brief.top_risks:
        parts.extend([f"- {item}" for item in brief.top_risks])
    else:
        parts.append("- No major risks identified yet; still requires normal caution.")
    parts.append("")
    parts.append("**Why It Matters**")
    parts.append(brief.why_it_matters)
    parts.append("")
    parts.append("**What To Watch Next**")
    if brief.what_to_watch_next:
        parts.extend([f"- {item}" for item in brief.what_to_watch_next])
    else:
        parts.append("- Watch for confirmation, liquidity, and follow-through.")

    if brief.risk_tags:
        parts.append("")
        parts.append("**Risk Tags**")
        for tag in brief.risk_tags:
            suffix = f" — {tag.note}" if tag.note else ""
            parts.append(f"- {tag.name}: {tag.level}{suffix}")

    if brief.conviction:
        parts.append("")
        parts.append("**Conviction**")
        parts.append(brief.conviction)

    if brief.beginner_note:
        parts.append("")
        parts.append("**Beginner Note**")
        parts.append(brief.beginner_note)

    return "\n".join(parts).strip() + "\n"
