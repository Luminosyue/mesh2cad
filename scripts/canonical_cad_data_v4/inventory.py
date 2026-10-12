#!/usr/bin/env python3
"""Step 1: source inventory. No conversion."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
REPO_ROOT = SCRIPTS.parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from canonical_cad_data_v4.config import (  # noqa: E402
    AUDIT_DIR,
    CADFS_FEATURESCRIPT,
    CADFS_STEP,
    CADFS_TEXT,
    DEEPCAD_RAW_JSON,
    DEEPCAD_TRAIN,
    FUSION360_570_PASS,
    FUSION360_FAILURES,
    FUSION360_RECON,
    FUSION360_TRAIN,
    HASHES_DIR,
    REPORTS_DIR,
)
from canonical_cad_data_v4.hashutil import file_manifest_entry, sha256_file, write_json  # noqa: E402


def _count_files(root: Path, suffix: str | None = None) -> int:
    if not root.exists():
        return 0
    n = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if suffix is None or name.endswith(suffix):
                n += 1
    return n


def _count_dirs(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for p in root.iterdir() if p.is_dir())


def inventory_deepcad() -> dict:
    raw_n = _count_files(DEEPCAD_RAW_JSON, ".json")
    train_n = _count_dirs(DEEPCAD_TRAIN)
    train_src = train_step = train_stl = 0
    if DEEPCAD_TRAIN.exists():
        for p in DEEPCAD_TRAIN.iterdir():
            if not p.is_dir():
                continue
            if (p / "source.json").exists():
                train_src += 1
            if (p / "model.step").exists():
                train_step += 1
            if (p / "model.stl").exists() or (p / "model.obj").exists():
                train_stl += 1
    converter = Path(__file__).resolve().parent / "converters" / "deepcad_to_dsl.py"
    legacy = REPO_ROOT / "scripts" / "deepcad" / "deepcad_to_dsl.py"
    return {
        "source_name": "DeepCAD",
        "root_path": str(DEEPCAD_RAW_JSON),
        "train_root": str(DEEPCAD_TRAIN),
        "total_files": raw_n,
        "total_candidate_cads": raw_n,
        "program_format": "deepcad_json_sketch_extrude_sequence",
        "step_available": train_step > 0,
        "stl_mesh_available": train_stl > 0,
        "source_program_available": raw_n > 0,
        "estimated_unique_cad_count": raw_n,
        "json_program_count": raw_n,
        "valid_cad_count": {
            "raw_json": raw_n,
            "train_dirs": train_n,
            "train_with_source_json": train_src,
            "train_with_step": train_step,
            "train_with_mesh": train_stl,
        },
        "current_converter_support": {
            "legacy_path": str(legacy),
            "legacy_sha256": sha256_file(legacy) if legacy.exists() else None,
            "v4_isolated_copy": str(converter),
            "v4_fixes": [
                "signed_extent",
                "circle_rect_extent_kwargs",
                "circle_rect_world_origin",
                "no_intersect_silent_skip",
                "no_occ_fallback",
            ],
            "notes": (
                "Full DeepCAD cad_json (~178k) is not present in this workspace. "
                "Inventory uses the local 2500 raw_json subset plus 2209 train samples."
            ),
        },
        "full_dataset_present": False,
    }


def inventory_fusion360() -> dict:
    recon_n = _count_files(FUSION360_RECON, ".json")
    step_n = _count_files(FUSION360_RECON, ".step") + _count_files(FUSION360_RECON, ".stp")
    obj_n = _count_files(FUSION360_RECON, ".obj")
    total_files = _count_files(FUSION360_RECON, None)
    train_n = _count_dirs(FUSION360_TRAIN)
    pass_ids: list[str] = []
    fail_ids: list[str] = []
    if FUSION360_570_PASS.exists():
        data = json.loads(FUSION360_570_PASS.read_text(encoding="utf-8"))
        pass_ids = list(data.get("cad_ids") or [])
    if FUSION360_FAILURES.exists():
        fails = json.loads(FUSION360_FAILURES.read_text(encoding="utf-8"))
        if isinstance(fails, list):
            fail_ids = [r.get("cad_id") for r in fails if r.get("cad_id")]
    v4_conv = Path(__file__).resolve().parent / "converters" / "fusion360_to_dsl.py"
    return {
        "source_name": "Fusion360",
        "root_path": str(FUSION360_RECON),
        "train_root": str(FUSION360_TRAIN),
        "total_files": total_files,
        "total_candidate_cads": recon_n,
        "program_format": "fusion360_reconstruction_json",
        "step_available": step_n > 0,
        "step_file_count": step_n,
        "obj_file_count": obj_n,
        "stl_mesh_available": obj_n > 0,
        "source_program_available": recon_n > 0,
        "estimated_unique_cad_count": recon_n,
        "raw_sequence_count": recon_n,
        "note": (
            "reconstruction/ contains JSON reconstruction sequences plus a larger "
            "STEP/OBJ/PNG/SMT gallery dump. V4 candidates are JSON programs only."
        ),
        "current_v2_fixed_converter_availability": {
            "available": v4_conv.exists(),
            "v4_copy": str(v4_conv),
            "provenance": "copied from scripts/geometry_pack_v2_mesh2cad/placement_v3/fusion360_to_dsl.py",
            "unit_scale": "preserved via fusion_unit_contract (copied)",
            "signed_extrusion": True,
            "symmetric_extrusion": True,
            "height_two": True,
            "two_sided_extrusion": True,
            "circle_rect_fast_path_keeps_extent": True,
        },
        "geometry_pass_570_subset": {
            "available": bool(pass_ids),
            "count": len(pass_ids),
            "path": str(FUSION360_570_PASS),
            "note": "570/602 joint geometry-pass from placement_v3 retest; V4 rebinds cad_id rather than copying old STEP",
        },
        "known_failed_ids": fail_ids,
        "known_failed_count": len(fail_ids),
        "train_processed_count": train_n,
    }


def inventory_cadfs() -> dict:
    fs_n = _count_files(CADFS_FEATURESCRIPT, ".txt")
    step_n = _count_files(CADFS_STEP, ".step")
    if step_n == 0:
        step_n = _count_files(CADFS_STEP, ".stp")
    text_n = _count_files(CADFS_TEXT, ".txt")
    unique_manifest = list(CADFS_FEATURESCRIPT.parent.glob("*unique*")) + list(
        CADFS_FEATURESCRIPT.parent.glob("*overlap*")
    )
    return {
        "source_name": "CADFS",
        "root_path": str(CADFS_FEATURESCRIPT.parent),
        "total_files": fs_n + step_n + text_n,
        "total_candidate_cads": fs_n,
        "program_format": "onshape_featurescript_rp",
        "step_available": step_n > 0,
        "stl_mesh_available": False,
        "source_program_available": fs_n > 0,
        "estimated_unique_cad_count": fs_n,
        "featurescript_available": fs_n > 0,
        "featurescript_count": fs_n,
        "step_count": step_n,
        "stl_available": False,
        "stl_count": 0,
        "operation_metadata_available": True,
        "operation_metadata_note": "operations inferred from FeatureScript calls; no separate op JSON",
        "unique_models_manifest_available": bool(unique_manifest),
        "unique_models_manifest_paths": [str(p) for p in unique_manifest],
        "deepcad_overlap_metadata_available": False,
        "text_annotations_available": text_n > 0,
        "text_annotations_count": text_n,
        "note": "No official unique-model or DeepCAD-overlap manifest shipped with this dump.",
    }


def run_inventory() -> dict:
    deepcad = inventory_deepcad()
    fusion = inventory_fusion360()
    cadfs = inventory_cadfs()
    report = {
        "pipeline_version": "canonical_cad_data_v4",
        "step": "SOURCE_INVENTORY",
        "converted_any_data": False,
        "sources": [deepcad, fusion, cadfs],
        "totals": {
            "total_candidate_cads": (
                deepcad["total_candidate_cads"]
                + fusion["total_candidate_cads"]
                + cadfs["total_candidate_cads"]
            ),
            "DEEPCAD": deepcad["total_candidate_cads"],
            "FUSION360": fusion["total_candidate_cads"],
            "CADFS": cadfs["total_candidate_cads"],
        },
    }
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    HASHES_DIR.mkdir(parents=True, exist_ok=True)
    out1 = AUDIT_DIR / "source_inventory.json"
    out2 = REPORTS_DIR / "01_source_inventory.json"
    write_json(out1, report)
    write_json(out2, report)
    man = {
        "source_inventory": file_manifest_entry(out1),
        "source_inventory_report_copy": file_manifest_entry(out2),
    }
    write_json(HASHES_DIR / "01_source_inventory_sha256.json", man)
    report["outputs"] = man
    return report


def main() -> int:
    report = run_inventory()
    print(json.dumps(report["totals"], indent=2))
    print("SOURCE_INVENTORY written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
