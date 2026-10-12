#!/usr/bin/env python3
"""Read-only CADFS inventory/candidate/body audit for CADFS_OVERFIT100_V1.

This script deliberately reuses the existing V4 FeatureScript converter and
never writes beneath CADFS, train688, Dev50, Test100, or existing V3 roots.
It only creates the isolated Phase A--D evidence required before a canary.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CADFS = ROOT / "CADFS"
OUT = ROOT / "ours3/cadfs_overfit100_v1"
RECORDS = ROOT / "ours3/canonical_cad_data_v4/records"
CONVERTER = ROOT / "scripts/canonical_cad_data_v4/converters/cadfs_to_dsl.py"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def find_count(*args: str) -> int:
    result = subprocess.run(["find", str(CADFS), *args], text=True, capture_output=True, check=True)
    return len([line for line in result.stdout.splitlines() if line])


def source_paths(source_id: str) -> tuple[Path, Path]:
    bucket = source_id[:4]
    return (
        CADFS / "featurescript_rp" / bucket / f"{source_id}.txt",
        CADFS / "step" / bucket / f"{source_id}.step",
    )


def body_audit(step_path: Path) -> dict:
    """Use OCC through CadQuery on the original CADFS STEP, not DSL output."""
    try:
        import cadquery as cq

        imported = cq.importers.importStep(str(step_path))
        # CadQuery's importer returns a Workplane; the OCC topology lives in
        # its contained TopoDS wrapper.  Audit that actual shape, not the
        # Workplane convenience object.
        shape = imported.val()
        solids = list(shape.Solids())
        shells = list(shape.Shells())
        compounds = list(shape.Compounds())
        bb = shape.BoundingBox()
        valid_bbox = all(float(v) > 0 for v in (bb.xlen, bb.ylen, bb.zlen))
        return {
            "body_audit_pass": bool(shape and valid_bbox),
            "solid_count": len(solids),
            "shell_count": len(shells),
            "compound_count": len(compounds),
            # A solid is a topologically connected component for the only
            # admissible first-version case. Multi-body candidates are kept
            # visible rather than split or silently converted.
            "connected_component_count": len(solids) if solids else len(compounds),
            "bbox": [float(bb.xmin), float(bb.ymin), float(bb.zmin), float(bb.xmax), float(bb.ymax), float(bb.zmax)],
            "error": None,
        }
    except Exception as exc:  # evidence, not a reason to mutate source data
        return {
            "body_audit_pass": False,
            "solid_count": None,
            "shell_count": None,
            "compound_count": None,
            "connected_component_count": None,
            "bbox": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    if not CADFS.is_dir():
        raise RuntimeError(f"CADFS root missing: {CADFS}")
    OUT.mkdir(parents=True, exist_ok=True)
    inv_dir, audit_dir, canary_dir = OUT / "inventory", OUT / "audits", OUT / "canary20"
    inv_dir.mkdir(exist_ok=True); audit_dir.mkdir(exist_ok=True); canary_dir.mkdir(exist_ok=True)

    # Inventory uses the actual source hierarchy and makes absent asset types explicit.
    inventory = {
        "EXPERIMENT": "CADFS_OVERFIT100_V1",
        "CADFS_ROOT": str(CADFS),
        "TOTAL_FEATURESCRIPT": find_count("-type", "f", "-name", "*.txt"),
        "TOTAL_STEP": find_count("-type", "f", "-iname", "*.step"),
        "TOTAL_STL": find_count("-type", "f", "-iname", "*.stl"),
        "JSON_OR_ANNOTATION": find_count("-type", "f", "(", "-iname", "*.json", "-o", "-iname", "*.jsonl", "-o", "-iname", "*.csv", ")"),
        "OFFICIAL_STL_STATUS": "NONE",
        "SOURCE_WRITTEN": False,
        "TRAINING_STARTED": False,
        "DORA_STARTED": False,
    }
    # Existing canonical V4 records are evidence of the *existing* supported
    # converter. We use them only to seed a deterministic, auditable candidate
    # pool; final asset construction is still made from original source paths.
    candidates: list[dict] = []
    for rec_dir in sorted(RECORDS.glob("CADFS_*")):
        meta_path = rec_dir / "metadata.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        sid = str(meta.get("source_id", ""))
        fs, step = source_paths(sid)
        dsl = Path(meta.get("canonical_program_path", rec_dir / "canonical/program.dsl"))
        status_clean = meta.get("status") == "clean"
        supported = bool(meta.get("cadfs_audit", {}).get("lossless_candidate")) and status_clean
        unsupported = list(meta.get("cadfs_audit", {}).get("unsupported", []))
        row = {
            "cad_id": f"cadfs__{sid}", "source_id": sid,
            "source_fs_path": str(fs), "source_step_path": str(step), "source_stl_path": None,
            "canonical_dsl_evidence_path": str(dsl),
            "operation_types": meta.get("operations", []),
            "operation_count": int(meta.get("num_operations", 0)),
            "complexity": meta.get("complexity", "unknown"),
            "supported_by_current_dsl": supported,
            "unsupported_reason": None if supported else (",".join(unsupported) or "existing_converter_not_clean"),
            "source_fs_exists": fs.is_file(), "source_step_exists": step.is_file(),
            "canonical_dsl_exists": dsl.is_file(),
        }
        candidates.append(row)
    candidates.sort(key=lambda r: r["source_id"])
    for example in candidates[:5]:
        inventory.setdefault("EXAMPLES", []).append({
            "cad_id": example["cad_id"], "FeatureScript": example["source_fs_path"],
            "STEP": example["source_step_path"], "STL": "NONE",
        })
    inventory.update({
        "TOTAL_CAD": len(candidates),
        "HAS_FEATURESCRIPT": sum(r["source_fs_exists"] for r in candidates),
        "HAS_STEP": sum(r["source_step_exists"] for r in candidates),
        "HAS_STL": 0,
        "HAS_FS_AND_STEP": sum(r["source_fs_exists"] and r["source_step_exists"] for r in candidates),
        "HAS_STEP_AND_STL": 0,
        "CANDIDATE_POOL_PROVENANCE": str(RECORDS),
        "CANDIDATE_ORDER": "lexicographic source_id from existing clean converter evidence",
    })
    write_json(inv_dir / "CADFS_LOCAL_INVENTORY.json", inventory)
    (inv_dir / "CADFS_LOCAL_INVENTORY.md").write_text(
        "# CADFS local inventory\n\n"
        f"- CADFS_ROOT: `{CADFS}`\n- source FeatureScript files: {inventory['TOTAL_FEATURESCRIPT']}\n"
        f"- source STEP files: {inventory['TOTAL_STEP']}\n- source STL files: {inventory['TOTAL_STL']} (NONE)\n"
        f"- deterministic supported-converter candidate evidence: {len(candidates)} existing clean records\n"
        "- No source CADFS file was modified; no Dora or training was started.\n",
        encoding="utf-8",
    )
    provenance = """# CADFS canonical DSL provenance\n\n""" + \
        f"- **CADFS_TARGET_SOURCE:** FeatureScript (`CADFS/featurescript_rp/<bucket>/<id>.txt`)\n" \
        f"- **CANONICAL_DSL_CONVERTER:** `{CONVERTER}`\n" \
        "- **FUNCTION:** `cadfs_to_dsl(text) -> (dsl_text, report)`\n" \
        "- **TARGET:** `cad_target.dsl`; this experiment does not train on raw FeatureScript.\n" \
        "- **Supported lossless subset:** line/circle/rectangle/polygon sketches; extrude; New/Add/Remove body operations; canonical result expression.\n" \
        "- **Unsupported:** revolve, loft, sweep, fillet, chamfer, shell, mirror, pattern, arc, ellipse, bspline, unsupported sketch planes/profile forms.\n" \
        "- The converter must reject unsupported operations; it never approximates them as an Extrude.\n"
    (audit_dir / "CADFS_DSL_PROVENANCE.md").write_text(provenance, encoding="utf-8")

    audited: list[dict] = []
    for i, row in enumerate(candidates, 1):
        eligible_pre_body = all((row["source_fs_exists"], row["source_step_exists"], row["canonical_dsl_exists"], row["supported_by_current_dsl"]))
        row = dict(row)
        row.update(body_audit(Path(row["source_step_path"])) if eligible_pre_body else {
            "body_audit_pass": False, "solid_count": None, "shell_count": None, "compound_count": None,
            "connected_component_count": None, "bbox": None, "error": "PRE_BODY_SOURCE_OR_CONVERTER_REJECT",
        })
        row["single_solid_candidate"] = bool(row["body_audit_pass"] and row["solid_count"] == 1)
        audited.append(row)
        if i % 50 == 0:
            print(f"BODY_AUDIT={i}/{len(candidates)}", flush=True)
    (inv_dir / "CADFS_CANDIDATES.jsonl").write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in audited), encoding="utf-8")
    body_counts = Counter("audit_error" if not r["body_audit_pass"] else ("single" if r["solid_count"] == 1 else ("multi2" if r["solid_count"] == 2 else "multi3plus")) for r in audited)
    body_report = {
        "CADFS_BODY_AUDIT_V1": "PASS" if body_counts["single"] >= 100 else "FAIL_INSUFFICIENT_SINGLE_SOLID",
        "ATTEMPTED": len(audited), "SINGLE_SOLID": body_counts["single"],
        "MULTI_SOLID_2": body_counts["multi2"], "MULTI_SOLID_3_PLUS": body_counts["multi3plus"],
        "AUDIT_ERROR": body_counts["audit_error"],
        "NO_SPLITTING_PERFORMED": True,
        "SINGLE_SOLID_ONLY_POLICY": True,
    }
    write_json(audit_dir / "CADFS_BODY_AUDIT.json", body_report)
    eligible = [r for r in audited if r["single_solid_candidate"]]
    # Deterministic complexity-span ordering: each complexity stratum contributes
    # in lexicographic source order, then leftovers; it never uses outcomes from
    # the canary to replace frozen early selections.
    buckets = {k: [r for r in eligible if r["complexity"] == k] for k in ("simple", "medium", "hard")}
    ordered: list[dict] = []
    idx = {k: 0 for k in buckets}
    while any(idx[k] < len(buckets[k]) for k in buckets):
        for k in ("simple", "medium", "hard"):
            if idx[k] < len(buckets[k]):
                ordered.append(buckets[k][idx[k]]); idx[k] += 1
    seen = {r["source_id"] for r in ordered}
    ordered.extend(r for r in eligible if r["source_id"] not in seen)
    canary = ordered[:20]
    manifest = {
        "EXPERIMENT": "CADFS_OVERFIT100_V1", "CANARY": "CADFS_CANARY20",
        "selection_algorithm": "round_robin(simple,medium,hard) with lexicographic source_id inside each stratum",
        "candidate_order_source": str(inv_dir / "CADFS_CANDIDATES.jsonl"),
        "records": canary, "count": len(canary),
        "sha256_of_ordered_ids": hashlib.sha256("\n".join(r["source_id"] for r in ordered).encode()).hexdigest(),
        "prohibitions": {"training_started": False, "dora_started": False, "official_stl_main_input": False},
    }
    write_json(canary_dir / "CANARY20_MANIFEST.json", manifest)
    phase = {"CURRENT_GATE": "CADFS_PHASE_AD_PASS" if len(eligible) >= 100 else "CADFS_PHASE_AD_FAIL", "candidate_count": len(candidates), "single_solid_eligible": len(eligible), "canary_frozen": len(canary), "next_allowed": "CANARY20_BUILD" if len(eligible) >= 100 else "STOP"}
    write_json(audit_dir / "PHASE_AD_SUMMARY.json", phase)
    print(json.dumps({"inventory": inventory, "body": body_report, "phase": phase}, indent=2))


if __name__ == "__main__":
    main()
