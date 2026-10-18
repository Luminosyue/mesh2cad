#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import numpy as np
import trimesh

from common import read_csv_dicts, write_csv_dicts


FIELDS = [
    "abc_id", "triangle_count", "vertex_count", "connected_component_count",
    "is_watertight", "is_winding_consistent", "is_volume", "volume", "surface_area",
    "bbox_x", "bbox_y", "bbox_z", "degenerate_face_count", "nonfinite_vertex_count",
    "load_seconds", "load_error",
]


def audit(path: str) -> dict:
    t0 = time.time()
    mesh = trimesh.load(path, force="mesh", process=False)
    faces = np.asarray(mesh.faces)
    verts = np.asarray(mesh.vertices)
    nonfinite = int((~np.isfinite(verts)).any(axis=1).sum()) if len(verts) else 0
    deg = 0
    if len(faces):
        tri = verts[faces]
        area = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) * 0.5
        deg = int((area <= 1e-14).sum())
    try:
        comps = len(mesh.split(only_watertight=False))
    except Exception:
        comps = -1
    ext = mesh.extents if hasattr(mesh, "extents") else [0, 0, 0]
    return {
        "triangle_count": int(len(mesh.faces)),
        "vertex_count": int(len(mesh.vertices)),
        "connected_component_count": comps,
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "is_volume": bool(mesh.is_volume),
        "volume": float(mesh.volume) if np.isfinite(mesh.volume) else "",
        "surface_area": float(mesh.area) if np.isfinite(mesh.area) else "",
        "bbox_x": float(ext[0]), "bbox_y": float(ext[1]), "bbox_z": float(ext[2]),
        "degenerate_face_count": deg,
        "nonfinite_vertex_count": nonfinite,
        "load_seconds": time.time() - t0,
        "load_error": "",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="datasets/abc_hard_two_case_demo/manifests/abc_file_index.csv")
    ap.add_argument("--out", default="datasets/abc_hard_two_case_demo/audits/all_candidates_mesh_audit.csv")
    args = ap.parse_args()
    rows = []
    for r in read_csv_dicts(args.index):
        if not r.get("stl_path"):
            continue
        try:
            rows.append({"abc_id": r["abc_id"], **audit(r["stl_path"])})
            print(f"MESH_AUDIT {r['abc_id']} ok")
        except Exception as e:
            rows.append({"abc_id": r.get("abc_id", ""), **{k: "" for k in FIELDS if k != "abc_id"}, "load_error": repr(e)})
            print(f"MESH_AUDIT_FAIL {r.get('abc_id','')} {e}")
    write_csv_dicts(args.out, rows, FIELDS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
