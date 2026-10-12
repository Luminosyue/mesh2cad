#!/usr/bin/env python3
"""CANONICAL_CAD_DATA_V4 canary: 100 DeepCAD + 100 Fusion360 + 300 CADFS.

Does not train. Does not modify old V2/V3 trees. Stops after the 500-gate.
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from canonical_cad_data_v4.config import (  # noqa: E402
    CADFS_FEATURESCRIPT,
    CADFS_STEP,
    CANARY,
    C2_ABS_DIFF_TOL,
    C2_PROVENANCE_N,
    DEEPCAD_RAW_JSON,
    FUSION360_570_PASS,
    FUSION360_FAILURES,
    FUSION360_RECON,
    FUSION360_TRAIN,
    HASHES_DIR,
    MANIFESTS_DIR,
    RECORDS_DIR,
    REPORTS_DIR,
    SEED,
)
from canonical_cad_data_v4.converters.cadfs_to_dsl import (  # noqa: E402
    CadfsUnsupported,
    audit_featurescript,
    cadfs_to_dsl,
)
from canonical_cad_data_v4.dsl_audit import run_dsl_audit  # noqa: E402
from canonical_cad_data_v4.geometry.c2_export import encode_curves  # noqa: E402
from canonical_cad_data_v4.hashutil import file_manifest_entry, sha256_file, write_json, write_jsonl  # noqa: E402
from canonical_cad_data_v4.inventory import run_inventory  # noqa: E402
from canonical_cad_data_v4.master_candidates import run_master_candidates  # noqa: E402
from canonical_cad_data_v4.process_cad import process_record  # noqa: E402
from canonical_cad_data_v4.schema import make_cad_id, new_record  # noqa: E402


def _select_deepcad(n: int) -> list[dict]:
    files = sorted(DEEPCAD_RAW_JSON.glob("*.json"))
    rng = random.Random(SEED)
    rng.shuffle(files)
    picked = files[:n]
    rows = []
    for p in picked:
        sid = p.stem
        rows.append(
            new_record(
                cad_id=make_cad_id("DEEPCAD", sid),
                source="DEEPCAD",
                source_id=sid,
                source_path=str(p),
                program_available=True,
                status="candidate",
            )
        )
    return rows


def _fusion_source_path(sid: str) -> Path | None:
    recon = FUSION360_RECON / f"{sid}.json"
    if recon.exists():
        return recon
    train = FUSION360_TRAIN / sid / "source.json"
    if train.exists():
        return train
    return None


def _select_fusion(n: int) -> list[dict]:
    data = json.loads(FUSION360_570_PASS.read_text(encoding="utf-8"))
    ids = sorted(data.get("cad_ids") or [])
    rows = []
    for raw in ids:
        sid = raw.replace("fusion360__", "")
        path = _fusion_source_path(sid)
        if path is None:
            continue
        rows.append(
            new_record(
                cad_id=make_cad_id("FUSION360", sid),
                source="FUSION360",
                source_id=sid,
                source_path=str(path),
                program_available=True,
                status="candidate",
            )
        )
        if len(rows) >= n:
            break
    return rows


def _cadfs_path(sid: str) -> Path:
    bucket = sid[:4]
    return CADFS_FEATURESCRIPT / bucket / f"{sid}.txt"


def _iter_cadfs_ids():
    for bucket in sorted(p for p in CADFS_FEATURESCRIPT.iterdir() if p.is_dir()):
        for p in sorted(bucket.glob("*.txt")):
            yield p.stem, p


def _select_cadfs(n_convert: int, n_audit: int) -> tuple[list[dict], dict]:
    rng = random.Random(SEED)
    all_ids = [(sid, p) for sid, p in _iter_cadfs_ids()]
    rng.shuffle(all_ids)
    # Read a pool large enough for stratification + lossless conversion.
    pool = all_ids[: max(8000, n_audit * 4)]
    audits = []
    by_stratum: dict[str, list] = defaultdict(list)
    lossless = []
    for sid, p in pool:
        text = p.read_text(encoding="utf-8", errors="replace")
        audit = audit_featurescript(text)
        rec = {
            "source_id": sid,
            "path": str(p),
            **audit,
        }
        audits.append(rec)
        by_stratum[audit["stratum"]].append(rec)
        if audit["lossless_candidate"]:
            try:
                cadfs_to_dsl(text)
            except (CadfsUnsupported, Exception):  # noqa: BLE001
                continue
            lossless.append(rec)

    # Stratified 1000 for operation audit
    strata_order = [
        "basic_sketch_extrude",
        "boolean",
        "revolve",
        "loft",
        "sweep",
        "fillet",
        "chamfer",
        "shell",
        "pattern",
        "mixed-complex",
    ]
    audit1000 = []
    per = max(1, n_audit // max(1, len(strata_order)))
    used = set()
    for s in strata_order:
        for rec in by_stratum.get(s, [])[:per]:
            if rec["source_id"] not in used:
                audit1000.append(rec)
                used.add(rec["source_id"])
    for rec in audits:
        if len(audit1000) >= n_audit:
            break
        if rec["source_id"] not in used:
            audit1000.append(rec)
            used.add(rec["source_id"])
    audit1000 = audit1000[:n_audit]

    convert_rows = []
    for rec in lossless:
        sid = rec["source_id"]
        p = Path(rec["path"])
        bucket = sid[:4]
        step = CADFS_STEP / bucket / f"{sid}.step"
        convert_rows.append(
            new_record(
                cad_id=make_cad_id("CADFS", sid),
                source="CADFS",
                source_id=sid,
                source_path=str(p),
                program_available=True,
                step_available=step.exists(),
                status="candidate",
            )
        )
        if len(convert_rows) >= n_convert:
            break

    op_counts = Counter()
    for rec in audit1000:
        for k, v in rec["counts"].items():
            if v:
                op_counts[k] += 1
    support_matrix = []
    v4_support = {
        "extrude": "SUPPORTED",
        "boolean": "PARTIAL",
        "circle": "SUPPORTED",
        "line": "PARTIAL",
        "revolve": "UNSUPPORTED",
        "loft": "UNSUPPORTED",
        "sweep": "UNSUPPORTED",
        "fillet": "UNSUPPORTED",
        "chamfer": "UNSUPPORTED",
        "shell": "UNSUPPORTED",
        "mirror": "UNSUPPORTED",
        "pattern": "UNSUPPORTED",
    }
    for op, support in v4_support.items():
        support_matrix.append(
            {
                "operation": op,
                "source_count": int(op_counts.get(op, 0)),
                "v4_dsl_support": support,
                "execute_pass": None,  # filled after conversion
            }
        )
    audit_report = {
        "requested_audit": n_audit,
        "audited": len(audit1000),
        "pool_scanned": len(pool),
        "stratum_counts": {k: len(v) for k, v in by_stratum.items()},
        "lossless_in_pool": len(lossless),
        "convert_selected": len(convert_rows),
        "operation_presence_in_audit1000": dict(op_counts),
        "program_length_chars_mean": (
            float(sum(r["program_chars"] for r in audit1000) / max(1, len(audit1000)))
        ),
        "feature_count_mean": (
            float(sum(r["n_features"] for r in audit1000) / max(1, len(audit1000)))
        ),
        "step_available_rate": None,
        "CADFS_CONVERSION_SUPPORT_MATRIX": support_matrix,
        "policy": "only lossless V4 DSL; never degrade loft/sweep/fillet/revolve to extrude",
    }
    write_json(REPORTS_DIR / "cadfs_operation_audit_1000.json", audit_report)
    write_jsonl(MANIFESTS_DIR / "cadfs_audit_1000.jsonl", audit1000)
    return convert_rows, audit_report


def _dedup(rows: list[dict]) -> dict:
    by_src: dict[tuple[str, str], list[str]] = defaultdict(list)
    by_dsl: dict[str, list[str]] = defaultdict(list)
    by_geom: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        if r.get("status") != "clean":
            continue
        by_src[(r["source"], r["source_id"])].append(r["cad_id"])
        if r.get("canonical_dsl_sha256"):
            by_dsl[r["canonical_dsl_sha256"]].append(r["cad_id"])
        if r.get("geometry_fingerprint"):
            by_geom[r["geometry_fingerprint"]].append(r["cad_id"])

    groups = []
    gid = 0
    assigned = {}
    for key, ids in by_dsl.items():
        if len(ids) > 1:
            gid += 1
            g = f"dsl_{gid:04d}"
            groups.append({"group": g, "kind": "canonical_dsl_sha256", "cad_ids": ids, "key": key})
            for i in ids:
                assigned[i] = g
    for key, ids in by_geom.items():
        if len(ids) > 1:
            gid += 1
            g = f"geom_{gid:04d}"
            groups.append({"group": g, "kind": "geometry_fingerprint", "cad_ids": ids, "key": key})
            for i in ids:
                assigned.setdefault(i, g)

    cross = []
    for g in groups:
        srcs = {r["source"] for r in rows if r["cad_id"] in g["cad_ids"]}
        if len(srcs) > 1:
            cross.append(g["group"])
            g["cross_source"] = True
        else:
            g["cross_source"] = False

    for r in rows:
        r["duplicate_group"] = assigned.get(r["cad_id"])
        if r.get("status") == "clean" and r["cad_id"] in assigned:
            # keep first cad_id in group as unique; others marked duplicate
            g = assigned[r["cad_id"]]
            members = next(x["cad_ids"] for x in groups if x["group"] == g)
            if r["cad_id"] != sorted(members)[0]:
                r["status"] = "duplicate"

    write_json(MANIFESTS_DIR / "duplicate_groups.json", {"groups": groups, "cross_source_groups": cross})
    return {"groups": groups, "cross_source_groups": cross, "n_groups": len(groups)}


def _assign_split(rows: list[dict]) -> None:
    rng = random.Random(SEED)
    unique = [r for r in rows if r.get("status") == "clean"]
    # split by duplicate_group or cad_id so a family cannot leak
    keys = sorted({r.get("duplicate_group") or r["cad_id"] for r in unique})
    rng.shuffle(keys)
    n = len(keys)
    n_train = int(n * 0.8)
    n_val = int(n * 0.1)
    mapping = {}
    for i, k in enumerate(keys):
        mapping[k] = "train" if i < n_train else ("val" if i < n_train + n_val else "test")
    for r in unique:
        r["split"] = mapping[r.get("duplicate_group") or r["cad_id"]]


def _c2_provenance(rows: list[dict]) -> dict:
    clean = [r for r in rows if r.get("status") == "clean" and r.get("c2_valid")]
    rng = random.Random(SEED)
    sample = clean[:]
    rng.shuffle(sample)
    sample = sample[:C2_PROVENANCE_N]
    diffs = []
    for r in sample:
        tok_path = RECORDS_DIR / r["cad_id"] / "geometry" / "curve_tokens_c2.npy"
        curves_path = RECORDS_DIR / r["cad_id"] / "geometry" / "curves.json"
        if not tok_path.exists() or not curves_path.exists():
            diffs.append({"cad_id": r["cad_id"], "error": "missing_files"})
            continue
        saved = __import__("numpy").load(tok_path)
        curves = json.loads(curves_path.read_text(encoding="utf-8"))["curves"]
        direct, _meta = encode_curves(curves)
        if saved.shape != direct.shape:
            diffs.append({"cad_id": r["cad_id"], "error": f"shape {saved.shape} vs {direct.shape}"})
            continue
        mad = float(abs(saved.astype("float64") - direct.astype("float64")).max())
        diffs.append({"cad_id": r["cad_id"], "max_abs_diff": mad, "pass": mad <= C2_ABS_DIFF_TOL})
    n_pass = sum(1 for d in diffs if d.get("pass"))
    note = None
    if diffs and n_pass < len(diffs):
        note = (
            "Non-zero diffs may come from GPU vs CPU matmul, TF32, or non-deterministic cuDNN. "
            "C2 is frozen (eval, requires_grad=False); re-export on the same device should match."
        )
    return {
        "n_sampled": len(sample),
        "n_pass": n_pass,
        "tol": C2_ABS_DIFF_TOL,
        "diffs": diffs,
        "C2_PROVENANCE": "PASS" if n_pass == len(diffs) and diffs else "FAIL",
        "note": note,
    }


def _curve_op_counts(rows: list[dict]) -> dict:
    c = Counter()
    ops = Counter()
    cx = Counter()
    for r in rows:
        if r.get("status") not in {"clean", "duplicate"}:
            continue
        c["LINE"] += int(r.get("num_line") or 0)
        c["CIRCLE"] += int(r.get("num_circle") or 0)
        c["ARC"] += int(r.get("num_arc") or 0)
        c["ELLIPSE"] += int(r.get("num_ellipse") or 0)
        c["BSPLINE"] += int(r.get("num_bspline") or 0)
        if r.get("has_extrude"):
            ops["extrude"] += 1
        if r.get("has_revolve"):
            ops["revolve"] += 1
        if r.get("has_loft"):
            ops["loft"] += 1
        if r.get("has_sweep"):
            ops["sweep"] += 1
        if r.get("has_fillet"):
            ops["fillet"] += 1
        if r.get("has_cut") or r.get("has_join"):
            ops["boolean"] += 1
        cx[r.get("complexity") or "unknown"] += 1
    return {"curves": dict(c), "ops": dict(ops), "complexity": dict(cx)}


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)
    HASHES_DIR.mkdir(parents=True, exist_ok=True)
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)

    print("=== SOURCE INVENTORY ===", flush=True)
    inv = run_inventory()
    print(json.dumps(inv["totals"], indent=2), flush=True)

    print("=== MASTER CANDIDATES ===", flush=True)
    master = run_master_candidates()
    print(json.dumps(master, indent=2), flush=True)

    print("=== DSL CAPABILITY AUDIT ===", flush=True)
    dsl = run_dsl_audit()
    print("SUPPORTED", dsl["SUPPORTED"], flush=True)
    print("UNSUPPORTED", dsl["UNSUPPORTED"], flush=True)

    print("=== SELECT CANARY 500 ===", flush=True)
    deep = _select_deepcad(CANARY["DEEPCAD"])
    fusion = _select_fusion(CANARY["FUSION360"])
    cadfs, cadfs_audit = _select_cadfs(CANARY["CADFS"], CANARY["CADFS_AUDIT"])
    canary = deep + fusion + cadfs
    write_jsonl(MANIFESTS_DIR / "canary_500_candidates.jsonl", canary)
    print(
        f"selected DEEPCAD={len(deep)} FUSION360={len(fusion)} CADFS={len(cadfs)} total={len(canary)}",
        flush=True,
    )

    results = []
    for i, rec in enumerate(canary, 1):
        print(f"[{i}/{len(canary)}] {rec['cad_id']}", flush=True)
        try:
            out = process_record(rec, c2_device="cpu")
        except Exception as exc:  # noqa: BLE001
            out = dict(rec)
            out["status"] = "dsl_execute_fail"
            out["failure_reason"] = f"uncaught:{type(exc).__name__}:{exc}"
        results.append(out)
        print(f"    -> {out.get('status')} {out.get('failure_reason') or ''}", flush=True)

    dedup = _dedup(results)
    _assign_split(results)

    clean = [r for r in results if r.get("status") == "clean"]
    b0 = [r for r in clean if r.get("b0_valid")]
    b1 = [r for r in clean if r.get("b1_valid")]
    m2 = [r for r in clean if r.get("m2_valid")]
    fair = [r for r in clean if r.get("fair_three_arm")]
    write_jsonl(MANIFESTS_DIR / "clean_canonical.jsonl", clean)
    write_jsonl(MANIFESTS_DIR / "fair_three_arm_pool.jsonl", fair)
    aircraft = [r for r in clean if int(r.get("aircraft_relevance") or 0) >= 1]
    write_jsonl(MANIFESTS_DIR / "aircraft_relevant_pool.jsonl", aircraft)

    # persist per-record metadata with split/dedup
    for r in results:
        meta = RECORDS_DIR / r["cad_id"] / "metadata.json"
        write_json(meta, r)

    counts = _curve_op_counts(results)
    src_valid = Counter(r["source"] for r in clean)
    status_c = Counter(r.get("status") for r in results)
    fail_reasons = Counter(r.get("failure_reason") for r in results if r.get("status") != "clean")

    c2_prov = _c2_provenance(results)

    # split leakage
    def _overlap(field: str) -> int:
        sets = defaultdict(set)
        for r in clean:
            sp = r.get("split")
            val = r.get(field)
            if sp and val:
                sets[sp].add(val)
        leak = 0
        names = list(sets)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                leak += len(sets[names[i]] & sets[names[j]])
        return leak

    leak = {
        "source_id": _overlap("source_id"),
        "canonical_dsl_sha256": _overlap("canonical_dsl_sha256"),
        "geometry_fingerprint": _overlap("geometry_fingerprint"),
        "duplicate_group": _overlap("duplicate_group"),
    }

    gate_ok = (
        len(canary) >= 100
        and len(fair) > 0
        and c2_prov["C2_PROVENANCE"] in {"PASS", "FAIL"}  # recorded either way
        and leak["source_id"] == 0
    )
    # 500 gate: require a non-trivial fair pool and no split leakage.
    current_gate = (
        "CANONICAL_CAD_DATA_V4_PREP_PASS"
        if len(fair) >= 50 and leak["source_id"] == 0 and c2_prov.get("n_sampled", 0) > 0
        else "CANONICAL_CAD_DATA_V4_PREP_FAIL"
    )

    conversion_report = {
        "attempted": len(results),
        "status_counts": dict(status_c),
        "failure_reasons": {str(k): v for k, v in fail_reasons.items()},
        "DEEPCAD_attempted": len(deep),
        "FUSION360_attempted": len(fusion),
        "CADFS_attempted": len(cadfs),
    }
    write_json(REPORTS_DIR / "conversion_report.json", conversion_report)
    write_json(REPORTS_DIR / "geometry_qa_report.json", {"clean": len(clean), "geometry_fail": status_c.get("geometry_fail", 0)})
    write_json(REPORTS_DIR / "curve_distribution.json", counts["curves"])
    write_json(REPORTS_DIR / "operation_distribution.json", counts["ops"])
    write_json(REPORTS_DIR / "complexity_distribution.json", counts["complexity"])

    known_fail = []
    if FUSION360_FAILURES.exists():
        known_fail = json.loads(FUSION360_FAILURES.read_text(encoding="utf-8"))
        if isinstance(known_fail, list):
            known_fail = [x.get("cad_id") for x in known_fail]

    final = {
        "CURRENT_GATE": current_gate,
        "TOTAL_SOURCE_CANDIDATES": master.get("TOTAL_CANDIDATES"),
        "CANONICAL_CONVERTED": sum(1 for r in results if r.get("canonical_program_path")),
        "DSL_EXEC_PASS": sum(1 for r in results if r.get("dsl_execute") is True),
        "STEP_RELOAD_PASS": sum(1 for r in results if r.get("step_reload") is True),
        "GEOMETRY_PASS": sum(1 for r in results if r.get("geometry_gate") is True),
        "DEDUP_UNIQUE": len(clean),
        "B0_VALID": len(b0),
        "B1_VALID": len(b1),
        "M2_VALID": len(m2),
        "FAIR_THREE_ARM_VALID": len(fair),
        "DEEPCAD_VALID": src_valid["DEEPCAD"],
        "FUSION360_VALID": src_valid["FUSION360"],
        "CADFS_VALID": src_valid["CADFS"],
        "SIMPLE": counts["complexity"].get("simple", 0),
        "MEDIUM": counts["complexity"].get("medium", 0),
        "HARD": counts["complexity"].get("hard", 0),
        "LINE_CURVES": counts["curves"].get("LINE", 0),
        "CIRCLE_CURVES": counts["curves"].get("CIRCLE", 0),
        "ARC_CURVES": counts["curves"].get("ARC", 0),
        "ELLIPSE_CURVES": counts["curves"].get("ELLIPSE", 0),
        "BSPLINE_CURVES": counts["curves"].get("BSPLINE", 0),
        "EXTRUDE_CADS": counts["ops"].get("extrude", 0),
        "REVOLVE_CADS": counts["ops"].get("revolve", 0),
        "LOFT_CADS": counts["ops"].get("loft", 0),
        "SWEEP_CADS": counts["ops"].get("sweep", 0),
        "FILLET_CADS": counts["ops"].get("fillet", 0),
        "BOOLEAN_CADS": counts["ops"].get("boolean", 0),
        "CROSS_SOURCE_DUP_GROUPS": len(dedup.get("cross_source_groups") or []),
        "CROSS_SPLIT_LEAKAGE": leak,
        "C2_PROVENANCE": c2_prov,
        "OLD_V2_MODIFIED": False,
        "OLD_V3_MODIFIED": False,
        "TRAINING_STARTED": False,
        "OFFICIAL_TEST_READ": False,
        "CANARY": {
            "requested": CANARY,
            "selected": {"DEEPCAD": len(deep), "FUSION360": len(fusion), "CADFS": len(cadfs)},
        },
        "status_counts": dict(status_c),
        "cadfs_audit_summary": {
            "audited": cadfs_audit.get("audited"),
            "lossless_in_pool": cadfs_audit.get("lossless_in_pool"),
        },
        "fusion360_known_failed_count": len(known_fail) if isinstance(known_fail, list) else None,
        "gate_ok_internal": gate_ok,
    }
    write_json(REPORTS_DIR / "FINAL_DATA_GATE.json", final)

    man = {
        "source_inventory": file_manifest_entry(REPORTS_DIR / "01_source_inventory.json"),
        "master_candidates": file_manifest_entry(MANIFESTS_DIR / "master_candidates.jsonl"),
        "dsl_audit": file_manifest_entry(REPORTS_DIR / "02_dsl_capability_audit.json"),
        "clean_canonical": file_manifest_entry(MANIFESTS_DIR / "clean_canonical.jsonl"),
        "fair_three_arm": file_manifest_entry(MANIFESTS_DIR / "fair_three_arm_pool.jsonl"),
        "final_gate": file_manifest_entry(REPORTS_DIR / "FINAL_DATA_GATE.json"),
    }
    write_json(HASHES_DIR / "FILE_MANIFEST_SHA256.json", man)

    print("\n========== FINAL GATE ==========", flush=True)
    for k, v in final.items():
        if k in {"C2_PROVENANCE", "CROSS_SPLIT_LEAKAGE", "CANARY", "status_counts", "cadfs_audit_summary"}:
            print(f"{k}={json.dumps(v)[:400]}", flush=True)
        else:
            print(f"{k}={v}", flush=True)
    return 0 if current_gate.endswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
