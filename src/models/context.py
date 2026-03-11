from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TokenContext:
    symbol: str
    display_name: str
    price: float = 0.0
    liquidity: float = 0.0
    holders: int = 0
    market_rank_context: str = ""
    signal_status: str = "unknown"
    signal_trigger_context: str = ""
    audit_flags: list[str] = field(default_factory=list)
    major_risks: list[str] = field(default_factory=list)
    smart_money_count: int = 0
    exit_rate: float = 0.0
    signal_age_hours: float = 0.0
    signal_freshness: str = "UNKNOWN"
    audit_gate: str = "ALLOW"
    blocked_reason: str = ""


@dataclass
class WalletHolding:
    symbol: str
    weight_pct: float


@dataclass
class WalletContext:
    address: str
    portfolio_value: float = 0.0
    holdings_count: int = 0
    top_holdings: list[WalletHolding] = field(default_factory=list)
    top_concentration_pct: float = 0.0
    change_24h: float = 0.0
    notable_exposures: list[str] = field(default_factory=list)
    major_risks: list[str] = field(default_factory=list)
    follow_verdict: str = "Unknown"
    style_read: str = ""


@dataclass
class WatchTodayContext:
    top_narratives: list[str] = field(default_factory=list)
    strongest_signals: list[str] = field(default_factory=list)
    risk_zones: list[str] = field(default_factory=list)
    market_takeaway: str = ""
    major_risks: list[str] = field(default_factory=list)
    trending_now: list[str] = field(default_factory=list)
    smart_money_flow: list[str] = field(default_factory=list)
    social_hype: list[str] = field(default_factory=list)
    meme_watch: list[str] = field(default_factory=list)
    top_picks: list[str] = field(default_factory=list)
    exchange_board: list[str] = field(default_factory=list)


@dataclass
class MemeContext:
    symbol: str
    display_name: str
    price: float = 0.0
    liquidity: float = 0.0
    market_rank_context: str = ""
    signal_status: str = "unknown"
    audit_flags: list[str] = field(default_factory=list)
    major_risks: list[str] = field(default_factory=list)
    smart_money_count: int = 0
    exit_rate: float = 0.0
    signal_age_hours: float = 0.0
    signal_freshness: str = "UNKNOWN"
    audit_gate: str = "ALLOW"
    blocked_reason: str = ""
    launch_platform: str = ""
    is_alpha: bool = False
    lifecycle_stage: str = "unknown"
    bonded_progress: float = 0.0


@dataclass
class SignalContext:
    token: str
    signal_status: str = "unknown"
    trigger_price: float = 0.0
    current_price: float = 0.0
    max_gain: float = 0.0
    exit_rate: float = 0.0
    audit_flags: list[str] = field(default_factory=list)
    supporting_context: str = ""
    major_risks: list[str] = field(default_factory=list)
    smart_money_count: int = 0
    signal_age_hours: float = 0.0
    signal_freshness: str = "UNKNOWN"
    audit_gate: str = "ALLOW"
    blocked_reason: str = ""
