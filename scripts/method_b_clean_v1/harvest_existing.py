"""Harvest already-clean Method-B curve packs for DeepCAD / Fusion360."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .constants import MANIFEST_ROOT, PRIMARY_CURVE_TYPES, SOURCE_ROOTS


def harvest_curve_ready(dataset: str) -> list[dict]:
    cfg = SOURCE_ROOTS[dataset]
    root: Path = cfg["curve_ready"]
    if root is None or not root.is_dir():
        return []
    out = []
    for d in sorted(p for p in root.iterdir() if p.is_dir()):
        cj = d / "curves.json"
        if not cj.is_file():
            continue
        data = json.loads(cj.read_text(encoding="utf-8"))
        counts = data.get("curve_type_counts") or {}
        if not counts and data.get("curves"):
            counts = {}
            for c in data["curves"]:
                t = c.get("curve_type", "OTHER")
                counts[t] = counts.get(t, 0) + 1
        primary = sum(int(counts.get(t, 0)) for t in PRIMARY_CURVE_TYPES)
        non_line = primary - int(counts.get("LINE", 0))
        step = cfg["step_root"] / d.name / cfg["step_name"]
        out.append(
            {
                "sample_id": d.name,
                "dataset": dataset,
                "curves_path": str(cj),
                "step_path": str(step) if step.is_file() else None,
                "has_step": step.is_file(),
                "num_curves": int(data.get("num_curves", primary)),
                "curve_type_counts": counts,
                "primary_curve_count": int(primary),
                "non_line_curve_count": int(non_line),
                "qa_pass": primary > 0 and step.is_file(),
            }
        )
    return out


def write_harvest(dataset: str, out_path: Path | None = None) -> Path:
    records = harvest_curve_ready(dataset)
    passed = [r for r in records if r["qa_pass"]]
    out_path = out_path or (MANIFEST_ROOT / "manifests" / f"{dataset}_curve_ready.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    type_tot = {t: 0 for t in PRIMARY_CURVE_TYPES}
    for r in passed:
        for t in PRIMARY_CURVE_TYPES:
            type_tot[t] += int(r["curve_type_counts"].get(t, 0))
    n_curves = sum(type_tot.values()) or 1
    obj = {
        "dataset": dataset,
        "role": SOURCE_ROOTS[dataset]["role"],
        "budget_frac": SOURCE_ROOTS[dataset]["budget_frac"],
        "n_scanned": len(records),
        "n_pass": len(passed),
        "curve_type_totals": type_tot,
        "curve_type_frac": {t: type_tot[t] / n_curves for t in PRIMARY_CURVE_TYPES},
        "sample_ids": [r["sample_id"] for r in passed],
        "records": passed,
    }
    out_path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", choices=["deepcad", "fusion360", "both"], default="both")
    args = ap.parse_args()
    ds = ["deepcad", "fusion360"] if args.dataset == "both" else [args.dataset]
    for d in ds:
        path = write_harvest(d)
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"{d}: pass={data['n_pass']}/{data['n_scanned']} -> {path}")
        print(f"  curve frac: { {k: round(v,4) for k,v in data['curve_type_frac'].items()} }")


if __name__ == "__main__":
    main()
