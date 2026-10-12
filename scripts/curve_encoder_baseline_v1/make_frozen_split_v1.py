#!/usr/bin/env python3
"""Freeze CAD-level split frozen_v1 from joint_deepcad_fusion360_v1.

Val/test stay at the real CAD distribution. No curve-level reshuffle.
Only writes under ours3/curve_encoder_baseline_v1/splits/frozen_v1/.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parents[1]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from curve_encoder_baseline_v1.config import (  # noqa: E402
    CURVE_DATA_ROOT,
    DATASET_TO_CURVE_SPLIT,
    JOINT_SPLIT_ROOT,
    PRIMARY_TYPES,
    SCHEMA_VERSION,
    SPLIT_DIR,
    SPLIT_NAME,
    SPLIT_SOURCE,
    TYPE_TO_ID,
)


def _load_joint(split: str) -> list[dict]:
    rows = json.loads((JOINT_SPLIT_ROOT / f"{split}.json").read_text(encoding="utf-8"))
    out = []
    for r in rows:
        ds = str(r["dataset"]).lower()
        sid = r["sample_id"]
        curve_split = DATASET_TO_CURVE_SPLIT[ds]
        cad_dir = CURVE_DATA_ROOT / curve_split / sid
        npz = cad_dir / "curve_samples.npz"
        curves = cad_dir / "curves.json"
        if not npz.is_file() or not curves.is_file():
            raise FileNotFoundError(f"missing curve pack for {ds}/{sid}: {cad_dir}")
        out.append(
            {
                "id": r["id"],
                "dataset": ds,
                "sample_id": sid,
                "curve_split": curve_split,
                "cad_dir": f"{curve_split}/{sid}",
            }
        )
    return out


def _type_hist(rows: list[dict]) -> dict[str, int]:
    counts = Counter({t: 0 for t in PRIMARY_TYPES})
    import numpy as np

    for r in rows:
        z = np.load(CURVE_DATA_ROOT / r["cad_dir"] / "curve_samples.npz")
        tids = z["curve_type_id"]
        for tid in tids.tolist():
            name = next((k for k, v in TYPE_TO_ID.items() if v == int(tid)), None)
            if name in counts:
                counts[name] += 1
    return dict(counts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--with-type-hist", action="store_true", help="count curve types (slow)")
    args = ap.parse_args()

    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    splits = {}
    for name in ("train", "val", "test"):
        rows = _load_joint(name)
        dest = SPLIT_DIR / f"{name}.json"
        dest.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        entry = {"n_cad": len(rows), "path": str(dest.relative_to(SPLIT_DIR.parent.parent))}
        if args.with_type_hist:
            entry["curve_type_counts"] = _type_hist(rows)
        splits[name] = entry
        print(f"[frozen_v1] {name}: {len(rows)} CAD → {dest}")

    # leak check
    ids = {s: {r["id"] for r in _load_joint(s)} for s in ("train", "val", "test")}
    leaks = {
        "train_val": sorted(ids["train"] & ids["val"]),
        "train_test": sorted(ids["train"] & ids["test"]),
        "val_test": sorted(ids["val"] & ids["test"]),
    }
    if any(leaks.values()):
        raise RuntimeError(f"CAD leak across splits: {leaks}")

    meta = {
        "schema_version": SCHEMA_VERSION,
        "split_name": SPLIT_NAME,
        "source": SPLIT_SOURCE,
        "source_dir": str(JOINT_SPLIT_ROOT),
        "curve_data_root": str(CURVE_DATA_ROOT),
        "unit": "CAD / part_id (= sample_id)",
        "note": (
            "CAD-level freeze of joint_deepcad_fusion360_v1. "
            "Train may use type-aware curve sampling; val/test keep natural CAD curve mix."
        ),
        "splits": splits,
        "leaks": leaks,
    }
    (SPLIT_DIR / "manifest.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "manifest": str(SPLIT_DIR / "manifest.json"), **{k: v["n_cad"] for k, v in splits.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
