from __future__ import annotations

from dataclasses import asdict, dataclass, field
from functools import lru_cache
from pathlib import Path
import json
import re

from src.config import ROOT


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
_URL_RE = re.compile(r"https://[^\s`\"')]+")
_USER_AGENT_RE = re.compile(r"User-Agent:\s*([^\n`]+)")


@dataclass(frozen=True)
class SkillReference:
    name: str
    description: str = ""
    version: str = ""
    author: str = ""
    path: str = ""
    source: str = ""
    source_type: str = ""
    computed_hash: str = ""
    user_agent: str = ""
    endpoints: tuple[str, ...] = field(default_factory=tuple)
    mirrors: tuple[str, ...] = field(default_factory=tuple)

    def to_public_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["endpoints"] = list(self.endpoints)
        data["mirrors"] = list(self.mirrors)
        return data


def _skill_roots() -> list[Path]:
    return [
        ROOT / ".agents" / "skills",
        ROOT / ".claude" / "skills",
        ROOT / "skills",
    ]


def _load_skill_lock() -> dict[str, dict[str, str]]:
    lock_path = ROOT / "skills-lock.json"
    if not lock_path.exists():
        return {}
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    skills = payload.get("skills")
    if not isinstance(skills, dict):
        return {}
    return {
        str(name): {
            "source": str(info.get("source", "")),
            "source_type": str(info.get("sourceType", "")),
            "computed_hash": str(info.get("computedHash", "")),
        }
        for name, info in skills.items()
        if isinstance(info, dict)
    }


def _parse_frontmatter(text: str) -> dict[str, object]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}

    lines = match.group(1).splitlines()
    out: dict[str, object] = {"metadata": {}}
    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("name:"):
            out["name"] = stripped.split(":", 1)[1].strip().strip('"').strip("'")
        elif stripped.startswith("description:"):
            value = stripped.split(":", 1)[1].strip()
            if value == "|":
                parts: list[str] = []
                index += 1
                while index < len(lines):
                    sub = lines[index]
                    if sub.startswith("  ") or not sub.strip():
                        parts.append(sub[2:] if sub.startswith("  ") else "")
                        index += 1
                        continue
                    index -= 1
                    break
                out["description"] = "\n".join(parts).strip()
            else:
                out["description"] = value.strip('"').strip("'")
        elif stripped.startswith("metadata:"):
            metadata: dict[str, str] = {}
            index += 1
            while index < len(lines):
                sub = lines[index]
                if not sub.startswith("  "):
                    index -= 1
                    break
                meta_line = sub.strip()
                if ":" in meta_line:
                    key, value = meta_line.split(":", 1)
                    metadata[key.strip()] = value.strip().strip('"').strip("'")
                index += 1
            out["metadata"] = metadata

        index += 1
    return out


def _dedupe(values: list[str]) -> tuple[str, ...]:
    out: list[str] = []
    for value in values:
        item = value.strip()
        if item and item not in out:
            out.append(item)
    return tuple(out)


@lru_cache(maxsize=1)
def get_skill_registry() -> dict[str, SkillReference]:
    skill_lock = _load_skill_lock()
    discovered: dict[str, dict[str, object]] = {}

    for root in _skill_roots():
        if not root.exists():
            continue
        for skill_dir in root.iterdir():
            if not skill_dir.exists():
                continue
            skill_path = skill_dir / "SKILL.md"
            if not skill_path.exists():
                continue
            skill_name = skill_dir.name
            entry = discovered.setdefault(skill_name, {"primary": None, "mirrors": []})
            primary = entry.get("primary")
            if primary is None:
                entry["primary"] = skill_dir
            elif skill_dir != primary:
                mirrors = entry.setdefault("mirrors", [])
                if isinstance(mirrors, list):
                    mirrors.append(skill_dir)

    registry: dict[str, SkillReference] = {}
    for skill_name in sorted(set(discovered) | set(skill_lock)):
        entry = discovered.get(skill_name, {})
        primary = entry.get("primary")
        primary_path = Path(primary) if isinstance(primary, Path) else None
        mirrors = entry.get("mirrors") if isinstance(entry.get("mirrors"), list) else []
        skill_md = primary_path / "SKILL.md" if primary_path else None

        text = skill_md.read_text(encoding="utf-8") if skill_md and skill_md.exists() else ""
        frontmatter = _parse_frontmatter(text)
        metadata = frontmatter.get("metadata") if isinstance(frontmatter.get("metadata"), dict) else {}
        lock_info = skill_lock.get(skill_name, {})

        registry[skill_name] = SkillReference(
            name=str(frontmatter.get("name") or skill_name),
            description=str(frontmatter.get("description") or ""),
            version=str(metadata.get("version", "")),
            author=str(metadata.get("author", "")),
            path=str(primary_path) if primary_path else "",
            source=str(lock_info.get("source", "")),
            source_type=str(lock_info.get("source_type", "")),
            computed_hash=str(lock_info.get("computed_hash", "")),
            user_agent=str((_USER_AGENT_RE.search(text).group(1).strip()) if _USER_AGENT_RE.search(text) else ""),
            endpoints=_dedupe(_URL_RE.findall(text)),
            mirrors=tuple(str(Path(path)) for path in mirrors if Path(path) != primary_path),
        )
    return registry


def get_skill_reference(name: str) -> SkillReference | None:
    return get_skill_registry().get(name)


def skill_registry_snapshot(skill_names: list[str]) -> dict[str, dict[str, object]]:
    registry = get_skill_registry()
    snapshot: dict[str, dict[str, object]] = {}
    for name in skill_names:
        ref = registry.get(name)
        if ref is not None:
            snapshot[name] = ref.to_public_dict()
    return snapshot
