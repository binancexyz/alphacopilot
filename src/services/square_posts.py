from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import request
from urllib.error import HTTPError, URLError

from src.config import settings
from src.models.schemas import AnalysisBrief


@dataclass
class SquarePostResult:
    ok: bool
    mode: str
    text: str
    detail: str = ""
    response_body: str = ""
    post_id: str = ""
    post_url: str = ""


def build_square_post(brief: AnalysisBrief, *, max_chars: int = 280) -> str:
    if brief.entity.startswith("Price:"):
        text = _build_price_post(brief)
    elif brief.entity.startswith("Brief:"):
        text = _build_brief_post(brief)
    elif brief.entity.startswith("Risk:"):
        text = _build_risk_post(brief)
    elif brief.entity.startswith("Audit:"):
        text = _build_audit_post(brief)
    elif brief.entity.startswith("Token:"):
        text = _build_token_post(brief)
    elif brief.entity.startswith("Signal:"):
        text = _build_signal_post(brief)
    elif brief.entity.startswith("Wallet:"):
        text = _build_wallet_post(brief)
    elif brief.entity.startswith("Meme:"):
        text = _build_meme_post(brief)
    elif brief.entity == "Market Watch":
        text = _build_watchtoday_post(brief)
    else:
        text = brief.quick_verdict.strip()

    text = "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()
    if len(text) <= max_chars:
        return text
    trimmed = text[: max_chars - 1].rstrip()
    return trimmed + "…"


def _build_price_post(brief: AnalysisBrief) -> str:
    name, symbol, _link, rank = (brief.quick_verdict.split("|", 3) + ["", "", "", "0"])[:4]
    price, change_24h, _high, _low, market_cap, volume_24h, arrow = (brief.why_it_matters.split("|", 6) + ["0", "0", "0", "0", "0", "0", "➖"])[:7]
    lines = [f"💰 {name} ({symbol})"]
    bits = []
    if price and float(price or 0) > 0:
        bits.append(f"Price ${float(price):,.2f}")
    if rank and int(rank or 0) > 0:
        bits.append(f"Rank #{int(rank)}")
    if bits:
        lines.append(" | ".join(bits))
    lines.append(f"24h {float(change_24h or 0):+.2f}% {arrow}")
    mc_bits = []
    if float(market_cap or 0) > 0:
        mc_bits.append(f"Cap {_human_money_short(float(market_cap))}")
    if float(volume_24h or 0) > 0:
        mc_bits.append(f"Vol {_human_money_short(float(volume_24h))}")
    if mc_bits:
        lines.append(" | ".join(mc_bits))
    if brief.top_risks:
        lines.append(f"Note: {brief.top_risks[0]}")
    return "\n".join(lines)


def _build_brief_post(brief: AnalysisBrief) -> str:
    name, symbol, price, change, rank, signal_status, liquidity, top_risk, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "0", "0", "0", "unknown", "0", "", ""])[:9]
    lines = [f"🧩 {name} ({symbol})"]
    meta = []
    if rank and int(rank or 0) > 0:
        meta.append(f"Rank #{int(rank)}")
    if signal_status and signal_status != "unknown":
        meta.append(f"Signal {signal_status}")
    if meta:
        lines.append(" | ".join(meta))
    if float(price or 0) > 0:
        lines.append(f"Price ${float(price):,.2f} | 24h {float(change or 0):+.2f}%")
    if float(liquidity or 0) > 0:
        lines.append(f"Visible liquidity {_human_money_short(float(liquidity))}")
    if verdict:
        lines.append(verdict)
    if top_risk:
        lines.append(f"Risk: {top_risk}")
    return "\n".join(lines)


def _build_risk_post(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_risk, second_risk, liquidity, signal_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "0", "unknown", ""])[:9]
    lines = [f"🛡️ {name} ({symbol})", f"Risk {risk_level}"]
    if signal_status and signal_status != "unknown":
        lines[-1] += f" | Signal {signal_status}"
    if verdict:
        lines.append(verdict)
    if top_risk:
        lines.append(f"Top risk: {top_risk}")
    if second_risk:
        lines.append(f"Next: {second_risk}")
    if audit_summary:
        lines.append(f"Audit: {audit_summary}")
    if float(liquidity or 0) > 0:
        lines.append(f"Visible liquidity {_human_money_short(float(liquidity))}")
    return "\n".join(lines)


def _build_audit_post(brief: AnalysisBrief) -> str:
    name, symbol, risk_level, audit_summary, top_flag, second_flag, _liquidity, gate_status, verdict = (brief.quick_verdict.split("|", 8) + ["", "", "Medium", "", "", "", "0", "warn", ""])[:9]
    gate = brief.audit_gate or gate_status.upper()
    lines = [f"🔐 {name} ({symbol})", f"Gate {gate} | Risk {risk_level}"]
    if verdict:
        lines.append(verdict)
    if top_flag:
        lines.append(f"Primary: {top_flag}")
    if second_flag:
        lines.append(f"Next: {second_flag}")
    if audit_summary:
        lines.append(f"Summary: {audit_summary}")
    return "\n".join(lines)


def _build_token_post(brief: AnalysisBrief) -> str:
    symbol = brief.entity.split(":", 1)[1].strip() if ":" in brief.entity else brief.entity
    lines = [f"🪙 {symbol} scan"]
    if brief.audit_gate:
        lines.append(f"Gate: {brief.audit_gate}")
    lines.append(brief.quick_verdict)
    if brief.signal_quality:
        quality = brief.signal_quality if not brief.conviction else f"{brief.signal_quality} | Conviction {brief.conviction}"
        lines.append(f"Read: {quality}")
    if brief.top_risks:
        lines.append(f"Risk: {brief.top_risks[0]}")
    if brief.what_to_watch_next:
        lines.append(f"Watch: {brief.what_to_watch_next[0]}")
    tags = _top_tag_notes(brief)
    if tags:
        lines.append(f"Tags: {tags}")
    return "\n".join(lines)


def _build_signal_post(brief: AnalysisBrief) -> str:
    symbol = brief.entity.split(":", 1)[1].strip() if ":" in brief.entity else brief.entity
    lines = [f"📡 {symbol} signal"]
    if brief.audit_gate:
        lines.append(f"Gate: {brief.audit_gate}")
    lines.append(brief.quick_verdict)
    if brief.signal_quality:
        quality = brief.signal_quality if not brief.conviction else f"{brief.signal_quality} | Conviction {brief.conviction}"
        lines.append(f"Strength: {quality}")
    if brief.top_risks:
        lines.append(f"Risk: {brief.top_risks[0]}")
    if brief.what_to_watch_next:
        lines.append(f"Watch: {brief.what_to_watch_next[0]}")
    return "\n".join(lines)


def _build_wallet_post(brief: AnalysisBrief) -> str:
    follow = next((tag.note for tag in brief.risk_tags if tag.name == "Follow Verdict" and tag.note), "Unknown")
    address = brief.entity.split(":", 1)[1].strip() if ":" in brief.entity else brief.entity
    lines = [f"👛 Wallet {address[:6]}…{address[-4:]}", f"Follow: {follow}", brief.quick_verdict]
    if brief.why_it_matters:
        lines.append(brief.why_it_matters)
    if brief.top_risks:
        lines.append(f"Risk: {brief.top_risks[0]}")
    return "\n".join(lines)


def _build_watchtoday_post(brief: AnalysisBrief) -> str:
    signal_section = next((section for section in brief.sections if "Smart Money Flow" in section.title or "Signal" in section.title), None)
    attention_section = next((section for section in brief.sections if "Trending Now" in section.title), None)

    signal_line = ""
    if signal_section:
        signal_line = next((line.strip('- ').strip() for line in signal_section.content.splitlines() if line.strip()), "")

    attention_line = ""
    if attention_section:
        attention_line = next((line.strip('- ').strip() for line in attention_section.content.splitlines() if line.strip()), "")

    verdict = (brief.quick_verdict or "").strip()
    lower = verdict.lower()
    if "opportunity exists" in lower and "selectivity matters" in lower:
        verdict = "Opportunity visible. Be selective."
    elif "selectively instead of defensively" in lower or "selective rather than complete" in lower:
        verdict = "Opportunity visible. Stay selective."
    elif not verdict:
        verdict = "Opportunity visible. Be selective."
    lines = [verdict]
    if signal_line:
        lines.append(signal_line)
    if attention_line:
        lines.append(attention_line)
    return "\n".join(lines)


def _build_meme_post(brief: AnalysisBrief) -> str:
    symbol = brief.entity.split(":", 1)[1].strip() if ":" in brief.entity else brief.entity
    lines = [f"🚀 {symbol} meme scan"]
    if brief.audit_gate:
        lines.append(f"Gate: {brief.audit_gate}")
    lines.append(brief.quick_verdict)
    if brief.why_it_matters:
        lines.append(brief.why_it_matters)
    if brief.top_risks:
        lines.append(f"Risk: {brief.top_risks[0]}")
    if brief.what_to_watch_next:
        lines.append(f"Watch: {brief.what_to_watch_next[0]}")
    tags = _top_tag_notes(brief)
    if tags:
        lines.append(f"Tags: {tags}")
    return "\n".join(lines)


def _top_tag_notes(brief: AnalysisBrief) -> str:
    bits = []
    for tag in brief.risk_tags[:3]:
        if tag.note:
            bits.append(f"{tag.name}={tag.note}")
        else:
            bits.append(tag.name)
    return ", ".join(bits)


def _human_money_short(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000:
        return f"${value/1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    if abs_value >= 1_000:
        return f"${value/1_000:.1f}K"
    return f"${value:,.0f}"


def masked_square_key() -> str:
    key = settings.square_api_key.strip()
    if len(key) <= 9:
        return "<set>" if key else "<missing>"
    return f"{key[:5]}...{key[-4:]}"


def publish_square_post(text: str, *, dry_run: bool = False) -> SquarePostResult:
    text = text.strip()
    if not text:
        return SquarePostResult(ok=False, mode="validation", text=text, detail="Post text cannot be empty.")

    if dry_run:
        return SquarePostResult(ok=True, mode="dry-run", text=text, detail="Draft prepared; not published.")

    if not settings.square_api_key or settings.square_api_key == "your_api_key":
        return SquarePostResult(
            ok=False,
            mode="config",
            text=text,
            detail="BINANCE_SQUARE_API_KEY is not configured.",
        )

    if not settings.square_api_base_url:
        return SquarePostResult(
            ok=False,
            mode="config",
            text=text,
            detail="BINANCE_SQUARE_API_BASE_URL is not configured.",
        )

    endpoint = settings.square_api_base_url.rstrip("/") + settings.square_api_publish_path
    payload = json.dumps({"bodyTextOnly": text}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        settings.square_api_key_header: settings.square_api_key,
        "clienttype": "binanceSkill",
    }

    req = request.Request(endpoint, data=payload, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return _parse_square_response(text=text, body=body, fallback_detail=f"Posted to {endpoint}")
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return _parse_square_response(text=text, body=body, fallback_detail=f"HTTP {exc.code} from Square API", ok_override=False)
    except URLError as exc:
        return SquarePostResult(ok=False, mode="live", text=text, detail=f"Connection error: {exc}")


def _parse_square_response(text: str, body: str, fallback_detail: str, ok_override: bool | None = None) -> SquarePostResult:
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = {}

    code = str(payload.get("code", ""))
    message = payload.get("message")
    post_id = str((payload.get("data") or {}).get("id", "") or "")
    ok = (code == "000000") if ok_override is None else ok_override and code == "000000"

    detail = fallback_detail
    if message:
        detail = str(message)
    elif code and code != "000000":
        detail = f"Square API returned code {code}"
    elif code == "000000" and not post_id:
        detail = "Post may have succeeded, but Binance did not return a content id. Check Square manually."

    post_url = f"https://www.binance.com/square/post/{post_id}" if post_id else ""
    return SquarePostResult(ok=ok, mode="live", text=text, detail=detail, response_body=body, post_id=post_id, post_url=post_url)
