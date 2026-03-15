from __future__ import annotations

# Exit pressure
EXIT_RATE_HIGH = 70
EXIT_RATE_MODERATE = 40

# Top-holder concentration
CONCENTRATION_EXTREME = 80
CONCENTRATION_HIGH = 65
CONCENTRATION_ELEVATED = 60
CONCENTRATION_MEANINGFUL = 45

# Wallet top-position concentration
WALLET_CONCENTRATION_EXTREME = 75
WALLET_CONCENTRATION_HIGH = 50
WALLET_CONCENTRATION_MEANINGFUL = 45

# Liquidity (USD)
LIQUIDITY_DEEP = 50_000_000
LIQUIDITY_MODERATE = 10_000_000
LIQUIDITY_THIN = 1_000_000

# Signal age (hours)
SIGNAL_AGE_STALE = 8
SIGNAL_AGE_AGING = 2

# Futures positioning
FUNDING_RATE_EXTREME = 0.001
FUNDING_RATE_ELEVATED = 0.0005
OI_CHANGE_SIGNIFICANT = 5.0  # percent
LS_RATIO_CROWDED_LONG = 1.25
LS_RATIO_CROWDED_SHORT = 0.9

# Market regime
BTC_TRENDING_THRESHOLD = 3.0  # percent 24h change
BTC_VOLATILE_THRESHOLD = 5.0  # percent 24h change
VOLUME_SPIKE_MULTIPLIER = 2.0  # vs average

# Momentum scoring
MOMENTUM_STRONG = 3.0  # percent
MOMENTUM_MODERATE = 1.0  # percent

# ATR-based entry zone
ATR_ZONE_MULTIPLIER = 1.5  # entry zone = trigger ± (ATR * multiplier)
ATR_FALLBACK_PCT = 0.01  # 1% fallback when no ATR data

# Risk/Reward
RR_MINIMUM_VIABLE = 1.5  # minimum R:R to flag as viable
RR_GOOD = 2.0  # good R:R ratio

# Rug-pull scoring
RUGPULL_HIGH = 70
RUGPULL_MODERATE = 40
