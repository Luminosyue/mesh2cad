#!/usr/bin/env python3
"""Step 3: master candidate manifest. Register source info only. No execute / sample / C2."""

from __future__ import annotations

import json
import os
import sys
from collections import Counter
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from canonical_cad_data_v4.config import (  # noqa: E402
    CADFS_FEATURESCRIPT,
    CADFS_STEP,
    DEEPCAD_RAW_JSON,
    FUSION360_RECON,
    HASHES_DIR,
    MANIFESTS_DIR,
    REPORTS_DIR,
)
from canonical_cad_data_v4.hashutil import file_manifest_entry, sha256_file, write_json  # noqa: E402
from canonical_cad_data_v4.schema import make_cad_id, new_record  # noqa: E402


def _iter_files(root: Path, suffix: str):
    if not root.exists():
        return
    for dirpath, _dirnames, filenames in os.walk(root):
        filenames.sort()
        for name in filenames:
            if name.endswith(suffix):
                yield Path(dirpath) / name


def deepcad_rows():
    for p in sorted(DEEPCAD_RAW_JSON.glob("*.json")) if DEEPCAD_RAW_JSON.exists() else []:
        sid = p.stem
        yield new_record(
            cad_id=make_cad_id("DEEPCAD", sid),
            source="DEEPCAD",
            source_id=sid,
            source_path=str(p),
            program_available=True,
            step_available=False,
            status="candidate",
        )


def fusion360_rows():
    for p in _iter_files(FUSION360_RECON, ".json"):
        sid = p.stem
        yield new_record(
            cad_id=make_cad_id("FUSION360", sid),
            source="FUSION360",
            source_id=sid,
            source_path=str(p),
            program_available=True,
            step_available=False,
            status="candidate",
        )


def cadfs_rows():
    for p in _iter_files(CADFS_FEATURESCRIPT, ".txt"):
        sid = p.stem
        bucket = sid[:4] if len(sid) >= 4 else sid
        step = CADFS_STEP / bucket / f"{sid}.step"
        if not step.exists():
            step = CADFS_STEP / bucket / f"{sid}.STEP"
        yield new_record(
            cad_id=make_cad_id("CADFS", sid),
            source="CADFS",
            source_id=sid,
            source_path=str(p),
            program_available=True,
            step_available=step.exists(),
            status="candidate" if p.exists() else "missing_source",
        )


def run_master_candidates() -> dict:
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    HASHES_DIR.mkdir(parents=True, exist_ok=True)
    out = MANIFESTS_DIR / "master_candidates.jsonl"

    seen_ids: dict[str, int] = Counter()
    seen_source_ids: dict[tuple[str, str], int] = Counter()
    counts = Counter()
    missing = 0
    n = 0
    def all_rows():
        yield from deepcad_rows()
        yield from fusion360_rows()
        yield from cadfs_rows()

    with out.open("w", encoding="utf-8") as f:
        for row in all_rows():
            seen_ids[row["cad_id"]] += 1
            seen_source_ids[(row["source"], row["source_id"])] += 1
            counts[row["source"]] += 1
            if not Path(row["source_path"]).exists():
                missing += 1
                row["status"] = "missing_source"
                row["failure_reason"] = "missing_source"
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            n += 1

    dup_cad = sum(1 for v in seen_ids.values() if v > 1)
    dup_src = sum(1 for v in seen_source_ids.values() if v > 1)
    summary = {
        "TOTAL_CANDIDATES": n,
        "DEEPCAD_COUNT": int(counts["DEEPCAD"]),
        "FUSION360_COUNT": int(counts["FUSION360"]),
        "CADFS_COUNT": int(counts["CADFS"]),
        "DUPLICATE_SOURCE_ID_COUNT": dup_src,
        "DUPLICATE_CAD_ID_COUNT": dup_cad,
        "MISSING_SOURCE_COUNT": missing,
        "manifest": str(out),
        "manifest_sha256": sha256_file(out) if out.exists() else None,
        "manifest_nbytes": out.stat().st_size if out.exists() else 0,
    }
    write_json(REPORTS_DIR / "01_master_candidate_report.json", summary)
    write_json(HASHES_DIR / "01_master_candidates_sha256.json", file_manifest_entry(out))
    return summary


def main() -> int:
    s = run_master_candidates()
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
