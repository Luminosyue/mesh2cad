"""CAD-level (family-aware) train/val/test splits for Curve Encoder V1.

Rules:
  - Never split by curve. All edges of one CAD stay in one split.
  - Fusion360 CADs that share the same (project, hash) family stay together.
  - Stratify so rare types (ELLIPSE, BSPLINE) appear in every split when possible.
"""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

from .config import (
    CURVE_TYPES,
    DATA_ROOT,
    SPLIT_RATIOS,
    SPLIT_SEED,
    SPLITS_DATA,
    SPLITS_DIR,
)


def _family_key(split: str, cad_id: str) -> str:
    if split.startswith("fusion360"):
        toks = cad_id.split("_")
        if len(toks) >= 2:
            return f"f360:{toks[0]}_{toks[1]}"
    return f"{split}:{cad_id}"


def _cad_type_flags(cad_dir: Path) -> dict[str, bool]:
    meta_path = cad_dir / "metadata.json"
    curves_path = cad_dir / "curves.json"
    counts = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        counts = meta.get("curve_type_counts") or {}
    if not counts and curves_path.is_file():
        counts = json.loads(curves_path.read_text()).get("curve_type_counts") or {}
    return {t: int(counts.get(t, 0)) > 0 for t in CURVE_TYPES}


def discover_cads() -> list[dict]:
    rows = []
    for split in SPLITS_DATA:
        root = DATA_ROOT / split
        if not root.is_dir():
            continue
        for d in sorted(p for p in root.iterdir() if p.is_dir()):
            if not (d / "curve_samples.npz").is_file():
                continue
            flags = _cad_type_flags(d)
            rows.append(
                {
                    "split_source": split,
                    "cad_id": d.name,
                    "path": str(d),
                    "family": _family_key(split, d.name),
                    "has_ellipse": flags["ELLIPSE"],
                    "has_bspline": flags["BSPLINE"],
                    "has_circle": flags["CIRCLE"],
                }
            )
    return rows


def assign_splits(cads: list[dict], seed: int = SPLIT_SEED) -> dict:
    """Assign each family to train/val/test with rare-type coverage."""
    rng = random.Random(seed)
    families: dict[str, list[dict]] = defaultdict(list)
    for c in cads:
        families[c["family"]].append(c)

    # Priority buckets: families that carry rare types go first so every split
    # gets at least one when the pool is large enough.
    fam_list = list(families.keys())
    rng.shuffle(fam_list)

    n = len(fam_list)
    n_test = max(1, int(round(n * SPLIT_RATIOS["test"])))
    n_val = max(1, int(round(n * SPLIT_RATIOS["val"])))
    # Round-robin rare families (ELLIPSE / BSPLINE only) into test/val/train.
    # Do NOT prefer CIRCLE here — that previously saturated val/test with CIRCLE CADs.
    assignment: dict[str, str] = {}
    buckets = {"test": [], "val": [], "train": []}
    cycle = ["test", "val", "train"]
    rare = [f for f in fam_list if any(m["has_ellipse"] or m["has_bspline"] for m in families[f])]
    common = [f for f in fam_list if f not in set(rare)]
    rng.shuffle(rare)
    rng.shuffle(common)
    for i, f in enumerate(rare):
        buckets[cycle[i % 3]].append(f)
    # Fill remaining quotas from common families (random order).
    need = {
        "test": max(0, n_test - len(buckets["test"])),
        "val": max(0, n_val - len(buckets["val"])),
        "train": 10**9,
    }
    for f in common:
        for name in ("test", "val", "train"):
            if need[name] > 0:
                buckets[name].append(f)
                need[name] -= 1
                break

    for name, flist in buckets.items():
        for f in flist:
            assignment[f] = name

    cad_rows = []
    counts = {"train": 0, "val": 0, "test": 0}
    for f, members in families.items():
        sp = assignment[f]
        for m in members:
            row = dict(m)
            row["encoder_split"] = sp
            cad_rows.append(row)
            counts[sp] += 1

    type_cov = {s: {t: 0 for t in CURVE_TYPES} for s in counts}
    for row in cad_rows:
        sp = row["encoder_split"]
        flags = _cad_type_flags(Path(row["path"]))
        for t, present in flags.items():
            if present:
                type_cov[sp][t] += 1

    return {
        "schema_version": "curve_encoder_split_v1",
        "seed": seed,
        "ratios": SPLIT_RATIOS,
        "n_families": len(families),
        "n_cads": len(cad_rows),
        "cad_counts": counts,
        "type_coverage_cads": type_cov,
        "cads": cad_rows,
    }


def write_splits(manifest: dict) -> Path:
    SPLITS_DIR.mkdir(parents=True, exist_ok=True)
    path = SPLITS_DIR / "cad_level_splits.json"
    path.write_text(json.dumps(manifest, indent=2))
    # Also emit plain id lists for convenience.
    for sp in ("train", "val", "test"):
        ids = [f"{c['split_source']}/{c['cad_id']}" for c in manifest["cads"] if c["encoder_split"] == sp]
        (SPLITS_DIR / f"{sp}_cads.txt").write_text("\n".join(ids) + "\n")
    md = SPLITS_DIR / "split_report.md"
    tc = manifest["type_coverage_cads"]
    lines = [
        "# CAD-level encoder splits",
        "",
        f"- seed: {manifest['seed']}",
        f"- families: {manifest['n_families']}",
        f"- CADs: {manifest['n_cads']}",
        f"- counts: {manifest['cad_counts']}",
        "",
        "## Type coverage (CADs containing type)",
        "",
        "| split | LINE | CIRCLE | ELLIPSE | BSPLINE |",
        "|---|---|---|---|---|",
    ]
    for sp in ("train", "val", "test"):
        lines.append(
            f"| {sp} | {tc[sp]['LINE']} | {tc[sp]['CIRCLE']} | {tc[sp]['ELLIPSE']} | {tc[sp]['BSPLINE']} |"
        )
    lines.append("")
    lines.append("Split unit is CAD (Fusion360: family = project_hash). Curves are never split across sets.")
    md.write_text("\n".join(lines) + "\n")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SPLIT_SEED)
    args = ap.parse_args()
    cads = discover_cads()
    manifest = assign_splits(cads, seed=args.seed)
    path = write_splits(manifest)
    print(json.dumps({"wrote": str(path), "cad_counts": manifest["cad_counts"],
                      "type_coverage_cads": manifest["type_coverage_cads"]}, indent=2))


if __name__ == "__main__":
    main()
