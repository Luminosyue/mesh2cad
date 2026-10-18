#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import is_hard_face_count, link_or_copy, read_csv_dicts, write_csv_dicts


FIELDS = [
    "case_name", "abc_id", "chunk_id", "step_face_count", "triangle_count", "vertex_count",
    "connected_component_count", "is_watertight", "source_step", "source_stl",
    "selection_reason", "step_sha256", "stl_sha256",
]


def truth(v: str) -> bool:
    return str(v).lower() in {"true", "1", "yes"}


def score(row: dict, target_min: int, target_max: int, fallback_min: int, fallback_max: int) -> tuple:
    fc = int(row["step_face_count"])
    tri = int(float(row.get("triangle_count") or 0))
    wat = 1 if truth(row.get("is_watertight", "")) else 0
    one = 1 if str(row.get("connected_component_count", "")) == "1" else 0
    in_target = target_min <= fc <= target_max
    in_fallback = fallback_min <= fc <= fallback_max
    target_mid = (target_min + target_max) / 2
    return (1 if in_target else 0, 1 if in_fallback else 0, wat, one, tri, -abs(fc - target_mid))


def merged_rows(index_path: Path, faces_path: Path, mesh_path: Path) -> list[dict]:
    idx = {r["abc_id"]: r for r in read_csv_dicts(index_path)}
    mesh = {r["abc_id"]: r for r in read_csv_dicts(mesh_path)}
    rows = []
    for f in read_csv_dicts(faces_path):
        abc_id = f["abc_id"]
        if abc_id not in idx or abc_id not in mesh:
            continue
        r = {**idx[abc_id], **f, **mesh[abc_id]}
        try:
            fc = int(r["step_face_count"])
            tri = int(float(r.get("triangle_count") or 0))
            deg = int(float(r.get("degenerate_face_count") or 0))
        except Exception:
            continue
        if not is_hard_face_count(fc):
            continue
        if not r.get("step_path") or not r.get("stl_path"):
            continue
        if tri <= 0 or deg >= tri:
            continue
        rows.append(r)
    return rows


def choose(rows: list[dict]) -> tuple[dict, dict]:
    usable = [r for r in rows if truth(r.get("is_watertight", ""))]
    if len(usable) < 2:
        usable = rows
    a_sorted = sorted(usable, key=lambda r: score(r, 200, 400, 151, 500), reverse=True)
    case_a = a_sorted[0]
    b_pool = [r for r in usable if r["abc_id"] != case_a["abc_id"]]
    b_sorted = sorted(b_pool, key=lambda r: score(r, 800, 1500, 600, 1500), reverse=True)
    if not b_sorted:
        raise RuntimeError("No non-duplicate Case B candidate")
    return case_a, b_sorted[0]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="datasets/abc_hard_two_case_demo/manifests/abc_file_index.csv")
    ap.add_argument("--faces", default="datasets/abc_hard_two_case_demo/manifests/step_face_counts.csv")
    ap.add_argument("--mesh-audit", default="datasets/abc_hard_two_case_demo/audits/all_candidates_mesh_audit.csv")
    ap.add_argument("--out", default="datasets/abc_hard_two_case_demo/manifests/selected_two_cases.csv")
    args = ap.parse_args()
    rows = merged_rows(Path(args.index), Path(args.faces), Path(args.mesh_audit))
    if len(rows) < 2:
        raise SystemExit("Not enough valid Hard candidates")
    a, b = choose(rows)
    selected = []
    for name, row, reason in [
        ("case_a", a, "STEP faces prioritized 200-400, high STL triangle count, watertight preferred"),
        ("case_b", b, "STEP faces prioritized 800-1500, high STL triangle count, watertight preferred"),
    ]:
        selected.append({
            "case_name": name,
            "abc_id": row["abc_id"],
            "chunk_id": row.get("chunk_id", ""),
            "step_face_count": row["step_face_count"],
            "triangle_count": row.get("triangle_count", ""),
            "vertex_count": row.get("vertex_count", ""),
            "connected_component_count": row.get("connected_component_count", ""),
            "is_watertight": row.get("is_watertight", ""),
            "source_step": row.get("step_path", ""),
            "source_stl": row.get("stl_path", ""),
            "selection_reason": reason,
            "step_sha256": row.get("step_sha256", ""),
            "stl_sha256": row.get("stl_sha256", ""),
        })
        link_or_copy(row["stl_path"], f"datasets/abc_hard_two_case_demo/selected/{name}_input_high_mesh.stl")
    write_csv_dicts(args.out, selected, FIELDS)
    for r in selected:
        print(f"{r['case_name'].upper()}_ID={r['abc_id']}")
        print(f"{r['case_name'].upper()}_STEP_FACES={r['step_face_count']}")
        print(f"{r['case_name'].upper()}_TRIANGLES={r['triangle_count']}")
        print(f"{r['case_name'].upper()}_WATERTIGHT={r['is_watertight']}")
    print(f"HARD_CANDIDATES={len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
