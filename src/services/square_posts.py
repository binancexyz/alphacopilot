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
    lines: list[str] = []
    lines.append(brief.quick_verdict.strip())

    if brief.signal_quality:
        lines.append(f"Signal Quality: {brief.signal_quality}")
    if brief.conviction:
        lines.append(f"Conviction: {brief.conviction}")
    if brief.top_risks:
        lines.append(f"Main risk: {brief.top_risks[0]}")
    if brief.what_to_watch_next:
        lines.append(f"Watch: {brief.what_to_watch_next[0]}")

    text = " | ".join(part for part in lines if part).strip()
    if len(text) <= max_chars:
        return text

    trimmed = text[: max_chars - 1].rstrip()
    return trimmed + "…"


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
