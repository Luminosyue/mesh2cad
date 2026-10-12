#!/usr/bin/env python3
"""Export joint_deepcad_fusion360_v1 ShareGPT records for SpatialLM J0/J2.

J0 and J2 share the same JSON: point_clouds -> surface_points.npy.
J2's mm_plugin then loads edge_points_gt_sharp.npy from the same folder.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JOINT = ROOT / "cad_spatial_dataset/joint_deepcad_fusion360_v1"
MEDIA_ROOT = ROOT / "cad_spatial_dataset"
PREFIX = "cad_spatial_dataset/"


def to_media_rel(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith(PREFIX):
        return p[len(PREFIX) :]
    if p.startswith("DeepCAD/") or p.startswith("Fusion360/"):
        return p
    raise ValueError(f"unexpected pack path: {path}")


def slim_record(row: dict) -> dict:
    pc = row["point_clouds"]
    if not isinstance(pc, list) or len(pc) != 1:
        raise ValueError(f"{row.get('id')} bad point_clouds: {pc!r}")
    rel = to_media_rel(pc[0])
    abs_path = MEDIA_ROOT / rel
    if not abs_path.is_file():
        raise FileNotFoundError(abs_path)
    edge_sharp = abs_path.parent / "edge_points_gt_sharp.npy"
    dsl = abs_path.parent / "cad_target.dsl"
    if not edge_sharp.is_file():
        raise FileNotFoundError(edge_sharp)
    if not dsl.is_file():
        raise FileNotFoundError(dsl)
    return {
        "id": row["id"],
        "dataset": row.get("dataset"),
        "sample_id": row.get("sample_id"),
        "surface_valid": row.get("surface_valid", True),
        "edge_valid": row.get("edge_valid", True),
        "is_freeform_step": row.get("is_freeform_step", False),
        "conversations": row["conversations"],
        "point_clouds": [rel],
    }


def update_dataset_info(names: list[str]) -> None:
    path = JOINT / "dataset_info.json"
    info = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    for name in names:
        info[name] = {
            "file_name": f"{name}.json",
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "point_clouds": "point_clouds"},
        }
    path.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--joint-dir", type=Path, default=JOINT)
    args = ap.parse_args()

    written = {}
    names = []
    for split in ("train", "val", "test"):
        src = args.joint_dir / f"{split}.json"
        rows = json.loads(src.read_text(encoding="utf-8"))
        records = [slim_record(r) for r in rows]
        name = f"joint_j0j2_v1_{split}"
        dest = args.joint_dir / f"{name}.json"
        dest.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
        names.append(name)
        n_dc = sum(1 for r in records if r.get("dataset") == "deepcad")
        n_fu = sum(1 for r in records if r.get("dataset") == "fusion360")
        n_edge_bad = sum(1 for r in records if not r.get("edge_valid"))
        written[split] = {
            "n": len(records),
            "deepcad": n_dc,
            "fusion360": n_fu,
            "edge_invalid": n_edge_bad,
            "file": str(dest),
        }

    update_dataset_info(names)
    print(json.dumps({"written": written, "dataset_info": names}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
