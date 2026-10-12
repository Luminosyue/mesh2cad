#!/usr/bin/env python3
"""Freeze joint_deepcad_fusion360_v1 train/val/test (part-level, no shuffle-merge).

Rules:
  - Unit = geometry_pack_v1 sample_id (= CAD part)
  - Stratify by dataset (deepcad / fusion360)
  - Within Fusion360, also stratify freeform-STEP parts so they appear in all splits
  - Same part never crosses splits
  - Surface-valid samples included even if edge_valid=false
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from joint_target_coverage_audit import FUSION_FREEFORM_PARTS  # noqa: E402

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""


def _dsl_label(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    return "\n".join(lines).strip() + "\n"


def load_pack_rows(pack_dir: Path, dataset: str, rel_prefix: str) -> list[dict]:
    rows = []
    freeform = set(FUSION_FREEFORM_PARTS)
    for meta_path in sorted(pack_dir.glob("*/metadata.json")):
        meta = json.loads(meta_path.read_text())
        sid = meta["sample_id"]
        sample_dir = meta_path.parent
        dsl = sample_dir / "cad_target.dsl"
        surf = sample_dir / "surface_points.npy"
        if not dsl.is_file() or not surf.is_file():
            continue
        surface_valid = bool(meta.get("surface_valid", True))
        edge_valid = bool(meta.get("edge_valid", True))
        if "edge_valid" not in meta:
            # Older packs before zero-sharp contract.
            nsharp = meta.get("brep_gt_edge_sharp", {}).get("num_topo_edges_sharp")
            if nsharp is not None:
                edge_valid = int(nsharp) > 0
        if not surface_valid:
            continue
        rows.append(
            {
                "id": f"{dataset}__{sid}",
                "dataset": dataset,
                "sample_id": sid,
                "part_id": sid,
                "surface_valid": surface_valid,
                "edge_valid": edge_valid,
                "is_freeform_step": sid in freeform if dataset == "fusion360" else False,
                "pack_dir": str(sample_dir.relative_to(ROOT)),
                "point_clouds": [f"{rel_prefix}/{sid}/surface_points.npy"],
                "edge_points_gt": f"{rel_prefix}/{sid}/edge_points_gt_sharp.npy",
                "edge_points_detected": f"{rel_prefix}/{sid}/edge_points_detected.npy",
                "cad_target": f"{rel_prefix}/{sid}/cad_target.dsl",
                "conversations": [
                    {
                        "from": "human",
                        "value": f"<point_cloud>\n{CAD_INSTRUCTION.strip()}",
                    },
                    {"from": "gpt", "value": _dsl_label(dsl)},
                ],
            }
        )
    return rows


def _split_ids(ids: list[str], ratios: tuple[float, float, float], rng: random.Random):
    ids = list(ids)
    rng.shuffle(ids)
    n = len(ids)
    n_test = max(1, int(round(n * ratios[2]))) if n >= 10 else max(0, n // 10)
    n_val = max(1, int(round(n * ratios[1]))) if n >= 10 else max(0, n // 10)
    if n_test + n_val >= n:
        n_test = max(0, min(n_test, n // 5))
        n_val = max(0, min(n_val, (n - n_test) // 5))
    test = ids[:n_test]
    val = ids[n_test : n_test + n_val]
    train = ids[n_test + n_val :]
    return train, val, test


def stratified_split(rows: list[dict], seed: int, ratios=(0.8, 0.1, 0.1)):
    rng = random.Random(seed)
    by_bucket: dict[str, list[str]] = {}
    id_to_row = {r["id"]: r for r in rows}
    for r in rows:
        # Buckets: deepcad | fusion360_freeform | fusion360_analytic
        if r["dataset"] == "deepcad":
            b = "deepcad"
        elif r["is_freeform_step"]:
            b = "fusion360_freeform"
        else:
            b = "fusion360_analytic"
        by_bucket.setdefault(b, []).append(r["id"])

    assign = {}
    for b, ids in by_bucket.items():
        tr, va, te = _split_ids(ids, ratios, rng)
        for i in tr:
            assign[i] = "train"
        for i in va:
            assign[i] = "val"
        for i in te:
            assign[i] = "test"

    splits = {"train": [], "val": [], "test": []}
    for rid, sp in assign.items():
        splits[sp].append(id_to_row[rid])
    for sp in splits:
        splits[sp].sort(key=lambda r: r["id"])
    return splits, {b: len(v) for b, v in by_bucket.items()}


def summary(splits: dict, bucket_sizes: dict, seed: int, ratios) -> dict:
    def count(rows, pred):
        return sum(1 for r in rows if pred(r))

    out = {
        "name": "joint_deepcad_fusion360_v1",
        "seed": seed,
        "ratios": {"train": ratios[0], "val": ratios[1], "test": ratios[2]},
        "unit": "part_id (= geometry_pack_v1 sample_id)",
        "stratify_buckets": bucket_sizes,
        "splits": {},
    }
    for sp, rows in splits.items():
        out["splits"][sp] = {
            "n": len(rows),
            "deepcad": count(rows, lambda r: r["dataset"] == "deepcad"),
            "fusion360": count(rows, lambda r: r["dataset"] == "fusion360"),
            "fusion360_freeform_step": count(rows, lambda r: r["is_freeform_step"]),
            "surface_valid": count(rows, lambda r: r["surface_valid"]),
            "edge_valid": count(rows, lambda r: r["edge_valid"]),
            "edge_invalid": count(rows, lambda r: not r["edge_valid"]),
        }
    # Leak check
    sets = {sp: {r["part_id"] for r in rows} for sp, rows in splits.items()}
    out["part_leak_train_val"] = sorted(sets["train"] & sets["val"])
    out["part_leak_train_test"] = sorted(sets["train"] & sets["test"])
    out["part_leak_val_test"] = sorted(sets["val"] & sets["test"])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/joint_deepcad_fusion360_v1",
    )
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--train-ratio", type=float, default=0.8)
    ap.add_argument("--val-ratio", type=float, default=0.1)
    ap.add_argument("--test-ratio", type=float, default=0.1)
    args = ap.parse_args()
    ratios = (args.train_ratio, args.val_ratio, args.test_ratio)

    deep = load_pack_rows(
        ROOT / "cad_spatial_dataset/DeepCAD/geometry_pack_v1",
        "deepcad",
        "cad_spatial_dataset/DeepCAD/geometry_pack_v1",
    )
    fus = load_pack_rows(
        ROOT / "cad_spatial_dataset/Fusion360/geometry_pack_v1",
        "fusion360",
        "cad_spatial_dataset/Fusion360/geometry_pack_v1",
    )
    rows = deep + fus
    splits, bucket_sizes = stratified_split(rows, args.seed, ratios)
    summ = summary(splits, bucket_sizes, args.seed, ratios)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for sp, sp_rows in splits.items():
        (args.out_dir / f"{sp}.json").write_text(json.dumps(sp_rows, indent=2) + "\n")
    (args.out_dir / "split_summary.json").write_text(json.dumps(summ, indent=2) + "\n")

    md = [
        "# joint_deepcad_fusion360_v1",
        "",
        f"- seed = **{args.seed}**",
        f"- ratios = train/val/test = **{ratios[0]}/{ratios[1]}/{ratios[2]}**",
        f"- total = **{sum(len(v) for v in splits.values())}**",
        "",
        "| split | n | deepcad | fusion360 | freeform-STEP | edge_valid | edge_invalid |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for sp in ("train", "val", "test"):
        s = summ["splits"][sp]
        md.append(
            f"| {sp} | {s['n']} | {s['deepcad']} | {s['fusion360']} | "
            f"{s['fusion360_freeform_step']} | {s['edge_valid']} | {s['edge_invalid']} |"
        )
    md += [
        "",
        "Part-level: no `part_id` appears in more than one split.",
        "Surface-only J0 should use all `surface_valid` rows (includes edge_invalid).",
        "",
    ]
    (args.out_dir / "README.md").write_text("\n".join(md) + "\n")
    print(json.dumps(summ, indent=2))
    print(f"wrote {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
