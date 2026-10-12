from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import trimesh


def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(str(path), force="mesh", process=False)


def bbox_diag(verts) -> float:
    import numpy as np

    v = np.asarray(verts, dtype=float)
    return float(np.linalg.norm(v.max(0) - v.min(0)))
