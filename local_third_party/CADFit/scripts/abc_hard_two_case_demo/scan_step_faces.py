#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import cadquery as cq

from common import read_csv_dicts, write_csv_dicts


FIELDS = [
    "abc_id", "chunk_id", "step_path", "step_face_count", "solid_count", "shell_count",
    "bbox_x", "bbox_y", "bbox_z", "parse_seconds",
]


def shape_stats(step_path: str) -> dict[str, float | int]:
    t0 = time.time()
    wp = cq.importers.importStep(step_path)
    vals = wp.vals() if hasattr(wp, "vals") else [wp.val()]
    faces = 0
    solids = 0
    shells = 0
    bbs = []
    for obj in vals:
        shape = obj.wrapped if hasattr(obj, "wrapped") else obj
        faces += len(obj.Faces()) if hasattr(obj, "Faces") else len(cq.Shape.cast(shape).Faces())
        solids += len(obj.Solids()) if hasattr(obj, "Solids") else len(cq.Shape.cast(shape).Solids())
        shells += len(obj.Shells()) if hasattr(obj, "Shells") else len(cq.Shape.cast(shape).Shells())
        bbs.append(obj.BoundingBox() if hasattr(obj, "BoundingBox") else cq.Shape.cast(shape).BoundingBox())
    if bbs:
        xmin = min(bb.xmin for bb in bbs); xmax = max(bb.xmax for bb in bbs)
        ymin = min(bb.ymin for bb in bbs); ymax = max(bb.ymax for bb in bbs)
        zmin = min(bb.zmin for bb in bbs); zmax = max(bb.zmax for bb in bbs)
    else:
        xmin = xmax = ymin = ymax = zmin = zmax = 0.0
    return {
        "step_face_count": faces,
        "solid_count": solids,
        "shell_count": shells,
        "bbox_x": xmax - xmin,
        "bbox_y": ymax - ymin,
        "bbox_z": zmax - zmin,
        "parse_seconds": time.time() - t0,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="datasets/abc_hard_two_case_demo/manifests/abc_file_index.csv")
    ap.add_argument("--out", default="datasets/abc_hard_two_case_demo/manifests/step_face_counts.csv")
    ap.add_argument("--failures", default="datasets/abc_hard_two_case_demo/manifests/step_parse_failures.csv")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()
    rows = read_csv_dicts(args.index)
    done = {r["abc_id"] for r in read_csv_dicts(args.out)} if args.resume else set()
    out_rows = read_csv_dicts(args.out) if args.resume else []
    fail_rows = read_csv_dicts(args.failures) if args.resume else []
    for r in rows:
        if r.get("abc_id") in done or not r.get("step_path") or r.get("step_exists") not in ("True", "true", True):
            continue
        try:
            stats = shape_stats(r["step_path"])
            out_rows.append({"abc_id": r["abc_id"], "chunk_id": r.get("chunk_id", ""), "step_path": r["step_path"], **stats})
            print(f"STEP_FACE {r['abc_id']} {stats['step_face_count']}")
        except Exception as e:
            fail_rows.append({"abc_id": r.get("abc_id", ""), "step_path": r.get("step_path", ""), "error": repr(e)})
            print(f"STEP_PARSE_FAIL {r.get('abc_id','')} {e}")
        write_csv_dicts(args.out, out_rows, FIELDS)
        write_csv_dicts(args.failures, fail_rows, ["abc_id", "step_path", "error"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
