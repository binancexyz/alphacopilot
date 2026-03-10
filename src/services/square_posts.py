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


def publish_square_post(text: str, *, dry_run: bool = False) -> SquarePostResult:
    text = text.strip()
    if not text:
        return SquarePostResult(ok=False, mode="validation", text=text, detail="Post text cannot be empty.")

    if dry_run:
        return SquarePostResult(ok=True, mode="dry-run", text=text, detail="Draft prepared; not published.")

    if not settings.square_api_key:
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
    payload = json.dumps({"text": text}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        settings.square_api_key_header: settings.square_api_key,
    }

    req = request.Request(endpoint, data=payload, headers=headers, method="POST")
    try:
        with request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return SquarePostResult(ok=True, mode="live", text=text, detail=f"Posted to {endpoint}", response_body=body)
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return SquarePostResult(ok=False, mode="live", text=text, detail=f"HTTP {exc.code} from Square API", response_body=body)
    except URLError as exc:
        return SquarePostResult(ok=False, mode="live", text=text, detail=f"Connection error: {exc}")
