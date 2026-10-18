#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from common import chunk_from_path, ensure_demo_dirs, parse_abc_id, sha256_file, write_csv_dicts


def collect(root: Path, exts: set[str]) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = defaultdict(list)
    if not root.exists():
        return out
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            abc_id = parse_abc_id(p.name)
            if abc_id:
                out[abc_id].append(p)
    return out


def build_index(step_root: Path, stl_root: Path, manifest_dir: Path) -> tuple[int, int]:
    steps = collect(step_root, {".step", ".stp"})
    stls = collect(stl_root, {".stl"})
    ids = sorted(set(steps) | set(stls))
    rows = []
    failures = []
    for abc_id in ids:
        sps = sorted(steps.get(abc_id, []))
        mps = sorted(stls.get(abc_id, []))
        step_path = sps[0] if sps else None
        stl_path = mps[0] if mps else None
        if len(sps) != 1 or len(mps) != 1:
            failures.append({
                "abc_id": abc_id,
                "issue": "duplicate_or_missing",
                "step_count": len(sps),
                "stl_count": len(mps),
                "step_paths": "|".join(map(str, sps[:5])),
                "stl_paths": "|".join(map(str, mps[:5])),
            })
        rows.append({
            "abc_id": abc_id,
            "chunk_id": chunk_from_path(step_path or stl_path or ""),
            "step_path": str(step_path or ""),
            "stl_path": str(stl_path or ""),
            "step_exists": bool(step_path),
            "stl_exists": bool(stl_path),
            "step_sha256": sha256_file(step_path) if step_path else "",
            "stl_sha256": sha256_file(stl_path) if stl_path else "",
            "duplicate_step_count": max(0, len(sps) - 1),
            "duplicate_stl_count": max(0, len(mps) - 1),
        })
    write_csv_dicts(manifest_dir / "abc_file_index.csv", rows, [
        "abc_id", "chunk_id", "step_path", "stl_path", "step_exists", "stl_exists",
        "step_sha256", "stl_sha256", "duplicate_step_count", "duplicate_stl_count",
    ])
    write_csv_dicts(manifest_dir / "index_failures.csv", failures, [
        "abc_id", "issue", "step_count", "stl_count", "step_paths", "stl_paths",
    ])
    return len([r for r in rows if r["step_exists"] and r["stl_exists"]]), len(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="data/abc_v00_demo")
    ap.add_argument("--manifest-dir", default="datasets/abc_hard_two_case_demo/manifests")
    args = ap.parse_args()
    ensure_demo_dirs()
    data = Path(args.data_root)
    matched, total = build_index(data / "step", data / "stl2", Path(args.manifest_dir))
    print(f"MATCHED_STEP_STL_OBJECTS={matched}")
    print(f"INDEXED_OBJECT_IDS={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
