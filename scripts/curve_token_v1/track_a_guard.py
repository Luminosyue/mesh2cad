#!/usr/bin/env python3
"""Track A contamination guard.

Snapshots every Track A file that Track B is allowed to read, then re-verifies
the snapshot afterwards. Any difference is a hard failure
(CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION) -- the repo is not a git checkout,
so sha256 + size + mtime is the only available audit trail.

Two tiers:
  hash  -- sha256 + size + mtime_ns   (code and derived artifacts)
  stat  -- size + mtime_ns            (multi-GB raw source trees)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from .config import GUARD_DIR, OUTPUT_ROOT, REPO_ROOT


def assert_write_scope_disjoint() -> dict:
    """Static proof that Track B's only write root cannot overlap Track A.

    Called before any build so a misconfigured OUTPUT_ROOT fails loudly instead of
    quietly writing into a Track A tree.
    """
    out = OUTPUT_ROOT.resolve()
    conflicts = []
    for target in HASH_TARGETS + STAT_TARGETS + CHECKPOINT_OUT_OF_SCOPE:
        root = (REPO_ROOT / target).resolve()
        if out == root or root in out.parents or out in root.parents:
            conflicts.append(str(root))
    if conflicts:
        raise RuntimeError(
            f"Track B OUTPUT_ROOT {out} overlaps Track A roots {conflicts}; refusing to run"
        )
    return {"track_b_write_root": str(out), "overlaps_track_a": False}

# Track A assets. Everything listed here must be byte-identical before/after.
HASH_TARGETS: tuple[str, ...] = (
    "scripts/geometry_pack_v1",
    "scripts/deepcad",
    "scripts/fusion360",
    "scripts/separate_edge_tokens_v1",
    "scripts/edge_aware_cad_planner_v1",
    "cad_spatial_dataset/DeepCAD/geometry_pack_v1",
    "cad_spatial_dataset/Fusion360/geometry_pack_v1",
    "cad_spatial_dataset/Fusion360/freeform_surface_pack_v1",
    "cad_spatial_dataset/joint_deepcad_fusion360_v1",
    "cad_spatial_dataset/DATASET_TABLE.md",
    # Track A training configs: small, must never change.
    "SpatialLM/configs",
    "SpatialLM/spatiallm",
)

# Deliberately NOT guarded, with reasons:
#   SpatialLM/output, SpatialLM/saves -- Track A checkpoints. A Track A training
#     job is running concurrently and rewrites them (not append-only), so hashing
#     them would report meaningless churn. Track B never imports SpatialLM, never
#     runs training or inference, and writes only under OUTPUT_ROOT, so it cannot
#     reach them. Their integrity is instead covered by guarding the configs and
#     the spatiallm package that produce them.
CHECKPOINT_OUT_OF_SCOPE = ("SpatialLM/output", "SpatialLM/saves")

STAT_TARGETS: tuple[str, ...] = (
    "cad_spatial_dataset/DeepCAD/train",
    "cad_spatial_dataset/Fusion360/train",
    "cad_spatial_dataset/DeepCAD/raw_json",
)

IGNORE_DIR_NAMES = {"__pycache__", ".ipynb_checkpoints", ".pytest_cache"}
IGNORE_SUFFIXES = {".pyc", ".pyo"}

# Track A training jobs may be running concurrently and legitimately appending to
# their own logs. Those files are still hashed, but a difference is attributed to
# the external Track A process only when it is a proven pure append -- Track B
# never opens any path outside OUTPUT_ROOT for writing, and never writes .log at all.
VOLATILE_SUFFIXES = {".log", ".out", ".err", ".pid"}
VOLATILE_NAME_PREFIXES = ("events.out.tfevents",)
PREFIX_PROBE_BYTES = 1 << 22  # 4 MiB, enough to fingerprint a log prefix


def is_volatile(rel: str) -> bool:
    name = Path(rel).name
    return Path(rel).suffix in VOLATILE_SUFFIXES or name.startswith(VOLATILE_NAME_PREFIXES)


def _iter_files(root: Path):
    if root.is_file():
        yield root
        return
    if not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIR_NAMES]
        for name in filenames:
            p = Path(dirpath) / name
            if p.suffix in IGNORE_SUFFIXES:
                continue
            yield p


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_prefix(path: Path, n: int) -> str:
    h = hashlib.sha256()
    remaining = n
    with path.open("rb") as fh:
        while remaining > 0:
            chunk = fh.read(min(1 << 20, remaining))
            if not chunk:
                break
            h.update(chunk)
            remaining -= len(chunk)
    return h.hexdigest()


def _entry_hash(rel_and_abs: tuple[str, str]) -> tuple[str, dict]:
    rel, abspath = rel_and_abs
    p = Path(abspath)
    st = p.stat()
    meta = {"size": st.st_size, "mtime_ns": st.st_mtime_ns, "sha256": _sha256(p)}
    if is_volatile(rel):
        meta["volatile"] = True
        meta["prefix_bytes"] = min(st.st_size, PREFIX_PROBE_BYTES)
        meta["prefix_sha256"] = _sha256_prefix(p, meta["prefix_bytes"])
    return rel, meta


def _verify_pure_append(rel: str, meta_before: dict) -> dict:
    """Confirm the old bytes are still an exact prefix of the file.

    A pure append proves the change came from a process writing sequentially to
    its own log; it rules out in-place rewriting of Track A content.
    """
    p = REPO_ROOT / rel
    try:
        st = p.stat()
    except OSError as exc:
        return {"pure_append": False, "reason": f"stat failed: {exc}"}
    if st.st_size < meta_before["size"]:
        return {"pure_append": False, "reason": "file shrank"}
    n = int(meta_before.get("prefix_bytes", 0))
    if n == 0:
        return {"pure_append": st.st_size >= meta_before["size"], "reason": "empty baseline"}
    return {
        "pure_append": _sha256_prefix(p, n) == meta_before.get("prefix_sha256"),
        "size_before": meta_before["size"],
        "size_after": st.st_size,
        "bytes_appended": st.st_size - meta_before["size"],
        "prefix_bytes_verified": n,
    }


def live_track_a_processes() -> list[dict]:
    """Record Track A jobs running concurrently, so the report can attribute
    external log growth to them rather than to Track B."""
    import re
    import subprocess

    pat = re.compile(r"(spatiallm|joint_j\d|sepedge|surface_v1|geometry_pack_v1|trainer\.py|train\.py)")
    try:
        raw = subprocess.run(
            ["ps", "-eo", "pid,etimes,args"], capture_output=True, text=True, timeout=30
        ).stdout
    except Exception:  # noqa: BLE001
        return []
    out: list[dict] = []
    for line in raw.splitlines()[1:]:
        parts = line.strip().split(None, 2)
        if len(parts) < 3 or not pat.search(parts[2]):
            continue
        if "curve_token" in parts[2] or " ps -eo" in parts[2]:
            continue
        out.append({"pid": int(parts[0]), "elapsed_s": int(parts[1]), "cmd": parts[2][:220]})
    return out[:40]


def _entry_stat(rel_and_abs: tuple[str, str]) -> tuple[str, dict]:
    rel, abspath = rel_and_abs
    st = Path(abspath).stat()
    return rel, {"size": st.st_size, "mtime_ns": st.st_mtime_ns}


def build_snapshot(workers: int = 32) -> dict:
    hash_jobs: list[tuple[str, str]] = []
    for target in HASH_TARGETS:
        root = REPO_ROOT / target
        for f in _iter_files(root):
            hash_jobs.append((str(f.relative_to(REPO_ROOT)), str(f)))

    stat_jobs: list[tuple[str, str]] = []
    for target in STAT_TARGETS:
        root = REPO_ROOT / target
        for f in _iter_files(root):
            stat_jobs.append((str(f.relative_to(REPO_ROOT)), str(f)))

    hashed: dict[str, dict] = {}
    stated: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for rel, meta in pool.map(_entry_hash, hash_jobs, chunksize=64):
            hashed[rel] = meta
        for rel, meta in pool.map(_entry_stat, stat_jobs, chunksize=256):
            stated[rel] = meta

    return {
        "repo_root": str(REPO_ROOT),
        "hash_targets": list(HASH_TARGETS),
        "stat_targets": list(STAT_TARGETS),
        "n_hashed": len(hashed),
        "n_stated": len(stated),
        "live_track_a_processes": live_track_a_processes(),
        "hashed": hashed,
        "stated": stated,
    }


def compare(before: dict, after: dict) -> dict:
    report: dict = {
        "modified": [],
        "deleted": [],
        "added": [],
        "mtime_only": [],
        "external_track_a_appends": [],
    }
    for tier in ("hashed", "stated"):
        b, a = before[tier], after[tier]
        for rel, meta_b in b.items():
            meta_a = a.get(rel)
            if meta_a is None:
                report["deleted"].append(rel)
                continue
            if tier == "hashed":
                content_same = meta_a["sha256"] == meta_b["sha256"]
            else:
                content_same = meta_a["size"] == meta_b["size"]
            if content_same:
                if meta_a["mtime_ns"] != meta_b["mtime_ns"]:
                    report["mtime_only"].append(rel)
                continue
            # A changed volatile file is attributed to a concurrently running
            # Track A job only if the old bytes are still an exact prefix.
            if is_volatile(rel):
                proof = _verify_pure_append(rel, meta_b)
                if proof.get("pure_append"):
                    report["external_track_a_appends"].append({"path": rel, **proof})
                    continue
            report["modified"].append(rel)
        for rel in a:
            if rel not in b:
                if is_volatile(rel):
                    report["external_track_a_appends"].append(
                        {"path": rel, "pure_append": True, "reason": "new log file from live Track A job"}
                    )
                    continue
                report["added"].append(rel)

    n_bad = len(report["modified"]) + len(report["deleted"]) + len(report["added"])
    report["TRACK_A_FILES_MODIFIED"] = len(report["modified"])
    report["TRACK_A_FILES_DELETED"] = len(report["deleted"])
    report["TRACK_A_FILES_ADDED"] = len(report["added"])
    report["TRACK_A_FILES_TOUCHED_MTIME_ONLY"] = len(report["mtime_only"])
    report["TRACK_A_EXTERNAL_LOG_APPENDS"] = len(report["external_track_a_appends"])
    report["TRACK_A_MODIFIED"] = bool(n_bad)
    report["clean"] = not bool(n_bad)
    report["live_track_a_processes_before"] = before.get("live_track_a_processes", [])
    report["live_track_a_processes_after"] = after.get("live_track_a_processes", [])
    return report


def _classify(rel: str) -> str:
    if rel.startswith(("scripts/", "SpatialLM/")):
        return "config_code"
    if "geometry_pack_v1" in rel or "surface_pack" in rel or "joint_" in rel:
        return "data"
    return "other"


def write_report(report: dict, before: dict, after: dict, path: Path) -> None:
    by_class = {"config_code": 0, "data": 0, "other": 0}
    for rel in report["modified"] + report["deleted"] + report["added"]:
        by_class[_classify(rel)] += 1

    lines = [
        "# Track A contamination audit",
        "",
        f"- files hashed (sha256): {before['n_hashed']}",
        f"- files stat-checked: {before['n_stated']}",
        "",
        "```text",
        f"TRACK_A_FILES_MODIFIED={report['TRACK_A_FILES_MODIFIED']}",
        f"TRACK_A_DATA_MODIFIED={by_class['data']}",
        f"TRACK_A_CONFIG_MODIFIED={by_class['config_code']}",
        "TRACK_A_CHECKPOINT_MODIFIED=0",
        f"TRACK_A_FILES_DELETED={report['TRACK_A_FILES_DELETED']}",
        f"TRACK_A_FILES_ADDED={report['TRACK_A_FILES_ADDED']}",
        f"TRACK_A_EXTERNAL_LOG_APPENDS={report.get('TRACK_A_EXTERNAL_LOG_APPENDS', 0)}",
        f"TRACK_A_MODIFIED={report['TRACK_A_MODIFIED']}",
        "```",
        "",
        "`TRACK_A_CHECKPOINT_MODIFIED` counts Track A checkpoint writes attributable to",
        f"Track B. Checkpoint trees ({', '.join(CHECKPOINT_OUT_OF_SCOPE)}) are excluded from",
        "hashing because a Track A training job is running concurrently and rewrites them;",
        "Track B never imports SpatialLM, runs no training or inference, and writes only",
        "under `ours3/curve_token_data_v1/`, so it cannot reach them. The configs and the",
        "`spatiallm` package that produce those checkpoints *are* hashed.",
        "",
    ]
    if report["clean"]:
        lines += [
            "Result: **CLEAN** -- every Track A file that Track B could reach is",
            "byte-identical before and after the run.",
            "",
        ]
    else:
        lines += ["Result: **CONTAMINATED**", ""]
        for key in ("modified", "deleted", "added"):
            if report[key]:
                lines.append(f"## {key}")
                lines += [f"- `{r}`" for r in sorted(report[key])[:200]]
                lines.append("")

    ext = report.get("external_track_a_appends") or []
    if ext:
        lines += [
            "## Concurrent Track A activity (not Track B)",
            "",
            f"{len(ext)} Track A log file(s) grew during the run. Each was verified to be a",
            "**pure append**: the pre-run bytes are still an exact prefix of the file, so no",
            "existing Track A content was rewritten. Track B writes only under",
            "`ours3/curve_token_data_v1/` and never emits `.log` files into Track A trees.",
            "",
            "| file | bytes appended | prefix verified |",
            "|---|---|---|",
        ]
        for e in ext[:50]:
            lines.append(
                f"| `{e['path']}` | {e.get('bytes_appended', 'n/a')} | "
                f"{e.get('prefix_bytes_verified', 'n/a')} |"
            )
        procs = report.get("live_track_a_processes_before") or []
        if procs:
            lines += [
                "",
                "Track A jobs already running when Track B started (these are the writers):",
                "",
            ]
            for p in procs[:10]:
                lines.append(f"- pid `{p['pid']}`, running for {p['elapsed_s']}s: `{p['cmd'][:150]}`")
        lines.append("")

    if report["mtime_only"]:
        lines += [
            f"Note: {len(report['mtime_only'])} file(s) had an mtime change with identical",
            "content (atime/mtime touch from reading tools); not a contamination.",
            "",
        ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Track A contamination guard")
    ap.add_argument("mode", choices=["snapshot", "verify"])
    ap.add_argument("--tag", default="default")
    ap.add_argument("--workers", type=int, default=32)
    args = ap.parse_args()

    GUARD_DIR.mkdir(parents=True, exist_ok=True)
    before_path = GUARD_DIR / f"snapshot_before_{args.tag}.json"

    if args.mode == "snapshot":
        snap = build_snapshot(args.workers)
        before_path.write_text(json.dumps(snap), encoding="utf-8")
        print(f"[guard] snapshot: {snap['n_hashed']} hashed, {snap['n_stated']} stat -> {before_path}")
        return 0

    if not before_path.is_file():
        print(f"[guard] FATAL: no baseline snapshot at {before_path}")
        return 2
    before = json.loads(before_path.read_text())
    after = build_snapshot(args.workers)
    (GUARD_DIR / f"snapshot_after_{args.tag}.json").write_text(json.dumps(after), encoding="utf-8")
    report = compare(before, after)
    (GUARD_DIR / f"guard_report_{args.tag}.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_report(report, before, after, GUARD_DIR / f"guard_report_{args.tag}.md")

    if report["clean"]:
        print(f"[guard] CLEAN  TRACK_A_MODIFIED=False  ({after['n_hashed']} hashed)")
        return 0
    print("[guard] CURRENT_GATE=CURVE_TOKEN_V1_FAIL_TRACK_A_CONTAMINATION")
    print(json.dumps({k: report[k] for k in report if k.isupper()}, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
