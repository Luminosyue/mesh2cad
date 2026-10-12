#!/usr/bin/env python3
"""Select CADFS FeatureScripts that convert losslessly to V4 CAD DSL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
CADFS_FS = ROOT / "CADFS" / "featurescript_rp"
CADFS_STEP = ROOT / "CADFS" / "step"
V4_RECORDS = ROOT / "ours3" / "canonical_cad_data_v4" / "records"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from canonical_cad_data_v4.converters.cadfs_to_dsl import (  # noqa: E402
    CadfsUnsupported,
    audit_featurescript,
    cadfs_to_dsl,
)


def _step_path(sample_id: str) -> Path:
    bucket = sample_id[:4] if len(sample_id) >= 4 else sample_id
    p = CADFS_STEP / bucket / f"{sample_id}.step"
    if p.exists():
        return p
    return CADFS_STEP / bucket / f"{sample_id}.STEP"


def v4_clean_ids() -> list[str]:
    ids: list[str] = []
    if not V4_RECORDS.exists():
        return ids
    for d in sorted(V4_RECORDS.iterdir()):
        if not d.is_dir() or not d.name.startswith("CADFS_"):
            continue
        meta = d / "metadata.json"
        if not meta.exists():
            continue
        rec = json.loads(meta.read_text(encoding="utf-8"))
        if rec.get("status") == "clean":
            ids.append(rec.get("source_id") or d.name.replace("CADFS_", "", 1))
    return ids


def try_convert(fs_path: Path) -> dict:
    text = fs_path.read_text(encoding="utf-8", errors="replace")
    audit = audit_featurescript(text)
    rec = {
        "sample_id": fs_path.stem,
        "featurescript": str(fs_path),
        "step": str(_step_path(fs_path.stem)),
        "lossless_candidate": bool(audit.get("lossless_candidate")),
        "stratum": audit.get("stratum"),
        "unsupported": audit.get("unsupported") or [],
        "convertible": False,
        "reason": None,
        "n_extrude": 0,
    }
    if not rec["lossless_candidate"]:
        rec["reason"] = "not_lossless_candidate:" + ",".join(rec["unsupported"] or ["other"])
        return rec
    if not Path(rec["step"]).exists():
        rec["reason"] = "missing_official_step"
        return rec
    try:
        _dsl, report = cadfs_to_dsl(text)
    except CadfsUnsupported as exc:
        rec["reason"] = exc.reason
        return rec
    except Exception as exc:  # noqa: BLE001
        rec["reason"] = f"{type(exc).__name__}:{exc}"[:240]
        return rec
    rec["convertible"] = True
    rec["n_extrude"] = int(report.get("n_extrude") or 0)
    rec["operations"] = report.get("operations") or []
    return rec


def scan_pool(limit: int, skip_ids: set[str], max_scan: int | None) -> list[dict]:
    selected: list[dict] = []
    scanned = 0
    buckets = sorted(p for p in CADFS_FS.iterdir() if p.is_dir())
    for bucket in buckets:
        for fs in sorted(bucket.glob("*.txt")):
            if max_scan is not None and scanned >= max_scan:
                return selected
            if fs.stem in skip_ids:
                continue
            scanned += 1
            rec = try_convert(fs)
            if rec["convertible"]:
                selected.append(rec)
                skip_ids.add(fs.stem)
                if len(selected) >= limit:
                    return selected
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Select lossless CADFS ids for cad_spatial Dora pack")
    parser.add_argument("--n", type=int, default=400, help="Target convertible sample count")
    parser.add_argument("--prefer-v4-clean", action="store_true", default=True)
    parser.add_argument("--no-prefer-v4-clean", action="store_false", dest="prefer_v4_clean")
    parser.add_argument("--max-scan", type=int, default=20000)
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "cad_spatial_dataset" / "CADFS" / "manifest_lossless.json",
    )
    args = parser.parse_args()

    rows: list[dict] = []
    seen: set[str] = set()
    if args.prefer_v4_clean:
        for sid in v4_clean_ids():
            fs_bucket = sid[:4] if len(sid) >= 4 else sid
            fs = CADFS_FS / fs_bucket / f"{sid}.txt"
            if not fs.exists():
                continue
            rec = try_convert(fs)
            rec["from_v4_clean"] = True
            if rec["convertible"]:
                rows.append(rec)
                seen.add(sid)
            if len(rows) >= args.n:
                break

    if len(rows) < args.n:
        extra = scan_pool(args.n - len(rows), seen, args.max_scan)
        for rec in extra:
            rec["from_v4_clean"] = False
        rows.extend(extra)

    payload = {
        "n_requested": args.n,
        "n_selected": len(rows),
        "n_from_v4_clean": sum(1 for r in rows if r.get("from_v4_clean")),
        "sample_ids": [r["sample_id"] for r in rows],
        "records": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("n_requested", "n_selected", "n_from_v4_clean")}, indent=2))
    print(str(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
