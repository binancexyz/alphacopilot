from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimePayload:
    command: str
    entity: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)
