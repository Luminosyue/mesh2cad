#!/usr/bin/env python3
"""Binary STL export of X-Part complete parts. No decimation, smoothing, or remesh."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import trimesh

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import CASE, STL_DIR, XPART_DIR  # noqa: E402


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def audit(mesh: trimesh.Trimesh) -> dict:
    counts = np.bincount(mesh.edges_unique_inverse) if len(mesh.faces) else np.array([])
    return {
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "watertight": bool(mesh.is_watertight),
        "boundary_edges": int(np.sum(counts == 1)) if len(counts) else 0,
        "bbox_min": mesh.bounds[0].tolist() if mesh.bounds is not None else None,
        "bbox_max": mesh.bounds[1].tolist() if mesh.bounds is not None else None,
    }


def main() -> int:
    STL_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    parts = sorted(XPART_DIR.glob("PART_*"))
    if not parts:
        print(f"No X-Part dirs in {XPART_DIR}", file=sys.stderr)
        return 1
    for part_dir in parts:
        pid = part_dir.name
        idx = int(pid.split("_")[1])
        obj = part_dir / f"complete_part_{idx:03d}.obj"
        if not obj.is_file():
            obj = part_dir / "generated_mesh.obj"
        if not obj.is_file():
            rows.append({"part_id": pid, "status": "missing_obj"})
            continue
        mesh = trimesh.load(obj, force="mesh", process=False)
        before = audit(mesh)
        stl = STL_DIR / f"{pid}.stl"
        mesh.export(stl, file_type="stl")
        after = audit(trimesh.load(stl, force="mesh", process=False))
        rows.append(
            {
                "part_id": pid,
                "status": "ok",
                "obj": str(obj),
                "stl": str(stl),
                "bytes": stl.stat().st_size,
                "before": before,
                "after": after,
                "triangle_match": before["triangles"] == after["triangles"],
            }
        )
        print(f"[stl] {pid}  {after['triangles']} tris  {stl.stat().st_size} bytes", flush=True)
    write_json(CASE / "artifacts/obj_to_stl.json", rows)
    n_ok = sum(1 for r in rows if r["status"] == "ok")
    print(f"Done {n_ok}/{len(rows)} STL")
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
