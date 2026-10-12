"""Deterministic hashing / JSON IO for V4."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_dsl_text(code: str) -> str:
    """Strip comments / blank lines / redundant whitespace; keep token order."""
    lines: list[str] = []
    for raw in code.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(r"\s+", " ", s)
        s = s.replace(" = ", "=").replace("= ", "=").replace(" =", "=")
        s = s.replace(", ", ",").replace("( ", "(").replace(" )", ")")
        lines.append(s)
    return "\n".join(lines) + ("\n" if lines else "")


def canonical_dsl_sha256(code: str) -> str:
    return sha256_text(canonical_dsl_text(code))


def write_json(path: Path, obj: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str, sort_keys=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, default=str, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def file_manifest_entry(path: Path) -> dict:
    p = Path(path)
    if not p.exists():
        return {"path": str(p), "exists": False, "sha256": None, "nbytes": 0}
    return {
        "path": str(p),
        "exists": True,
        "sha256": sha256_file(p),
        "nbytes": p.stat().st_size,
    }
