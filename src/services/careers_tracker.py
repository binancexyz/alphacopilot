from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime, UTC
import json
import re
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[2]
CACHE_PATH = ROOT / "tmp" / "binance_careers_cache.json"
DEFAULT_CAREERS_URL = "https://www.binance.com/en/careers/job-openings?team=All"


@dataclass
class CareerJob:
    title: str
    team: str = "Unknown"
    location: str = "Unknown"
    url: str = ""
    requisition_id: str = ""


@dataclass
class CareersSnapshot:
    source: str
    fetched_at: str
    url: str
    jobs: list[CareerJob]
    warning: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "fetched_at": self.fetched_at,
            "url": self.url,
            "warning": self.warning,
            "jobs": [asdict(job) for job in self.jobs],
        }


def fetch_careers_page(url: str = DEFAULT_CAREERS_URL, timeout: float = 20.0) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
    }
    with httpx.Client(timeout=timeout, follow_redirects=True, headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def extract_jobs_from_html(html: str) -> list[CareerJob]:
    jobs: list[CareerJob] = []
    seen: set[tuple[str, str, str]] = set()

    for job in _extract_jsonld_jobs(html):
        key = (job.title, job.url or "", job.requisition_id or "")
        if key not in seen:
            seen.add(key)
            jobs.append(job)

    for job in _extract_generic_jobs(html):
        key = (job.title, job.url or "", job.requisition_id or "")
        if key not in seen:
            seen.add(key)
            jobs.append(job)

    return jobs


def _extract_jsonld_jobs(html: str) -> list[CareerJob]:
    jobs: list[CareerJob] = []
    for match in re.finditer(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.I | re.S):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for item in _walk_json(payload):
            if not isinstance(item, dict):
                continue
            if str(item.get("@type", "")).lower() != "jobposting":
                continue
            title = _pick(item, "title")
            if not title:
                continue
            location = _extract_location(item)
            url = _pick(item, "url")
            jobs.append(CareerJob(title=title, location=location or "Unknown", url=url or ""))
    return jobs


GENERIC_TITLE_KEYS = {"title", "jobtitle", "positionname", "name"}
GENERIC_TEAM_KEYS = {"team", "department", "departments", "category", "function"}
GENERIC_LOCATION_KEYS = {"location", "city", "country", "locations"}
GENERIC_URL_KEYS = {"url", "joburl", "applyurl", "detailurl"}
GENERIC_ID_KEYS = {"jobid", "id", "requisitionid", "reqid"}


def _extract_generic_jobs(html: str) -> list[CareerJob]:
    jobs: list[CareerJob] = []
    for payload in _extract_json_blobs(html):
        for item in _walk_json(payload):
            if not isinstance(item, dict):
                continue
            normalized = {str(k).lower(): v for k, v in item.items()}
            title = _first_value(normalized, GENERIC_TITLE_KEYS)
            if not title:
                continue
            if not _looks_like_job_title(str(title)):
                continue
            team = _first_value(normalized, GENERIC_TEAM_KEYS) or "Unknown"
            location = _first_value(normalized, GENERIC_LOCATION_KEYS) or "Unknown"
            url = _first_value(normalized, GENERIC_URL_KEYS) or ""
            requisition_id = str(_first_value(normalized, GENERIC_ID_KEYS) or "")
            jobs.append(
                CareerJob(
                    title=_clean_text(str(title)),
                    team=_clean_text(_stringify(location_or_team := team)),
                    location=_clean_text(_stringify(location)),
                    url=_clean_text(str(url)),
                    requisition_id=requisition_id,
                )
            )
    return jobs


def snapshot_from_jobs(jobs: list[CareerJob], url: str = DEFAULT_CAREERS_URL, source: str = "live", warning: str | None = None) -> CareersSnapshot:
    return CareersSnapshot(source=source, fetched_at=datetime.now(UTC).isoformat(), url=url, jobs=jobs, warning=warning)


def save_snapshot(snapshot: CareersSnapshot, path: Path = CACHE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


def load_snapshot(path: Path = CACHE_PATH) -> CareersSnapshot | None:
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    jobs = [CareerJob(**item) for item in payload.get("jobs", [])]
    return CareersSnapshot(
        source=str(payload.get("source", "cache")),
        fetched_at=str(payload.get("fetched_at", "")),
        url=str(payload.get("url", DEFAULT_CAREERS_URL)),
        jobs=jobs,
        warning=payload.get("warning"),
    )


def refresh_snapshot(url: str = DEFAULT_CAREERS_URL, path: Path = CACHE_PATH) -> CareersSnapshot:
    html = fetch_careers_page(url)
    jobs = extract_jobs_from_html(html)
    warning = None if jobs else "No jobs could be extracted from the current careers page response."
    snapshot = snapshot_from_jobs(jobs, url=url, source="live", warning=warning)
    save_snapshot(snapshot, path)
    return snapshot


def summarize_snapshot(snapshot: CareersSnapshot, limit: int = 6) -> str:
    header = "Binance Careers Pulse"
    status_line = f"Source: {snapshot.source} | fetched_at: {snapshot.fetched_at}"
    if snapshot.warning:
        status_line += f" | warning: {snapshot.warning}"

    if not snapshot.jobs:
        return "\n".join([
            header,
            status_line,
            "No current job rows are available yet.",
            "Best use for now: keep this as ecosystem intelligence, not trading logic.",
            f"URL: {snapshot.url}",
        ])

    team_counts = Counter(job.team for job in snapshot.jobs if job.team and job.team != "Unknown")
    location_counts = Counter(job.location for job in snapshot.jobs if job.location and job.location != "Unknown")

    lines = [header, status_line, f"Openings captured: {len(snapshot.jobs)}"]
    if team_counts:
        top_teams = ", ".join(f"{team} ({count})" for team, count in team_counts.most_common(4))
        lines.append(f"Top teams: {top_teams}")
    if location_counts:
        top_locations = ", ".join(f"{location} ({count})" for location, count in location_counts.most_common(4))
        lines.append(f"Top locations: {top_locations}")

    lines.append("Interesting openings:")
    for job in snapshot.jobs[:limit]:
        bits = [f"- {job.title}"]
        if job.team and job.team != "Unknown":
            bits.append(job.team)
        if job.location and job.location != "Unknown":
            bits.append(job.location)
        if job.url:
            bits.append(job.url)
        lines.append(" | ".join(bits))

    lines.append("Takeaway: use this as Binance ecosystem / company-priority context, not as a direct market signal.")
    return "\n".join(lines)


def refresh_or_load(url: str = DEFAULT_CAREERS_URL, path: Path = CACHE_PATH) -> CareersSnapshot:
    try:
        return refresh_snapshot(url=url, path=path)
    except Exception as exc:
        cached = load_snapshot(path)
        if cached is not None:
            cached.warning = f"Live refresh failed; using cache. Reason: {exc}"
            return cached
        return snapshot_from_jobs([], url=url, source="unavailable", warning=f"Live refresh failed and no cache exists. Reason: {exc}")


def _extract_json_blobs(html: str) -> list[Any]:
    payloads: list[Any] = []
    for match in re.finditer(r'<script[^>]*>(.*?)</script>', html, re.I | re.S):
        raw = match.group(1).strip()
        if not raw or raw.startswith("function") or len(raw) < 20:
            continue
        if "{" not in raw and "[" not in raw:
            continue
        candidate = raw
        if "=" in candidate and candidate.split("=", 1)[0].strip().startswith(("window.", "self.", "__")):
            candidate = candidate.split("=", 1)[1].strip().rstrip(";")
        try:
            payloads.append(json.loads(candidate))
        except json.JSONDecodeError:
            continue
    return payloads


def _walk_json(value: Any):
    stack = [value]
    while stack:
        current = stack.pop()
        yield current
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)


def _first_value(payload: dict[str, Any], keys: set[str]) -> Any:
    for key in keys:
        if key in payload and payload[key] not in (None, "", [], {}):
            return payload[key]
    return None


def _pick(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value in (None, ""):
        return None
    return _clean_text(_stringify(value))


def _stringify(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(_stringify(item) for item in value if item not in (None, ""))
    if isinstance(value, dict):
        for candidate in ("name", "label", "value", "title"):
            if value.get(candidate):
                return _stringify(value[candidate])
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _extract_location(payload: dict[str, Any]) -> str:
    direct = payload.get("jobLocation") or payload.get("applicantLocationRequirements")
    if isinstance(direct, list):
        values = [_extract_location(item) for item in direct]
        values = [value for value in values if value]
        return ", ".join(values)
    if isinstance(direct, dict):
        address = direct.get("address")
        if isinstance(address, dict):
            pieces = [address.get("addressLocality"), address.get("addressRegion"), address.get("addressCountry")]
            cleaned = [_clean_text(str(piece)) for piece in pieces if piece]
            if cleaned:
                return ", ".join(cleaned)
        for key in ("name", "addressLocality", "addressRegion", "addressCountry"):
            if direct.get(key):
                return _clean_text(_stringify(direct[key]))
    return ""


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _looks_like_job_title(text: str) -> bool:
    cleaned = _clean_text(text)
    if len(cleaned) < 4 or len(cleaned) > 140:
        return False
    blacklist = {"all", "remote", "singapore", "london", "binance", "careers", "job openings"}
    lowered = cleaned.lower()
    if lowered in blacklist:
        return False
    role_keywords = (
        "engineer", "manager", "lead", "director", "analyst", "specialist", "designer", "developer",
        "product", "research", "marketing", "operations", "compliance", "security", "data", "intern",
        "associate", "counsel", "trader", "sales", "qa", "devops", "sre", "recruiter", "writer",
    )
    return any(keyword in lowered for keyword in role_keywords)
