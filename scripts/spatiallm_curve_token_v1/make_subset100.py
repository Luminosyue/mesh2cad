#!/usr/bin/env python3
"""Step 4: carve a 100-CAD overfit subset out of joint_deepcad_fusion360_v1.

80 DeepCAD + 20 Fusion360, drawn from the existing joint ShareGPT records so the
prompts and DSL targets are byte-identical to J0/J2. A CAD is only eligible when
it has surface points, sharp edge points, and exported Curve Tokens, so all three
arms see exactly the same 100 CADs.

Train and eval use the SAME rows on purpose: the goal is to confirm the model can
overfit and that the Curve Token stream is actually used, not to measure
generalization.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from spatiallm_curve_token_v1.config import (  # noqa: E402
    CURVE_DATA_ROOT,
    JOINT_DATASET_DIR,
    PACK_ROOT,
    SCHEMA_VERSION,
    SUBSET_DIR,
    SUBSET_N_DEEPCAD,
    SUBSET_N_FUSION360,
    SUBSET_SEED,
)

CURVE_SPLIT_DIR = {"deepcad": "deepcad_train", "fusion360": "fusion360_train"}


def eligible(row: dict) -> bool:
    ds, sid = row["dataset"], row["sample_id"]
    pack = PACK_ROOT[ds] / sid
    curve = CURVE_DATA_ROOT / CURVE_SPLIT_DIR[ds] / sid
    return (
        row.get("surface_valid", False)
        and row.get("edge_valid", False)
        and (pack / "surface_points.npy").is_file()
        and (pack / "edge_points_gt_sharp.npy").is_file()
        and (pack / "brep_edges.json").is_file()
        and (curve / "curve_samples.npz").is_file()
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seed", type=int, default=SUBSET_SEED)
    args = ap.parse_args()

    src = JOINT_DATASET_DIR / "joint_j0j2_v1_train.json"
    rows = json.loads(src.read_text(encoding="utf-8"))
    pools: dict[str, list[dict]] = {"deepcad": [], "fusion360": []}
    for r in rows:
        if r["dataset"] in pools and eligible(r):
            pools[r["dataset"]].append(r)

    rng = random.Random(args.seed)
    picked: list[dict] = []
    wanted = {"deepcad": SUBSET_N_DEEPCAD, "fusion360": SUBSET_N_FUSION360}
    for ds, n in wanted.items():
        pool = sorted(pools[ds], key=lambda r: r["id"])
        if len(pool) < n:
            raise SystemExit(f"only {len(pool)} eligible {ds} CADs, need {n}")
        picked.extend(rng.sample(pool, n))
    picked.sort(key=lambda r: r["id"])

    SUBSET_DIR.mkdir(parents=True, exist_ok=True)
    train_path = SUBSET_DIR / "curve100_train.json"
    train_path.write_text(json.dumps(picked, indent=1) + "\n", encoding="utf-8")

    info = {
        f"curve100_{split}": {
            "file_name": "curve100_train.json",
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "point_clouds": "point_clouds"},
        }
        for split in ("train", "eval")
    }
    (SUBSET_DIR / "dataset_info.json").write_text(
        json.dumps(info, indent=2) + "\n", encoding="utf-8"
    )

    ids = [{"dataset": r["dataset"], "sample_id": r["sample_id"],
            "cad_dir": f"{CURVE_SPLIT_DIR[r['dataset']]}/{r['sample_id']}"}
           for r in picked]
    (SUBSET_DIR / "curve100_ids.json").write_text(
        json.dumps(ids, indent=1) + "\n", encoding="utf-8"
    )

    meta = {
        "schema_version": SCHEMA_VERSION,
        "source": str(src.relative_to(ROOT)),
        "seed": args.seed,
        "eligible_pool": {k: len(v) for k, v in pools.items()},
        "picked": {k: sum(1 for r in picked if r["dataset"] == k) for k in pools},
        "n_total": len(picked),
        "note": "train == eval on purpose (overfit probe, not a generalization test)",
    }
    (SUBSET_DIR / "subset_meta.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(meta, indent=2))
    print(f"[subset] wrote {train_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
