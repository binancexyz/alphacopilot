from __future__ import annotations


def bullet_join(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
