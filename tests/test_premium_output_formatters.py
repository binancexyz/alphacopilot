from src.formatters.brief_formatter import format_brief
from src.models.schemas import AnalysisBrief, BriefSection, RiskTag


def test_format_compact_brief_card_renders_market_section_and_wallet_count():
    brief = AnalysisBrief(
        entity="Brief: BNB",
        quick_verdict="BNB|BNB|612.5|3.25|0|active|1250000|Using Binance Spot market data via BNBUSDT; exchange price context is good, but setup quality still depends on confirmation.|Clean price context. Setup needs confirmation.|1200000000|85000000000|12|rising",
        signal_quality="High",
    )
    rendered = format_brief(brief)
    assert "Signal: Active follow-through · 12 wallets" in rendered
    assert "Trend: K-line rising" in rendered
    assert "**📊 Market**" in rendered
    assert "Volume 24h: $1.2B" in rendered
    assert "Market Cap: $85.0B" in rendered


def test_format_token_card_renders_market_and_momentum_sections():
    brief = AnalysisBrief(
        entity="Token: BNB",
        quick_verdict="Active setup. Structure is supportive.",
        signal_quality="High",
        why_it_matters="",
        audit_gate="ALLOW",
        beginner_note="\n".join([
            "Holders: 120,000",
            "Smart money: 5 wallets",
            "Top-10 concentration: 34.0%",
            "KOL holders: 8 (4.5%)",
            "Pro holders: 3 (2.2%)",
        ]),
        risk_tags=[
            RiskTag(name="Header Market", level="Info", note="612.5|3.25|0"),
            RiskTag(name="Liquidity", level="High", note="Visible liquidity 59300000"),
            RiskTag(name="Market Data", level="Info", note="Volume 24h: $1.2B | Market Cap: $85.0B | 24h Range: $595.00 – $625.00"),
            RiskTag(name="Momentum", level="High", note="5m +1.2% | 1h +3.4% | 4h +5.6%"),
        ],
    )
    rendered = format_brief(brief)
    assert "Momentum: 5m +1.2% | 1h +3.4% | 4h +5.6%" in rendered
    assert "**📊 Market**" in rendered
    assert "KOL holders: 8 (4.5%)" in rendered
    assert "Pro holders: 3 (2.2%)" in rendered


def test_format_signal_card_renders_context_section():
    brief = AnalysisBrief(
        entity="Signal: DOGE",
        quick_verdict="Active setup. Trigger is holding.",
        signal_quality="High",
        top_risks=["Visible signals can fail quickly when follow-through does not arrive."],
        audit_gate="ALLOW",
        risk_tags=[
            RiskTag(name="Header Market", level="Info", note="0.11|4.20|0"),
            RiskTag(name="Entry Zone", level="Info", note="$0.10 – $0.10"),
            RiskTag(name="Signal Timing", level="Low", note="Fresh | 0.5h old"),
            RiskTag(name="Invalidation", level="Info", note="Breaks if price loses the trigger zone and follow-through fades."),
            RiskTag(name="Volume 24h", level="Info", note="$1.2B"),
            RiskTag(name="Market Cap", level="Info", note="$45.0B"),
            RiskTag(name="Max Gain", level="Info", note="+45.2%"),
            RiskTag(name="Smart Money Inflow", level="High", note="~$250.0K"),
        ],
    )
    rendered = format_brief(brief)
    assert "**📊 Context**" in rendered
    assert "Volume 24h: $1.2B" in rendered
    assert "Market Cap: $45.0B" in rendered
    assert "Max Gain: +45.2%" in rendered
    assert "Smart Money Inflow: ~$250.0K" in rendered


def test_format_watchtoday_card_caps_extra_sections_at_six_total():
    brief = AnalysisBrief(
        entity="Market Watch",
        quick_verdict="Strong board. High selectivity needed.",
        signal_quality="High",
        top_risks=["Some board lanes are still sparse (Social Hype), so coverage is selective rather than complete."],
        sections=[
            BriefSection(title="🧠 Smart Money Flow", content="- BNB inflows"),
            BriefSection(title="🔥 Trending Now", content="- BNB +3.2%"),
            BriefSection(title="🏦 Exchange Board", content="- BNB +3.2% | BNBUSDT | strong"),
            BriefSection(title="👀 Today's Top 3", content="- BNB\n- BTC\n- SOL"),
            BriefSection(title="🌊 Narrative", content="- AI\n- L2"),
            BriefSection(title="🚀 Meme Watch", content="- PEPE\n- BONK"),
            BriefSection(title="📈 Futures Sentiment", content="- BTC funding +0.02%"),
            BriefSection(title="🏆 Top Traders", content="- 0x1234…5678"),
        ],
    )
    rendered = format_brief(brief)
    assert "**🏦 Exchange Board**" in rendered
    assert "**👀 Top 3 Picks**" in rendered
    assert "**🌊 Narrative**" in rendered
    assert "**🚀 Meme Watch**" in rendered
    assert "**📈 Futures Sentiment**" not in rendered
    assert "**🏆 Top Traders**" not in rendered


def test_format_audit_card_renders_market_context_section():
    brief = AnalysisBrief(
        entity="Audit: BNB",
        quick_verdict="BNB|BNB|Low|Risk level 0 (LOW)|Contract: No red flags|Tax: Buy 1.50% / Sell 2.00%|Liquidity: $20.0M visible|allow|Clean audit. Normal caution still applies.",
        signal_quality="Low",
        sections=[BriefSection(title="📊 Market Context", content="- Price: $612.50\n- Volume 24h: $1.2B")],
        audit_gate="ALLOW",
    )
    rendered = format_brief(brief)
    assert "**📊 Market Context**" in rendered
    assert "Price: $612.50" in rendered
    assert "Volume 24h: $1.2B" in rendered


def test_format_portfolio_card_renders_margin_trend_and_five_holdings():
    brief = AnalysisBrief(
        entity="Portfolio: Binance Spot",
        quick_verdict="Levered posture. Margin exposure is material.",
        signal_quality="Aggressive",
        why_it_matters="Estimated visible Spot value is about $120000.00 across 5 priced asset(s). Stablecoins are 20.0% of the priced snapshot and risk assets are 80.0%.",
        beginner_note="\n".join([
            "BTC ~$40,000.00 (33.3%)",
            "ETH ~$30,000.00 (25.0%)",
            "BNB ~$20,000.00 (16.7%)",
            "SOL ~$15,000.00 (12.5%)",
            "USDT ~$15,000.00 (12.5%)",
        ]),
        risk_tags=[
            RiskTag(name="Stablecoin Share", level="Medium", note="20.0%"),
            RiskTag(name="Lead Group", level="Info", note="Majors 58.0%"),
            RiskTag(name="Margin Exposure", level="High", note="Net equity $5,000.00 | borrowed $2,000.00"),
            RiskTag(name="Short Trend", level="Info", note="visible value is up versus the older local trend"),
        ],
    )
    rendered = format_brief(brief)
    assert "Lead group: Majors 58.0%" in rendered
    assert "USDT ~$15,000.00 (12.5%)" in rendered
    assert "**🏦 Margin**" in rendered
    assert "borrowed $2,000.00" in rendered
    assert "**📈 Snapshot Trend**" in rendered


def test_format_wallet_card_renders_value_holdings_and_narrative():
    brief = AnalysisBrief(
        entity="Wallet: 0x1234567890abcdef",
        quick_verdict="Trackable wallet. Useful behavior signal.",
        signal_quality="Medium",
        why_it_matters="This wallet tracks roughly $240,000 across 7 holding(s), so it is large enough to inspect for behavior rather than treating it as random dust.",
        beginner_note="\n".join([
            "BNB 38.5%",
            "BTC 17.0%",
            "SOL 12.0%",
            "24h Volatility: 16.5%",
            "Public wallet posture",
        ]),
        risk_tags=[
            RiskTag(name="Follow Verdict", level="Low", note="Track"),
            RiskTag(name="Style Profile", level="Low", note="selective diversified momentum-seeking"),
            RiskTag(name="Activity", level="High", note="24h change +5.1%"),
            RiskTag(name="Lead Holding", level="Medium", note="BNB 38.5%"),
            RiskTag(name="Narrative Risk", level="Medium", note="AI, L1"),
        ],
    )
    rendered = format_brief(brief)
    assert "~$240,000" in rendered
    assert "Style: selective diversified momentum-seeking" in rendered
    assert "Narrative: AI, L1" in rendered
    assert "**💼 Holdings**" in rendered
    assert "BTC 17.0%" in rendered
