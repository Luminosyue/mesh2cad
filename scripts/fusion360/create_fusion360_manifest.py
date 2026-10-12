#!/usr/bin/env python3
"""Create Fusion360 Reconstruction manifest from official train_test split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SPLIT = ROOT / "cad_spatial_dataset/Fusion360/reconstruction/train_test.json"
DEFAULT_RECON = ROOT / "cad_spatial_dataset/Fusion360/reconstruction/reconstruction"
DEFAULT_MANIFEST = ROOT / "cad_spatial_dataset/Fusion360/manifest_train200.json"


def create_manifest(
    num_samples: int = 200,
    split: str = "train",
    split_path: Path = DEFAULT_SPLIT,
    recon_dir: Path = DEFAULT_RECON,
    manifest_path: Path = DEFAULT_MANIFEST,
    start: int = 0,
    require_geometry: bool = True,
) -> dict:
    split_data = json.loads(split_path.read_text(encoding="utf-8"))
    candidates = list(split_data[split])[start : start + num_samples * 3]

    selected: list[str] = []
    missing: list[str] = []
    for sample_id in candidates:
        if len(selected) >= num_samples:
            break
        json_p = recon_dir / f"{sample_id}.json"
        step_p = recon_dir / f"{sample_id}.step"
        obj_p = recon_dir / f"{sample_id}.obj"
        if require_geometry and not (json_p.exists() and step_p.exists() and obj_p.exists()):
            missing.append(sample_id)
            continue
        selected.append(sample_id)

    manifest = {
        "split": split,
        "start": start,
        "requested": num_samples,
        "selected": len(selected),
        "missing_geometry": missing[:20],
        "sample_ids": selected,
        "recon_dir": str(recon_dir),
        "split_path": str(split_path),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Create Fusion360 train manifest")
    parser.add_argument("--num-samples", type=int, default=200)
    parser.add_argument("--split", type=str, default="train", choices=["train", "test"])
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--split-path", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--recon-dir", type=Path, default=DEFAULT_RECON)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args()

    report = create_manifest(
        num_samples=args.num_samples,
        split=args.split,
        split_path=args.split_path,
        recon_dir=args.recon_dir,
        manifest_path=args.manifest,
        start=args.start,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["selected"] >= args.num_samples else 2


if __name__ == "__main__":
    raise SystemExit(main())
