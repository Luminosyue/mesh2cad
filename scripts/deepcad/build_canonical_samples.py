#!/usr/bin/env python3
"""Build canonical features/DSL/transform for DeepCAD samples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cad_canonical import DEFAULT_TARGET_DIAGONAL, build_sample_canonical  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CAD canonical artifacts")
    parser.add_argument(
        "--train-dir",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/train",
    )
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--target-diagonal", type=float, default=DEFAULT_TARGET_DIAGONAL)
    parser.add_argument(
        "--out-report",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/canonical_build_report.json",
    )
    args = parser.parse_args()

    if args.manifest and args.manifest.exists():
        ids = [
            sid.replace("/", "_")
            for sid in json.loads(args.manifest.read_text())["sample_ids"]
        ]
        dirs = [args.train_dir / sid for sid in ids if (args.train_dir / sid).is_dir()]
    else:
        dirs = sorted(p for p in args.train_dir.iterdir() if p.is_dir())

    reports = []
    errors = []
    for i, d in enumerate(dirs):
        if args.limit is not None and i >= args.limit:
            break
        if not (d / "features.npy").exists() or not (d / "program.dsl").exists():
            continue
        try:
            rep = build_sample_canonical(d, target_diagonal=args.target_diagonal)
            reports.append(rep)
            print(
                f"ok {rep['sample_id']} scale={rep['scale']:.4f} "
                f"diag={rep['canonical_diagonal']:.4f} min={rep['canonical_min']}"
            )
        except Exception as e:
            errors.append({"sample_id": d.name, "error": str(e)})
            print(f"FAIL {d.name}: {e}", flush=True)

    out = {
        "n_ok": len(reports),
        "n_fail": len(errors),
        "target_diagonal": args.target_diagonal,
        "errors": errors,
        "samples": reports,
    }
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"n_ok": out["n_ok"], "n_fail": out["n_fail"], "report": str(args.out_report)}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
