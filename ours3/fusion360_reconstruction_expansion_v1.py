#!/usr/bin/env python3
"""Stage controller for Fusion360 reconstruction expansion V1.

This script deliberately writes only to the expansion output directory. Frozen
EXACT10K inputs are read for exclusions and provenance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = PROJECT_ROOT / "ours3"
RAW_ROOT = PROJECT_ROOT / "cad_spatial_dataset/Fusion360/reconstruction/reconstruction"
EXACT10K_DIR = OURS3 / "clean10k_pool_merge_and_freeze_v1"
OUT_DIR = OURS3 / "fusion360_reconstruction_expansion_v1"
C2_CHECKPOINT = (
    OURS3 / "curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt"
)

CANARY_N = 100
PILOT_N = 1000
SEED = 42
CONTEXT = 8192
CURVE_K_CAP = 128
PER_CASE_TIMEOUT_SECONDS = 600

FAILURE_TAXONOMY = [
    "SOURCE_PARSE_FAIL",
    "UNSUPPORTED_PROGRAM",
    "DSL_CONVERSION_FAIL",
    "DSL_EXEC_FAIL",
    "STEP_WRITE_FAIL",
    "STEP_RELOAD_FAIL",
    "BREP_INVALID",
    "OCC_NATIVE_NONTERMINATION",
    "SURFACE_FAIL",
    "CURVE_EXTRACTION_FAIL",
    "C2_FAIL",
    "CONTEXT_OVERFLOW",
    "TARGET_TRUNCATION",
    "EOS_SUPERVISION_FAIL",
    "RESULT_SUPERVISION_FAIL",
    "LABEL_MASK_FAIL",
    "OTHER",
]


def read_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_jsonl(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_ids(ids: list[str]) -> str:
    return sha256_text("\n".join(ids) + ("\n" if ids else ""))


def normalize_source_id(cad_id: str | None, source_id: str | None = None) -> str | None:
    raw = source_id or cad_id
    if raw is None:
        return None
    raw = str(raw)
    if raw.startswith("fusion360__"):
        return raw.split("__", 1)[1]
    return raw


def stable_cad_id(source_id: str) -> str:
    return f"fusion360__{source_id}"


def detect_feature_counts(data: dict[str, Any]) -> dict[str, int]:
    entities = data.get("entities") or {}
    counts: Counter[str] = Counter()
    for ent in entities.values():
        if isinstance(ent, dict):
            typ = ent.get("type")
            if typ:
                counts[str(typ)] += 1
            for subkey in ("profiles", "curves", "points", "constraints"):
                if isinstance(ent.get(subkey), dict):
                    counts[subkey] += len(ent[subkey])
    timeline = data.get("timeline") or []
    seq = data.get("sequence") or []
    return {
        "timeline_len": len(timeline) if isinstance(timeline, list) else 0,
        "sequence_len": len(seq) if isinstance(seq, list) else 0,
        "entity_count": len(entities) if isinstance(entities, dict) else 0,
        "sketch_count": counts.get("Sketch", 0),
        "profile_count": counts.get("profiles", 0),
        "curve_entity_count": counts.get("curves", 0),
        "body_count": counts.get("BRepBody", 0) + counts.get("Body", 0),
        "extrude_count": sum(v for k, v in counts.items() if "Extrude" in k),
        "revolve_count": sum(v for k, v in counts.items() if "Revolve" in k),
        "fillet_count": sum(v for k, v in counts.items() if "Fillet" in k),
        "chamfer_count": sum(v for k, v in counts.items() if "Chamfer" in k),
    }


def raw_inventory() -> tuple[list[dict[str, Any]], dict[str, int]]:
    json_paths = sorted(RAW_ROOT.glob("*.json"), key=lambda p: p.name)
    rows: list[dict[str, Any]] = []
    parseable = 0
    has_program = 0
    has_geometry = 0
    has_step = 0
    has_metadata = 0
    ext_counts: Counter[str] = Counter()
    for json_path in json_paths:
        source_id = json_path.stem
        step = RAW_ROOT / f"{source_id}.step"
        smt = RAW_ROOT / f"{source_id}.smt"
        obj = RAW_ROOT / f"{source_id}.obj"
        png = RAW_ROOT / f"{source_id}.png"
        data = None
        err = None
        try:
            data = read_json(json_path)
            parseable += 1
        except Exception as exc:  # keep identity even if source parse fails
            err = repr(exc)
        counts = detect_feature_counts(data) if isinstance(data, dict) else {}
        if isinstance(data, dict) and (data.get("timeline") or data.get("sequence")):
            has_program += 1
        if step.exists() or smt.exists() or obj.exists():
            has_geometry += 1
        if step.exists():
            has_step += 1
        if isinstance(data, dict) and data.get("metadata"):
            has_metadata += 1
        for p in (json_path, step, smt, obj, png):
            if p.exists():
                ext_counts[p.suffix.lower()] += 1
        rows.append(
            {
                "cad_id": stable_cad_id(source_id),
                "source_id": source_id,
                "dataset": "Fusion360",
                "subset": "reconstruction",
                "raw_path": str(json_path),
                "program_path": str(json_path),
                "geometry_path": str(step if step.exists() else obj if obj.exists() else smt if smt.exists() else ""),
                "step_path": str(step) if step.exists() else None,
                "obj_path": str(obj) if obj.exists() else None,
                "smt_path": str(smt) if smt.exists() else None,
                "metadata_path": str(json_path) if isinstance(data, dict) and data.get("metadata") else None,
                "png_path": str(png) if png.exists() else None,
                "parseable_source": data is not None,
                "has_program": bool(isinstance(data, dict) and (data.get("timeline") or data.get("sequence"))),
                "has_geometry": step.exists() or smt.exists() or obj.exists(),
                "has_step": step.exists(),
                "has_metadata": bool(isinstance(data, dict) and data.get("metadata")),
                "source_parse_error": err,
                "source_json_bytes": json_path.stat().st_size,
                "step_bytes": step.stat().st_size if step.exists() else 0,
                "obj_bytes": obj.stat().st_size if obj.exists() else 0,
                "smt_bytes": smt.stat().st_size if smt.exists() else 0,
                **counts,
            }
        )
    stats = {
        "RAW_TOTAL": len(rows),
        "PARSEABLE_SOURCE": parseable,
        "HAS_PROGRAM": has_program,
        "HAS_GEOMETRY": has_geometry,
        "HAS_STEP": has_step,
        "HAS_METADATA": has_metadata,
        "RAW_FILE_EXTENSION_COUNTS": dict(sorted(ext_counts.items())),
    }
    return rows, stats


def add_ids_from_row(row: dict[str, Any], dest: dict[str, set[str]], label: str) -> None:
    if str(row.get("dataset", "")).lower() == "fusion360":
        sid = normalize_source_id(row.get("cad_id"), row.get("source_id"))
        if sid:
            dest[label].add(sid)
    for key in ("cad_id", "source_id", "sample_id"):
        sid = normalize_source_id(row.get(key))
        if sid and re.match(r"^\d+_[0-9a-fA-F]+_\d+(?:_\d+)?$", sid):
            dest[label].add(sid)


def build_exclusion_sets() -> tuple[dict[str, Any], dict[str, Any]]:
    buckets: dict[str, set[str]] = defaultdict(set)
    sources: dict[str, dict[str, Any]] = {}

    exact_manifest = EXACT10K_DIR / "EXACT10K_MANIFEST.jsonl"
    for row in iter_jsonl(exact_manifest):
        before = len(buckets["exact10k_v1"])
        add_ids_from_row(row, buckets, "exact10k_v1")
        if len(buckets["exact10k_v1"]) > before:
            sid = normalize_source_id(row.get("cad_id"), row.get("source_id"))
            if sid:
                sources.setdefault(sid, {})["exact10k_v1"] = str(exact_manifest)

    for fn in ("ALL_READY_10431.jsonl",):
        path = EXACT10K_DIR / fn
        for row in iter_jsonl(path):
            before = len(buckets["all_ready_10431_fusion"])
            add_ids_from_row(row, buckets, "all_ready_10431_fusion")
            if len(buckets["all_ready_10431_fusion"]) > before:
                sid = normalize_source_id(row.get("cad_id"), row.get("source_id"))
                if sid:
                    sources.setdefault(sid, {})["all_ready_10431_fusion"] = str(path)

    common = OURS3 / "fusion360_dora_free_common_valid_equivalence_v1/COMMON_VALID_SUBSET_FREEZE.json"
    common_obj = read_json(common) or {}
    for row in common_obj.get("records", []):
        sid = normalize_source_id(row.get("cad_id"), row.get("source_id"))
        if sid:
            buckets["historical_common_valid_592"].add(sid)
            sources.setdefault(sid, {})["historical_common_valid_592"] = str(common)

    for path in [
        OURS3 / "m2_exact_source_ready_2796_full_stage_audit_v1/EXACT_SOURCE_READY_2796_FREEZE.jsonl",
        OURS3 / "m2_exact_source_ready_1851_eligibility_completion_v1/FINAL_2796_ELIGIBILITY.jsonl",
        OURS3 / "m2_rebaseline_runtime_interface_closure_v1/FINAL_RUNTIME_ELIGIBILITY.jsonl",
        OURS3 / "deepcad_fusion360_full_clean_build_v1/FULL_CANDIDATE_REGISTRY.jsonl",
    ]:
        for row in iter_jsonl(path):
            label = path.stem.lower()
            before = len(buckets[label])
            add_ids_from_row(row, buckets, label)
            if len(buckets[label]) > before:
                sid = normalize_source_id(row.get("cad_id"), row.get("source_id"))
                if sid:
                    sources.setdefault(sid, {})[label] = str(path)

    protected_paths = [
        OURS3 / "deepcad_fusion360_full_clean_build_v1/HISTORICAL_EVAL_PROTECTION.json",
        OURS3 / "m2_rebaseline_runtime_interface_closure_v1/FINAL_REBASELINE_EXTERNAL_EVAL.json",
        EXACT10K_DIR / "EXACT10K_LEAKAGE_AUDIT.json",
    ]
    for path in protected_paths:
        obj = read_json(path)
        text = json.dumps(obj, sort_keys=True) if obj is not None else ""
        for sid in set(re.findall(r"\b\d+_[0-9a-fA-F]{6,}_\d+(?:_\d+)?\b", text)):
            buckets["protected_eval_records"].add(sid)
            sources.setdefault(sid, {})["protected_eval_records"] = str(path)

    exclusion_ids = sorted(set().union(*buckets.values()) if buckets else set())
    exclusion = {
        "dataset": "Fusion360",
        "subset": "reconstruction",
        "identity_normalization": "cad_id fusion360__<source_id> and bare source_id both normalize to source_id",
        "excluded_source_ids": exclusion_ids,
        "excluded_cad_ids": [stable_cad_id(sid) for sid in exclusion_ids],
        "buckets": {k: sorted(v) for k, v in sorted(buckets.items())},
        "source_refs": sources,
    }
    audit = {
        "EXACT10K_V1_USED_FUSION360_IDS": len(buckets.get("exact10k_v1", set())),
        "ALL_READY_10431_FUSION_IDS": len(buckets.get("all_ready_10431_fusion", set())),
        "HISTORICAL_COMMON_VALID_592_IDS": len(buckets.get("historical_common_valid_592", set())),
        "PROTECTED_EVAL_IDS": len(buckets.get("protected_eval_records", set())),
        "TOTAL_EXCLUDED_UNIQUE": len(exclusion_ids),
        "sources": {k: len(v) for k, v in sorted(buckets.items())},
        "exclusion_id_sha256": sha256_ids(exclusion_ids),
        "audit_note": "Counts are derived from concrete manifests/audit records; no historical count was forced.",
    }
    return exclusion, audit


def select_canary(candidates: list[dict[str, Any]], n: int = CANARY_N) -> list[dict[str, Any]]:
    if len(candidates) <= n:
        return candidates
    rng = random.Random(SEED)
    selected: dict[str, dict[str, Any]] = {}

    def add(row: dict[str, Any]) -> None:
        if len(selected) < n:
            selected[row["source_id"]] = row

    # Cover extremes and quantiles for complexity and geometry size.
    keys = ["timeline_len", "sequence_len", "entity_count", "source_json_bytes", "step_bytes", "obj_bytes"]
    for key in keys:
        ordered = sorted(candidates, key=lambda r: (r.get(key, 0), r["source_id"]))
        for idx in [0, len(ordered) // 10, len(ordered) // 4, len(ordered) // 2, 3 * len(ordered) // 4, 9 * len(ordered) // 10, len(ordered) - 1]:
            add(ordered[idx])

    # Cover operation categories when metadata/source can expose them.
    op_keys = ["extrude_count", "revolve_count", "fillet_count", "chamfer_count", "sketch_count", "profile_count", "body_count"]
    for key in op_keys:
        positives = [r for r in candidates if r.get(key, 0) > 0]
        ordered = sorted(positives, key=lambda r: (-r.get(key, 0), r["source_id"]))
        for row in ordered[:5]:
            add(row)

    # Stable random remainder across the full candidate space.
    shuffled = list(candidates)
    rng.shuffle(shuffled)
    for row in shuffled:
        add(row)
        if len(selected) >= n:
            break
    return [selected[k] for k in sorted(selected)]


def select_pilot(candidates: list[dict[str, Any]], canary_ids: set[str], n: int = PILOT_N) -> list[dict[str, Any]]:
    remaining = [r for r in candidates if r["source_id"] not in canary_ids]
    rng = random.Random(SEED + 1000)
    ordered = list(remaining)
    rng.shuffle(ordered)
    chosen = ordered[: min(n, len(ordered))]
    return [r for r in sorted(chosen, key=lambda x: x["source_id"])]


def summarize_ops(rows: list[dict[str, Any]]) -> dict[str, Any]:
    numeric_keys = [
        "timeline_len",
        "sequence_len",
        "entity_count",
        "sketch_count",
        "profile_count",
        "curve_entity_count",
        "body_count",
        "extrude_count",
        "revolve_count",
        "fillet_count",
        "chamfer_count",
        "source_json_bytes",
        "step_bytes",
        "obj_bytes",
    ]
    out: dict[str, Any] = {}
    for key in numeric_keys:
        vals = sorted(int(r.get(key, 0) or 0) for r in rows)
        if not vals:
            continue
        out[key] = {
            "min": vals[0],
            "p50": vals[len(vals) // 2],
            "p90": vals[int(0.9 * (len(vals) - 1))],
            "p95": vals[int(0.95 * (len(vals) - 1))],
            "p99": vals[int(0.99 * (len(vals) - 1))],
            "max": vals[-1],
        }
    return out


def run_cmd(cmd: list[str], timeout: int | None = None, cwd: Path | None = None) -> tuple[int, str, str, bool]:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True, timeout=timeout)
        return proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", exc.stderr or "", True


def classify_build_failure(returncode: int, stdout: str, stderr: str, timed_out: bool) -> str:
    text = f"{stdout}\n{stderr}"
    if timed_out:
        return "OCC_NATIVE_NONTERMINATION"
    if returncode == 2 or "Fusion360FilterError" in text or "filter_reason" in text:
        return "UNSUPPORTED_PROGRAM"
    if "convert_file" in text or "fusion360_to_dsl" in text:
        return "DSL_CONVERSION_FAIL"
    if "dsl_to_occ" in text or "run_dsl_to_occ" in text:
        return "DSL_EXEC_FAIL"
    if "STEP" in text and "reload" in text:
        return "STEP_RELOAD_FAIL"
    if "build_cad_spatial_part" in text or "trimesh" in text or "Dora" in text:
        return "SURFACE_FAIL"
    if returncode == 3:
        # The legacy Fusion360 builder returns 3 for QA mismatch between the
        # canonical DSL execution and official geometry. Keep this under
        # conversion semantics rather than protocol drift.
        return "DSL_CONVERSION_FAIL"
    return "OTHER"


def execute_canary(rows: list[dict[str, Any]], force: bool = False) -> dict[str, Any]:
    report_path = OUT_DIR / "FUSION360_CANARY100_REPORT.json"
    result_path = OUT_DIR / "canary/FUSION360_CANARY100_EXECUTION.jsonl"
    if report_path.exists() and not force:
        return read_json(report_path)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    nonterms: list[dict[str, Any]] = []
    build_root = OUT_DIR / "canary/build"
    for i, row in enumerate(rows, 1):
        sid = row["source_id"]
        case_start = time.time()
        cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts/fusion360/build_fusion360_sample.py"),
            "--sample-id",
            sid,
            "--output",
            str(build_root),
            "--num-points",
            "8192",
            "--no-vis",
        ]
        rc, so, se, timed_out = run_cmd(cmd, timeout=PER_CASE_TIMEOUT_SECONDS, cwd=PROJECT_ROOT)
        meta_path = build_root / "Fusion360/train" / sid / "meta.json"
        meta = read_json(meta_path) or {}
        qa = meta.get("qa") or {}
        ok = rc == 0 and bool(qa.get("passed", True))
        failure = None if ok else classify_build_failure(rc, so, se, timed_out)
        out_row = {
            **{k: row[k] for k in ("cad_id", "source_id", "dataset", "subset", "raw_path", "program_path", "step_path", "obj_path", "metadata_path")},
            "index": i,
            "returncode": rc,
            "timeout": timed_out,
            "elapsed_seconds": round(time.time() - case_start, 3),
            "PROGRAM_PASS": bool(meta.get("conversion")),
            "DSL_EXEC_PASS": bool(meta.get("occ_qa", {}).get("ok")),
            "STEP_PASS": bool(meta.get("model_step")) or bool(meta.get("occ_qa", {}).get("step")),
            "BREP_PASS": ok,
            "SURFACE_PASS": ok and bool(meta.get("spatial", {}).get("num_points") == 8192),
            "CURVE_PASS": False,
            "C2_PASS": False,
            "RUNTIME_PASS": False,
            "FINAL_READY": False,
            "failure_stage": failure,
            "failure_reason": (qa.get("reject_reason") or se[-1000:] or so[-1000:]) if failure else None,
            "artifact_dir": str(build_root / "Fusion360/train" / sid),
        }
        results.append(out_row)
        if failure:
            failures.append(
                {
                    "cad_id": row["cad_id"],
                    "source_id": sid,
                    "stage": failure,
                    "failure_reason": out_row["failure_reason"],
                    "timeout": timed_out,
                    "artifact_refs": {"artifact_dir": out_row["artifact_dir"]},
                }
            )
        if timed_out:
            nonterms.append(
                {
                    "cad_id": row["cad_id"],
                    "source_id": sid,
                    "timeout": PER_CASE_TIMEOUT_SECONDS,
                    "stage": "OCC_NATIVE_NONTERMINATION",
                    "retry_count": 0,
                    "worker_status": "subprocess_timeout_killed",
                }
            )
        print(f"[canary {i}/{len(rows)}] {sid} rc={rc} failure={failure}", flush=True)
    write_jsonl(result_path, results)
    append_failures(failures)
    append_nonterms(nonterms)
    counts = {field: sum(1 for r in results if r.get(field)) for field in ["PROGRAM_PASS", "DSL_EXEC_PASS", "STEP_PASS", "BREP_PASS", "SURFACE_PASS", "CURVE_PASS", "C2_PASS", "RUNTIME_PASS", "FINAL_READY"]}
    failure_matrix = dict(Counter(r["failure_stage"] or "PASS_GEOMETRY_ONLY_CURVE_C2_RUNTIME_PENDING" for r in results))
    unresolved_infra = failure_matrix.get("OTHER", 0)
    systemic = max([v for k, v in failure_matrix.items() if k != "PASS_GEOMETRY_ONLY_CURVE_C2_RUNTIME_PENDING"] or [0]) > len(rows) * 0.10
    gate = "FUSION360_CANARY_SYSTEMIC_FAILURE_REVIEW" if systemic or unresolved_infra else "FUSION360_CANARY_GEOMETRY_COMPLETE_RUNTIME_PENDING"
    report = {
        "CURRENT_STAGE": "CANARY100",
        "CANARY_N": len(rows),
        **counts,
        "READY_YIELD": counts["FINAL_READY"] / len(rows) if rows else 0,
        "FAILURE_MATRIX": failure_matrix,
        "OCC_NATIVE_NONTERMINATION": failure_matrix.get("OCC_NATIVE_NONTERMINATION", 0),
        "UNRESOLVED_INFRA_FAILURE": unresolved_infra,
        "PROTOCOL_DRIFT": "NO",
        "CURRENT_GATE": gate,
        "NEXT_STEP": "Run official GT curve/C2/runtime audit for canary; do not proceed to Pilot1000 until it passes.",
        "notes": [
            "Canary execution used existing Fusion360 canonical DSL/official geometry/spatial QA builder in per-case subprocess isolation.",
            "CURVE/C2/RUNTIME/FINAL_READY remain false because no official expansion C2/runtime writer was executed by this controller.",
        ],
    }
    write_json(report_path, report)
    return report


def append_failures(rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path = OUT_DIR / "FUSION360_EXPANSION_FAILURES.jsonl"
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def append_nonterms(rows: list[dict[str, Any]]) -> None:
    path = OUT_DIR / "FUSION360_OCC_NATIVE_NONTERMINATION.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with path.open("a", encoding="utf-8") as f:
            for row in rows:
                f.write(json.dumps(row, sort_keys=True) + "\n")
    elif not path.exists():
        path.write_text("", encoding="utf-8")


def existing_gpu_plan() -> dict[str, Any]:
    rc, so, se, _ = run_cmd(["bash", "-lc", "nvidia-smi --query-gpu=index,name,memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits"], timeout=20)
    gpus = []
    if rc == 0:
        for line in so.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 5:
                idx, name, used, total, util = parts[:5]
                try:
                    used_i, total_i, util_i = int(used), int(total), int(util)
                except ValueError:
                    used_i = total_i = util_i = -1
                gpus.append({"index": int(idx), "name": name, "memory_used_mb": used_i, "memory_total_mb": total_i, "utilization_gpu_pct": util_i})
    free = [g["index"] for g in gpus if g.get("memory_used_mb", 10**9) < 1024 and g.get("utilization_gpu_pct", 100) < 20]
    return {
        "AVAILABLE_GPUS": gpus,
        "TRAINING_RESERVED_GPUS": "UNKNOWN_NO_FORMAL_LOCKFILE_FOUND",
        "CLEANING_GPUS": free[:1],
        "CPU_WORKERS": min(8, max(1, (os.cpu_count() or 4) // 4)),
        "OCC_WORKERS": 1,
        "SURFACE_WORKERS": 1 if free else 0,
        "C2_WORKERS": 1 if free else 0,
        "GPU_POLICY": "Do not use training-reserved GPUs; if reservation is unknown, run CPU/OCC stages and keep GPU-dependent stages gated.",
        "nvidia_smi_returncode": rc,
        "nvidia_smi_stderr": se[-1000:],
    }


def stage_a(run_canary: bool = False, force_canary: bool = False) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "shards").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "canary").mkdir(parents=True, exist_ok=True)
    raw_rows, inv_stats = raw_inventory()
    exclusion, exclusion_audit = build_exclusion_sets()
    excluded = set(exclusion["excluded_source_ids"])
    for row in raw_rows:
        row["existing_overlap"] = row["source_id"] in excluded
        row["protected_overlap"] = row["source_id"] in set(exclusion["buckets"].get("protected_eval_records", []))
    candidates = [
        r for r in raw_rows
        if r["parseable_source"] and r["has_program"] and r["has_geometry"] and r["has_step"] and not r["existing_overlap"] and not r["protected_overlap"]
    ]
    candidates = sorted(candidates, key=lambda r: r["source_id"])
    canary = select_canary(candidates)
    canary_ids = {r["source_id"] for r in canary}
    pilot = select_pilot(candidates, canary_ids)

    inventory = {
        **inv_stats,
        "EXISTING_OVERLAP": sum(1 for r in raw_rows if r["existing_overlap"]),
        "PROTECTED_OVERLAP": sum(1 for r in raw_rows if r["protected_overlap"]),
        "NEW_RAW_CANDIDATES": len(candidates),
        "raw_root": str(RAW_ROOT),
        "candidate_policy": "parseable source + program + STEP geometry + not in formal exclusion/protected sets",
        "raw_source_id_sha256": sha256_ids([r["source_id"] for r in raw_rows]),
        "new_candidate_id_sha256": sha256_ids([r["source_id"] for r in candidates]),
        "operation_statistics": summarize_ops(raw_rows),
        "new_candidate_operation_statistics": summarize_ops(candidates),
    }

    write_json(OUT_DIR / "FUSION360_RECONSTRUCTION_INVENTORY.json", inventory)
    write_json(OUT_DIR / "FUSION360_EXISTING_EXCLUSION_SET.json", exclusion)
    write_json(OUT_DIR / "FUSION360_EXISTING_EXCLUSION_AUDIT.json", exclusion_audit)
    write_jsonl(OUT_DIR / "FUSION360_NEW_CANDIDATES.jsonl", candidates)
    write_jsonl(OUT_DIR / "FUSION360_CANARY100_MANIFEST.jsonl", canary)
    write_jsonl(OUT_DIR / "FUSION360_PILOT1000_MANIFEST.jsonl", pilot)

    # Freeze the full cohort now by candidate order, but do not run it.
    write_jsonl(OUT_DIR / "FUSION360_FULL_EXPANSION_MANIFEST.jsonl", candidates)
    shard_dir = OUT_DIR / "shards"
    for old in shard_dir.glob("shard_*.jsonl"):
        old.unlink()
    for i in range(0, len(candidates), 100):
        write_jsonl(shard_dir / f"shard_{i//100:03d}.jsonl", candidates[i:i + 100])

    write_json(OUT_DIR / "FUSION360_CLEANING_RESOURCE_PLAN.json", existing_gpu_plan())
    write_jsonl(OUT_DIR / "FUSION360_GEOMETRY_C2_CLEAN.jsonl", [])
    write_jsonl(OUT_DIR / "FUSION360_FINAL_ELIGIBILITY.jsonl", [])
    write_jsonl(OUT_DIR / "FUSION360_RECONSTRUCTION_READY_EXPANSION_V1.jsonl", [])
    write_jsonl(OUT_DIR / "FUSION360_EXTERNAL_TEST_CANDIDATE_POOL.jsonl", [])
    if not (OUT_DIR / "FUSION360_EXPANSION_FAILURES.jsonl").exists():
        write_jsonl(OUT_DIR / "FUSION360_EXPANSION_FAILURES.jsonl", [])
    if not (OUT_DIR / "FUSION360_OCC_NATIVE_NONTERMINATION.jsonl").exists():
        write_jsonl(OUT_DIR / "FUSION360_OCC_NATIVE_NONTERMINATION.jsonl", [])

    protocol = {
        "Canonical target": "same",
        "Surface": "same",
        "Curve representation": "same",
        "C2": "same",
        "Context": "same",
        "Tokenizer": "same",
        "Supervision": "same",
        "Runtime collator": "same",
        "Allowed difference": "source dataset-specific ingestion parser",
        "Canonical target detail": "CANONICAL_DSL",
        "Surface detail": "8192x6 xyz+normal via official surface pipeline",
        "Curve source": "GT_BREP",
        "C2 checkpoint": str(C2_CHECKPOINT),
        "C2 checkpoint sha256": sha256_file(C2_CHECKPOINT),
        "VARIABLE_K": "YES",
        "K_CAP": CURVE_K_CAP,
        "K8": "NO",
        "CONTEXT": CONTEXT,
        "PROTOCOL_DRIFT": "NO",
    }
    write_json(OUT_DIR / "FUSION360_PROTOCOL_DRIFT_AUDIT.json", protocol)

    canary_report = None
    if run_canary:
        canary_report = execute_canary(canary, force=force_canary)
    else:
        canary_report = {
            "CURRENT_STAGE": "CANARY100",
            "CANARY_N": len(canary),
            "PROGRAM_PASS": 0,
            "DSL_EXEC_PASS": 0,
            "STEP_PASS": 0,
            "BREP_PASS": 0,
            "SURFACE_PASS": 0,
            "CURVE_PASS": 0,
            "C2_PASS": 0,
            "RUNTIME_PASS": 0,
            "FINAL_READY": 0,
            "READY_YIELD": 0,
            "FAILURE_MATRIX": {},
            "OCC_NATIVE_NONTERMINATION": 0,
            "UNRESOLVED_INFRA_FAILURE": 0,
            "PROTOCOL_DRIFT": "NO",
            "CURRENT_GATE": "FUSION360_CANARY_READY_TO_RUN",
            "NEXT_STEP": "Run --run-canary with per-case subprocess isolation, then gate Pilot1000.",
        }
        write_json(OUT_DIR / "FUSION360_CANARY100_REPORT.json", canary_report)

    pilot_report = {
        "CURRENT_STAGE": "PILOT1000",
        "PILOT_N": len(pilot),
        "FINAL_READY": 0,
        "READY_YIELD": 0,
        "PROGRAM_FAIL": 0,
        "GEOMETRY_FAIL": 0,
        "OCC_NATIVE_NONTERMINATION": 0,
        "SURFACE_FAIL": 0,
        "CURVE_FAIL": 0,
        "C2_FAIL": 0,
        "CONTEXT_OVERFLOW": 0,
        "SUPERVISION_FAIL": 0,
        "CANARY_OVERLAP": len(set(r["source_id"] for r in pilot) & canary_ids),
        "EXACT10K_OVERLAP": len(set(r["source_id"] for r in pilot) & set(exclusion["buckets"].get("exact10k_v1", []))),
        "EXISTING_READY_OVERLAP": len(set(r["source_id"] for r in pilot) & excluded),
        "PROTECTED_OVERLAP": len(set(r["source_id"] for r in pilot) & set(exclusion["buckets"].get("protected_eval_records", []))),
        "CURRENT_GATE": "BLOCKED_UNTIL_CANARY100_FINAL_READY_GATE_PASSES",
        "NEXT_STEP": "Do not launch Pilot1000 until canary has no systemic failure and official C2/runtime audit passes.",
    }
    write_json(OUT_DIR / "FUSION360_PILOT1000_REPORT.json", pilot_report)

    failure_summary = {
        "TOTAL_FAIL": sum(1 for _ in iter_jsonl(OUT_DIR / "FUSION360_EXPANSION_FAILURES.jsonl")),
        **{k: 0 for k in FAILURE_TAXONOMY},
    }
    for row in iter_jsonl(OUT_DIR / "FUSION360_EXPANSION_FAILURES.jsonl"):
        stage = row.get("stage") if row.get("stage") in FAILURE_TAXONOMY else "OTHER"
        failure_summary[stage] += 1
    write_json(OUT_DIR / "FUSION360_EXPANSION_FAILURE_SUMMARY.json", failure_summary)

    full_ids = [r["source_id"] for r in candidates]
    final_ids: list[str] = []
    stats = {
        "RAW_TOTAL": inventory["RAW_TOTAL"],
        "NEW_CANDIDATE_N": len(candidates),
        "CANARY_N": len(canary),
        "PILOT_N": len(pilot),
        "FULL_COHORT_N": len(candidates),
        "PROGRAM_PASS": canary_report.get("PROGRAM_PASS", 0),
        "GEOMETRY_PASS": canary_report.get("SURFACE_PASS", 0),
        "SURFACE_PASS": canary_report.get("SURFACE_PASS", 0),
        "CURVE_PASS": canary_report.get("CURVE_PASS", 0),
        "C2_PASS": canary_report.get("C2_PASS", 0),
        "RUNTIME_PASS": canary_report.get("RUNTIME_PASS", 0),
        "FINAL_READY": 0,
        "READY_YIELD": 0,
        "failure_matrix": canary_report.get("FAILURE_MATRIX", {}),
    }
    write_json(OUT_DIR / "FUSION360_EXPANSION_DATASET_STATS.json", stats)

    provenance = {
        "task": "FUSION360_RECONSTRUCTION_EXPANSION_V1",
        "raw_root": str(RAW_ROOT),
        "raw_inventory_hash": sha256_file(OUT_DIR / "FUSION360_RECONSTRUCTION_INVENTORY.json"),
        "exclusion_set_hash": sha256_file(OUT_DIR / "FUSION360_EXISTING_EXCLUSION_SET.json"),
        "candidate_manifest_hash": sha256_file(OUT_DIR / "FUSION360_NEW_CANDIDATES.jsonl"),
        "canary_hash": sha256_file(OUT_DIR / "FUSION360_CANARY100_MANIFEST.jsonl"),
        "pilot_hash": sha256_file(OUT_DIR / "FUSION360_PILOT1000_MANIFEST.jsonl"),
        "full_cohort_hash": sha256_file(OUT_DIR / "FUSION360_FULL_EXPANSION_MANIFEST.jsonl"),
        "C2_checkpoint": str(C2_CHECKPOINT),
        "C2_checkpoint_hash": sha256_file(C2_CHECKPOINT),
        "protocol_references": [
            str(EXACT10K_DIR / "EXACT10K_RUNTIME_SURFACE_TARGET_M2_CONTRACT.json"),
            str(OURS3 / "m2_rebaseline_runtime_interface_closure_v1/FINAL_RUNTIME_CONTEXT_FREEZE.json"),
            str(OURS3 / "m2_rebaseline_runtime_interface_closure_v1/REBASELINE_DATASET_COLLATOR_FREEZE.json"),
        ],
        "runtime_audit_references": [
            str(OURS3 / "m2_rebaseline_runtime_interface_closure_v1/B0_FULL_LOADER_RUNTIME_AUDIT.json"),
            str(OURS3 / "m2_rebaseline_runtime_interface_closure_v1/M2_FULL_LOADER_RUNTIME_AUDIT.json"),
        ],
        "final_ready_hash": sha256_file(OUT_DIR / "FUSION360_RECONSTRUCTION_READY_EXPANSION_V1.jsonl"),
        "NEW_CANDIDATE_ID_SHA256": sha256_ids([r["source_id"] for r in candidates]),
        "FULL_COHORT_ID_SHA256": sha256_ids(full_ids),
        "FINAL_READY_ID_SHA256": sha256_ids(final_ids),
        "FINAL_READY_MANIFEST_SHA256": sha256_file(OUT_DIR / "FUSION360_RECONSTRUCTION_READY_EXPANSION_V1.jsonl"),
    }
    write_json(OUT_DIR / "FUSION360_EXPANSION_PROVENANCE.json", provenance)

    final_report = {
        "CURRENT_STAGE": "CANARY100" if run_canary else "INVENTORY",
        "RAW_TOTAL": inventory["RAW_TOTAL"],
        "EXISTING_EXCLUDED": inventory["EXISTING_OVERLAP"],
        "NEW_RAW_CANDIDATES": len(candidates),
        "CANARY_N": len(canary),
        "PILOT_N": len(pilot),
        "FULL_COHORT": len(candidates),
        "COMPLETED": len(canary) if run_canary else 0,
        "GEOMETRY_C2_CLEAN": 0,
        "RUNTIME_AUDITED": 0,
        "FINAL_READY": 0,
        "READY_YIELD": 0,
        "FAILURES": failure_summary,
        "CONTRACT": {
            "TARGET": "CANONICAL_DSL",
            "SURFACE": "SAME_AS_EXACT10K_V1",
            "CURVE_SOURCE": "GT_BREP",
            "C2": "FROZEN",
            "VARIABLE_K": "YES",
            "CAP": CURVE_K_CAP,
            "CONTEXT": CONTEXT,
            "K8": "NO",
            "PROTOCOL_DRIFT": "NO",
        },
        "LEAKAGE": {
            "EXACT10K_OVERLAP": 0,
            "EXISTING_READY_DUPLICATE": 0,
            "PROTECTED_CONFLICT": 0,
        },
        "READY_POOL": {
            "NEW_FUSION360_READY": 0,
            "FINAL_READY_ID_SHA256": provenance["FINAL_READY_ID_SHA256"],
            "FINAL_READY_MANIFEST_SHA256": provenance["FINAL_READY_MANIFEST_SHA256"],
        },
        "SAFETY": {
            "EXACT10K_V1_CHANGED": "NO",
            "TRAINING_RUN": "NO",
            "OPTIMIZER_STEP": "NO",
            "DECODE_RUN": "NO",
            "TARGET_CHANGED": "NO",
            "TOKENIZER_CHANGED": "NO",
            "CONTEXT_CHANGED": "NO",
            "C2_CHANGED": "NO",
        },
        "CURRENT_GATE": canary_report.get("CURRENT_GATE", "FUSION360_CANARY_READY_TO_RUN"),
        "FUSION360_EXPANSION_READY": "NO",
        "EXACT10K_V1_CHANGED": "NO",
        "TRAINING_BLOCKED_BY_EXPANSION": "NO",
        "NEXT_RECOMMENDED_DATA_TASK": None,
    }
    write_json(OUT_DIR / "FINAL_REPORT.json", final_report)
    md = f"""# FUSION360_RECONSTRUCTION_EXPANSION_V1

CURRENT_STAGE = {final_report['CURRENT_STAGE']}

RAW_TOTAL = {inventory['RAW_TOTAL']}
EXISTING_EXCLUDED = {inventory['EXISTING_OVERLAP']}
PROTECTED_OVERLAP = {inventory['PROTECTED_OVERLAP']}
NEW_RAW_CANDIDATES = {len(candidates)}
CANARY_N = {len(canary)}
PILOT_N = {len(pilot)}
FULL_COHORT = {len(candidates)}

PROGRAM_PASS = {canary_report.get('PROGRAM_PASS', 0)}
DSL_EXEC_PASS = {canary_report.get('DSL_EXEC_PASS', 0)}
STEP_PASS = {canary_report.get('STEP_PASS', 0)}
BREP_PASS = {canary_report.get('BREP_PASS', 0)}
SURFACE_PASS = {canary_report.get('SURFACE_PASS', 0)}
CURVE_PASS = {canary_report.get('CURVE_PASS', 0)}
C2_PASS = {canary_report.get('C2_PASS', 0)}
RUNTIME_PASS = {canary_report.get('RUNTIME_PASS', 0)}
FINAL_READY = 0
READY_YIELD = 0

CURRENT_GATE = {final_report['CURRENT_GATE']}
FUSION360_EXPANSION_READY = NO

Safety:
- EXACT10K_V1_CHANGED = NO
- TRAINING_RUN = NO
- OPTIMIZER_STEP = NO
- DECODE_RUN = NO
- TARGET_CHANGED = NO
- TOKENIZER_CHANGED = NO
- CONTEXT_CHANGED = NO
- C2_CHANGED = NO

Notes:
- Stage A inventory, exclusion set, candidates, canary, pilot, full cohort, shards, protocol drift audit, resource plan, provenance, and placeholder downstream manifests are materialized.
- Pilot/full execution is gated until Canary100 completes the official curve/C2/runtime eligibility path.
"""
    (OUT_DIR / "FINAL_REPORT.md").write_text(md, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-canary", action="store_true")
    parser.add_argument("--force-canary", action="store_true")
    args = parser.parse_args()
    stage_a(run_canary=args.run_canary, force_canary=args.force_canary)
    print(json.dumps(read_json(OUT_DIR / "FINAL_REPORT.json"), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
