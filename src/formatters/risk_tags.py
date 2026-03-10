from __future__ import annotations

from src.models.schemas import RiskTag


DEFAULT_HIGH_RISK = RiskTag(name="Narrative Risk", level="High", note="Attention can reverse quickly.")
DEFAULT_MEDIUM_LIQUIDITY_RISK = RiskTag(name="Liquidity Risk", level="Medium", note="Watch liquidity depth and follow-through.")
DEFAULT_LOW_CONTRACT_RISK = RiskTag(name="Contract Risk", level="Low", note="No obvious contract concern surfaced in the current pass.")
