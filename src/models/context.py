from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TokenContext:
    symbol: str
    display_name: str
    price: float = 0.0
    liquidity: float = 0.0
    holders: int = 0
    volume_24h: float = 0.0
    pct_change_24h: float = 0.0
    market_cap: float = 0.0
    top_holder_concentration_pct: float = 0.0
    market_rank_context: str = ""
    signal_status: str = "unknown"
    signal_trigger_context: str = ""
    audit_flags: list[str] = field(default_factory=list)
    major_risks: list[str] = field(default_factory=list)
    smart_money_count: int = 0
    smart_money_holders: int = 0
    smart_money_holding_pct: float = 0.0
    smart_money_inflow_usd: float = 0.0
    smart_money_inflow_traders: int = 0
    exit_rate: float = 0.0
    signal_age_hours: float = 0.0
    signal_freshness: str = "UNKNOWN"
    audit_gate: str = "ALLOW"
    blocked_reason: str = ""
    futures_funding_rate: float = 0.0
    futures_long_short_ratio: float = 0.0
    futures_sentiment: str = ""
    meme_lifecycle: str = ""
    meme_bonded_progress: float = 0.0
    is_meme_candidate: bool = False
    kline_trend: str = ""
    kline_above_ma20: bool = False
    top_trader_interest: bool = False


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
    volatility_24h: float = 0.0
    notable_exposures: list[str] = field(default_factory=list)
    major_risks: list[str] = field(default_factory=list)
    follow_verdict: str = "Unknown"
    style_read: str = ""
    style_profile: str = ""
    exposure_breakdown: list[str] = field(default_factory=list)
    risky_holdings_count: int = 0
    holdings_audit_notes: list[str] = field(default_factory=list)


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
    meme_score: float = 0.0
    social_brief: str = ""
    top_holder_concentration_pct: float = 0.0


@dataclass
class SignalContext:
    token: str
    signal_status: str = "unknown"
    trigger_price: float = 0.0
    current_price: float = 0.0
    max_gain: float = 0.0
    exit_rate: float = 0.0
    liquidity: float = 0.0
    holders: int = 0
    volume_24h: float = 0.0
    pct_change_24h: float = 0.0
    market_cap: float = 0.0
    audit_flags: list[str] = field(default_factory=list)
    supporting_context: str = ""
    major_risks: list[str] = field(default_factory=list)
    smart_money_count: int = 0
    smart_money_holders: int = 0
    smart_money_holding_pct: float = 0.0
    smart_money_inflow_usd: float = 0.0
    signal_age_hours: float = 0.0
    signal_freshness: str = "UNKNOWN"
    audit_gate: str = "ALLOW"
    blocked_reason: str = ""
    funding_rate: float = 0.0
    long_short_ratio: float = 0.0
    funding_sentiment: str = ""
