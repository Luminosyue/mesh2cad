"""Aggregate Method-B pack statistics and write cleaned scale manifests."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .constants import (
    MANIFEST_ROOT,
    OUTPUT_ROOT,
    PRIMARY_CURVE_TYPES,
    SCALE_TARGETS,
    STATS_DIR,
)


def scan_pack_root(dataset: str) -> dict:
    root = OUTPUT_ROOT / dataset
    if not root.is_dir():
        return {
            "dataset": dataset,
            "n_built": 0,
            "n_pass": 0,
            "curve_type_totals": {t: 0 for t in PRIMARY_CURVE_TYPES},
            "records": [],
        }
    records = []
    type_tot = Counter()
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        qa_path = d / "qa.json"
        meta_path = d / "metadata.json"
        if not qa_path.is_file():
            continue
        qa = json.loads(qa_path.read_text(encoding="utf-8"))
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        counts = qa.get("curve_type_counts") or {}
        for t, c in counts.items():
            type_tot[t] += int(c)
        records.append(
            {
                "sample_id": d.name,
                "qa_pass": bool(qa.get("qa_pass")),
                "edge_valid": bool(qa.get("edge_valid")),
                "num_curves": int(qa.get("num_curves", 0)),
                "non_line_curve_count": int(qa.get("non_line_curve_count", 0)),
                "curve_type_counts": counts,
                "fail_reasons": qa.get("fail_reasons", []),
                "elapsed_sec": meta.get("elapsed_sec"),
            }
        )
    passed = [r for r in records if r["qa_pass"]]
    n_curves = sum(type_tot[t] for t in PRIMARY_CURVE_TYPES) or 1
    return {
        "dataset": dataset,
        "n_built": len(records),
        "n_pass": len(passed),
        "n_edge_valid": sum(1 for r in passed if r["edge_valid"]),
        "curve_type_totals": {t: int(type_tot[t]) for t in PRIMARY_CURVE_TYPES},
        "curve_type_frac": {t: type_tot[t] / n_curves for t in PRIMARY_CURVE_TYPES},
        "sample_ids_pass": [r["sample_id"] for r in passed],
        "records": records,
    }


def _rank_for_budget(records: list[dict], n: int, seed: int) -> list[str]:
    """Prefer non-LINE diversity, then more curves, with deterministic shuffle tie-break."""
    rng = np.random.default_rng(seed)
    scored = []
    for r in records:
        if not r.get("qa_pass", True):
            continue
        counts = r.get("curve_type_counts") or {}
        rare = sum(int(counts.get(t, 0)) for t in ("CIRCLE", "ELLIPSE", "BSPLINE"))
        scored.append((rare, int(r.get("num_curves", 0)), rng.random(), r["sample_id"]))
    scored.sort(reverse=True)
    return [s[3] for s in scored[:n]]


def write_scale_manifest(scale: str, seed: int = 0) -> Path:
    targets = SCALE_TARGETS[scale]
    # DeepCAD / Fusion from harvested curve-ready manifests
    manifests = {}
    for ds in ("deepcad", "fusion360"):
        path = MANIFEST_ROOT / "manifests" / f"{ds}_curve_ready.json"
        manifests[ds] = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"records": []}

    cadfs_stats = scan_pack_root("cadfs")
    cadfs_pass = [r for r in cadfs_stats["records"] if r["qa_pass"]]

    deep_ids = _rank_for_budget(manifests["deepcad"].get("records", []), targets["deepcad"], seed)
    fus_ids = _rank_for_budget(manifests["fusion360"].get("records", []), targets["fusion360"], seed + 1)
    cadfs_ranked = _rank_for_budget(cadfs_pass, targets["cadfs_train"] + targets["cadfs_test"], seed + 2)
    cadfs_train = cadfs_ranked[: targets["cadfs_train"]]
    cadfs_test = cadfs_ranked[targets["cadfs_train"] : targets["cadfs_train"] + targets["cadfs_test"]]

    obj = {
        "scale": scale,
        "seed": seed,
        "policy": {
            "cad_budget": "50/30/20 DeepCAD/Fusion360/CADFS",
            "buckets_separate": True,
            "no_global_shuffle_mix": True,
            "cadfs_half_held_out_test": True,
            "curve_type_rebalance": "deferred_to_dataloader_sampler",
        },
        "targets": targets,
        "selected": {
            "deepcad": deep_ids,
            "fusion360": fus_ids,
            "cadfs_train": cadfs_train,
            "cadfs_test": cadfs_test,
        },
        "counts": {
            "deepcad": len(deep_ids),
            "fusion360": len(fus_ids),
            "cadfs_train": len(cadfs_train),
            "cadfs_test": len(cadfs_test),
        },
        "gaps": {
            "deepcad": max(0, targets["deepcad"] - len(deep_ids)),
            "fusion360": max(0, targets["fusion360"] - len(fus_ids)),
            "cadfs_train": max(0, targets["cadfs_train"] - len(cadfs_train)),
            "cadfs_test": max(0, targets["cadfs_test"] - len(cadfs_test)),
        },
        "notes": [
            "DeepCAD/Fusion360 ids point at ours3/curve_token_data_v1 curves.json (Method B GT already clean).",
            "CADFS ids point at cad_spatial_dataset/method_b_pack_v1/cadfs/<id>/ after rebuild.",
            "Fill gaps by expanding STEP pools / rebuilding packs before claiming 50/30/20.",
        ],
    }
    out = MANIFEST_ROOT / "manifests" / f"scale_{scale}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return out


def write_stats_report() -> Path:
    STATS_DIR.mkdir(parents=True, exist_ok=True)
    report = {"cadfs_pack": scan_pack_root("cadfs")}
    for ds in ("deepcad", "fusion360"):
        path = MANIFEST_ROOT / "manifests" / f"{ds}_curve_ready.json"
        if path.is_file():
            report[ds] = json.loads(path.read_text(encoding="utf-8"))
    out_json = STATS_DIR / "method_b_clean_stats.json"
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = ["# Method-B clean stats", ""]
    for key, block in report.items():
        if key.endswith("_pack") or key == "cadfs_pack":
            lines.append(f"## CADFS method_b_pack_v1")
            lines.append(f"- built: {block.get('n_built')}  pass: {block.get('n_pass')}")
            lines.append(f"- curve frac: {block.get('curve_type_frac')}")
        else:
            lines.append(f"## {key} (existing curve_token_data_v1)")
            lines.append(f"- pass: {block.get('n_pass')} / scanned {block.get('n_scanned')}")
            lines.append(f"- curve frac: { {k: round(v,4) for k,v in (block.get('curve_type_frac') or {}).items()} }")
        lines.append("")
    out_md = STATS_DIR / "method_b_clean_stats.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out_md


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--scale", choices=list(SCALE_TARGETS), default="overfit100")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    man = write_scale_manifest(args.scale, args.seed)
    md = write_stats_report()
    print(f"manifest -> {man}")
    print(f"stats -> {md}")


if __name__ == "__main__":
    main()
