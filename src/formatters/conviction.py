from __future__ import annotations


def conviction_label(signal_quality: str, risk_count: int) -> str:
    quality = signal_quality.lower()
    if "high" in quality and risk_count <= 1:
        return "High"
    if "medium" in quality and risk_count <= 2:
        return "Medium"
    return "Medium-Low" if "medium" in quality else "Low"
