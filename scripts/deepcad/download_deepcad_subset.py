#!/usr/bin/env python3
"""Download a small DeepCAD train subset for pipeline validation.

DeepCAD full data.tar is large (~GB). This script supports:
1. Using an existing local data root
2. Extracting only selected JSON files from a local data.tar
3. Writing a manifest for batch processing

Recommended first run: --num-samples 100
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_ROOT = ROOT / "DeepCAD" / "data"
FALLBACK_DATA_ROOT = Path("/data/home/cuiyuehan/project/cadnew/DeepCAD/data")
DEFAULT_OUT = ROOT / "cad_spatial_dataset" / "DeepCAD" / "raw_json"
DEFAULT_MANIFEST = ROOT / "cad_spatial_dataset" / "DeepCAD" / "manifest_train100.json"

DATA_TAR_URL = "http://www.cs.columbia.edu/cg/deepcad/data.tar"


def _load_split(data_root: Path) -> dict:
    split_path = data_root / "train_val_test_split.json"
    if not split_path.exists():
        raise FileNotFoundError(
            f"missing {split_path}. Download DeepCAD data first:\n"
            f"  mkdir -p {data_root.parent} && cd {data_root.parent}\n"
            f"  wget {DATA_TAR_URL}\n"
            f"  tar -xf data.tar data/train_val_test_split.json data/cad_json\n"
        )
    return json.loads(split_path.read_text(encoding="utf-8"))


def _extract_json_from_tar(tar_path: Path, sample_id: str, out_path: Path) -> bool:
    member = f"data/cad_json/{sample_id}.json"
    with tarfile.open(tar_path, "r:*") as tf:
        try:
            src = tf.extractfile(member)
        except KeyError:
            return False
        if src is None:
            return False
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(src.read())
    return True


def _copy_json(data_root: Path, sample_id: str, out_path: Path) -> bool:
    src = data_root / "cad_json" / f"{sample_id}.json"
    if not src.exists():
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, out_path)
    return True


def _resolve_data_root(data_root: Path | None) -> Path:
    if data_root is not None and (data_root / "train_val_test_split.json").exists():
        return data_root
    if (DEFAULT_DATA_ROOT / "train_val_test_split.json").exists():
        return DEFAULT_DATA_ROOT
    if FALLBACK_DATA_ROOT.exists():
        return FALLBACK_DATA_ROOT
    return data_root or DEFAULT_DATA_ROOT


def download_subset(
    num_samples: int = 100,
    split: str = "train",
    data_root: Path | None = None,
    out_dir: Path = DEFAULT_OUT,
    tar_path: Path | None = None,
    manifest_path: Path = DEFAULT_MANIFEST,
    start: int = 0,
) -> dict:
    data_root = _resolve_data_root(data_root)
    split_data = _load_split(data_root)
    ids = list(split_data[split])[start : start + num_samples]
    if not ids:
        raise ValueError(f"no ids selected from split={split!r}, start={start}, num={num_samples}")

    out_dir.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    missing: list[str] = []

    for sample_id in ids:
        safe_name = sample_id.replace("/", "_")
        out_json = out_dir / f"{safe_name}.json"
        ok = False
        if (data_root / "cad_json" / f"{sample_id}.json").exists():
            ok = _copy_json(data_root, sample_id, out_json)
        elif tar_path is not None and tar_path.exists():
            ok = _extract_json_from_tar(tar_path, sample_id, out_json)
        if ok:
            copied.append(sample_id)
        else:
            missing.append(sample_id)

    manifest = {
        "split": split,
        "start": start,
        "requested": num_samples,
        "copied": len(copied),
        "missing": missing,
        "sample_ids": copied,
        "raw_json_dir": str(out_dir),
        "data_root": str(data_root),
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    manifest["manifest"] = str(manifest_path)
    return manifest


def maybe_download_tar(data_root: Path, tar_path: Path) -> None:
    if tar_path.exists():
        return
    tar_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {DATA_TAR_URL} → {tar_path} (this is large; prefer local copy)")
    subprocess.run(["wget", "-c", DATA_TAR_URL, "-O", str(tar_path)], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare DeepCAD train subset JSON files")
    parser.add_argument("--num-samples", type=int, default=100)
    parser.add_argument("--split", type=str, default="train", choices=["train", "validation", "test"])
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--tar",
        type=Path,
        default=DEFAULT_DATA_ROOT.parent / "data.tar",
        help="Optional local data.tar for selective extraction",
    )
    parser.add_argument(
        "--download-tar",
        action="store_true",
        help="Attempt to download full data.tar if missing (NOT recommended for first test)",
    )
    args = parser.parse_args()

    if args.download_tar:
        maybe_download_tar(args.data_root, args.tar)

    report = download_subset(
        num_samples=args.num_samples,
        split=args.split,
        data_root=args.data_root,
        out_dir=args.out_dir,
        tar_path=args.tar if args.tar.exists() else None,
        manifest_path=args.manifest,
        start=args.start,
    )
    print(json.dumps(report, indent=2))
    if report["missing"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
