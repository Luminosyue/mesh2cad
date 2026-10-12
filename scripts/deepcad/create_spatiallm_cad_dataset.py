#!/usr/bin/env python3
"""Build ShareGPT JSON for SpatialLM CAD DSL SFT (step 4).

Each record (canonical contract):
  point_cloud → features_canonical.npy (or 6-ch baseline variant)
  instruction → "Generate CAD program"
  output      → program_canonical.dsl text

Offline T is stored in coordinate_transform.json; mm_plugin must not re-scale.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""

POINT_CLOUD_PLACEHOLDER = "<point_cloud>"


def _sample_ids_from_manifest(manifest: Path) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return [sid.replace("/", "_") for sid in data.get("sample_ids", [])]


def _is_complete(sample_dir: Path, *, use_canonical: bool = True) -> bool:
    if use_canonical:
        required = (
            "features_canonical.npy",
            "program_canonical.dsl",
            "coordinate_transform.json",
            "meta.json",
        )
    else:
        required = ("features.npy", "program.dsl", "meta.json")
    return all((sample_dir / f).exists() for f in required)


def _load_dsl_label(dsl_path: Path) -> str:
    text = dsl_path.read_text(encoding="utf-8").strip()
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("#")]
    return "\n".join(lines).strip() + "\n"


def build_records(
    train_dir: Path,
    sample_ids: list[str],
    variant: str,
    *,
    use_canonical: bool = True,
) -> list[dict]:
    """variant: baseline | edge_zero | edge_shuffle | ours (real Dora edge)."""
    variant_paths = {
        "baseline": ("features_canonical_xyz_normal.npy", 6),
        "edge_zero": ("features_canonical_edge_zero.npy", 7),
        "edge_shuffle": ("features_canonical_edge_shuffle.npy", 7),
        "ours": ("features_canonical.npy", 7),
        "edge_real": ("features_canonical.npy", 7),
    }
    if variant not in variant_paths:
        raise ValueError(f"unknown variant {variant!r}; expected one of {list(variant_paths)}")

    fname, n_ch = variant_paths[variant]
    records = []
    for sid in sample_ids:
        sample_dir = train_dir / sid
        if not _is_complete(sample_dir, use_canonical=use_canonical):
            continue

        if use_canonical:
            pc_abs = sample_dir / fname
            if variant == "baseline" and not pc_abs.exists():
                import numpy as np

                feats = np.load(sample_dir / "features_canonical.npy")
                np.save(pc_abs, feats[:, :6].astype(np.float32))
            pc_rel = f"train/{sid}/{fname}"
            dsl_path = sample_dir / "program_canonical.dsl"
        else:
            legacy = {
                "baseline": "features_xyz_normal.npy",
                "ours": "features.npy",
                "edge_real": "features.npy",
            }
            pc_abs = sample_dir / legacy.get(variant, "features.npy")
            pc_rel = f"train/{sid}/{pc_abs.name}"
            dsl_path = sample_dir / "program.dsl"

        if not pc_abs.exists():
            continue
        feats = __import__("numpy").load(pc_abs)
        if feats.shape[1] != n_ch:
            continue

        dsl_label = _load_dsl_label(dsl_path)
        records.append(
            {
                "id": sid,
                "conversations": [
                    {
                        "from": "human",
                        "value": f"{POINT_CLOUD_PLACEHOLDER}\n{CAD_INSTRUCTION.strip()}",
                    },
                    {"from": "gpt", "value": dsl_label},
                ],
                "point_clouds": [pc_rel],
            }
        )
    return records


def write_dataset_info(
    dataset_dir: Path, train_name: str, val_name: str | None = None, test_name: str | None = None
) -> None:
    info = {
        train_name: {
            "file_name": f"{train_name}.json",
            "formatting": "sharegpt",
            "columns": {
                "messages": "conversations",
                "point_clouds": "point_clouds",
            },
        },
    }
    if val_name:
        info[val_name] = {
            "file_name": f"{val_name}.json",
            "formatting": "sharegpt",
            "columns": {
                "messages": "conversations",
                "point_clouds": "point_clouds",
            },
        }
    if test_name:
        info[test_name] = {
            "file_name": f"{test_name}.json",
            "formatting": "sharegpt",
            "columns": {
                "messages": "conversations",
                "point_clouds": "point_clouds",
            },
        }
    path = dataset_dir / "dataset_info.json"
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing.update(info)
        info = existing
    path.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create SpatialLM CAD ShareGPT dataset")
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/train",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/manifest_train100.json",
    )
    parser.add_argument("--limit", type=int, default=None, help="Max samples (e.g. 10 for overfit)")
    parser.add_argument(
        "--variant",
        choices=("ours", "baseline", "edge_zero", "edge_shuffle", "edge_real"),
        default="ours",
        help="baseline=6ch; edge_zero/shuffle/real=7ch canonical ablation; ours=real",
    )
    parser.add_argument("--val-ratio", type=float, default=0.0, help="Hold-out fraction")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--name-suffix",
        type=str,
        default="",
        help="Suffix for dataset name, e.g. overfit10",
    )
    parser.add_argument(
        "--no-canonical",
        action="store_true",
        help="Use source features.npy + program.dsl (legacy desynced path; not recommended)",
    )
    parser.add_argument(
        "--split-json",
        type=Path,
        default=None,
        help="Reuse train_ids/val_ids from split JSON (e.g. split_train100_seed42.json)",
    )
    args = parser.parse_args()

    sample_ids = _sample_ids_from_manifest(args.manifest)
    if args.limit is not None:
        sample_ids = sample_ids[: args.limit]

    use_canonical = not args.no_canonical
    records = build_records(
        args.train_dir, sample_ids, args.variant, use_canonical=use_canonical
    )
    if not records:
        print("No complete samples found.")
        return 1

    rng = random.Random(args.seed)
    fixed_train: set[str] | None = None
    fixed_val: set[str] | None = None
    fixed_test: set[str] | None = None
    if args.split_json and args.split_json.exists():
        split = json.loads(args.split_json.read_text(encoding="utf-8"))
        fixed_train = set(split["train_ids"])
        fixed_val = set(split.get("val_ids") or [])
        fixed_test = set(split.get("test_ids") or [])
        by_id = {r["id"]: r for r in records}
        train_records = [by_id[sid] for sid in split["train_ids"] if sid in by_id]
        val_records = [by_id[sid] for sid in split.get("val_ids") or [] if sid in by_id]
        test_records = [by_id[sid] for sid in split.get("test_ids") or [] if sid in by_id]
    elif args.val_ratio > 0 and len(records) > 1:
        rng.shuffle(records)
        n_val = max(1, int(len(records) * args.val_ratio))
        val_records = records[:n_val]
        train_records = records[n_val:]
        test_records = []
    else:
        train_records = records
        val_records = []
        test_records = []

    suffix = f"_{args.name_suffix}" if args.name_suffix else ""
    variant_tag = {
        "baseline": "baseline",
        "ours": "ours",
        "edge_real": "ours",
        "edge_zero": "edge_zero",
        "edge_shuffle": "edge_shuffle",
    }[args.variant]
    train_name = f"deepcad_cad_{variant_tag}{suffix}_train"
    train_path = args.output_dir / f"{train_name}.json"
    train_path.write_text(json.dumps(train_records, indent=2) + "\n", encoding="utf-8")

    val_name = None
    if val_records:
        val_name = f"deepcad_cad_{variant_tag}{suffix}_val"
        val_path = args.output_dir / f"{val_name}.json"
        val_path.write_text(json.dumps(val_records, indent=2) + "\n", encoding="utf-8")

    test_name = None
    if test_records:
        test_name = f"deepcad_cad_{variant_tag}{suffix}_test"
        test_path = args.output_dir / f"{test_name}.json"
        test_path.write_text(json.dumps(test_records, indent=2) + "\n", encoding="utf-8")

    # Persist split for ablation reproducibility
    if val_records and args.name_suffix and not fixed_train:
        split_path = args.output_dir / f"split_{args.name_suffix}_seed{args.seed}.json"
        split_path.write_text(
            json.dumps(
                {
                    "seed": args.seed,
                    "val_ratio": args.val_ratio,
                    "variant": args.variant,
                    "train_ids": [r["id"] for r in train_records],
                    "val_ids": [r["id"] for r in val_records],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    write_dataset_info(args.output_dir, train_name, val_name, test_name)

    print(json.dumps({
        "train": len(train_records),
        "val": len(val_records),
        "test": len(test_records),
        "variant": args.variant,
        "use_canonical": use_canonical,
        "train_file": str(train_path),
        "dataset_name": train_name,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
