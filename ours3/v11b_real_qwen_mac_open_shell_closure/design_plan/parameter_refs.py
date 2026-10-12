"""Parameter reference grammar helpers."""
from __future__ import annotations

from design_plan.schema import REF_GRAMMAR, is_ref


def parse_ref(text: str) -> dict[str, str]:
    if not is_ref(text):
        raise ValueError(f"invalid_ref:{text}")
    parts = text.split(".")
    return {"root": parts[0], "path": text, "tail": parts[-1], "family": parts[1] if len(parts) > 1 else ""}


__all__ = ["parse_ref", "REF_GRAMMAR", "is_ref"]
