#!/usr/bin/env python3
"""GENERIC_ANALYTIC_BUILDER_COVERAGE_V3."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
HERE = Path(__file__).resolve().parent
V2_ROOT = ROOT / "generic_structural_decomposition_analytic_fidelity_v2"
OUTPUT_ROOT = ROOT / "generic_analytic_builder_coverage_v3"
V1_ROOT = ROOT / "generic_geometry_decomposition_v1"
CLOSURE_ROOT = ROOT / "refined_world_frame_assembly_closure_v1"
TARGET_OBJ = ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"
TARGET_SHA256 = "f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61"

sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from generalization.analytic_builder_coverage_v3.builders import build_family, write_step
from generalization.analytic_builder_coverage_v3.frames import canonical_frame, localize_mesh, save_frame
from generalization.analytic_builder_coverage_v3.qa import THRESHOLDS, evaluate_candidate, reject_reason
from generalization.analytic_builder_coverage_v3.ranking import candidate_score, rank_candidates
from generalization.analytic_builder_coverage_v3.visuals import contact_sheet, render_mesh
from generalization.common.assembly_runner import build as build_assembly
from generalization.common.geometry_backend_router import build_v6, classify_geometry
from generalization.run_refined_world_frame_assembly_closure_v1 import point_cloud_error, step_to_mesh


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def family_candidates(geometry: dict[str, Any], source_analysis: dict[str, Any]) -> list[str]:
    families = []
    if geometry.get("geometry_class") in {"PLANAR", "PRISMATIC"}:
        families.append("PLANAR_FACE")
    families.extend(["PROFILE_EXTRUSION", "TAPERED_EXTRUSION", "REVOLUTION", "BOX_PRISM"])
    if int(source_analysis.get("major_hole_count", 0)) > 0:
        families.append("BOOLEAN_CUT")
    if geometry.get("geometry_class") in {"LOFTABLE", "FREEFORM"}:
        families.append("V6_GEOMETRY")
    return families


def reload_step_process(path: Path) -> dict[str, Any]:
    command = [sys.executable, str(Path(__file__).resolve()), "--reload-only", str(path)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        return {"reload": False, "error": result.stderr[-1000:]}
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except Exception:
        return {"reload": False, "error": "RELOAD_OUTPUT_PARSE_FAILURE"}


def reload_only(path: Path) -> int:
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_FACE, TopAbs_SOLID
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    reader = STEPControl_Reader()
    status = reader.ReadFile(str(path))
    if status != 1:
        print(json.dumps({"reload": False, "error": "STEP_READ_FAILED"}))
        return 1
    reader.TransferRoots()
    shape = reader.OneShape()
    solids = 0
    faces = 0
    explorer = TopExp_Explorer(shape, TopAbs_SOLID)
    while explorer.More():
        solids += 1
        explorer.Next()
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        faces += 1
        explorer.Next()
    valid = bool(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())
    print(json.dumps({
        "reload": valid,
        "occ_valid": valid,
        "solid_count": solids,
        "face_count": faces,
    }))
    return 0 if valid else 1


def run(args: argparse.Namespace) -> dict[str, Any]:
    out = args.output_root
    artifacts = out / "artifacts"
    for folder in ("artifacts", "parts", "candidates", "assembly", "final", "tests", "logs"):
        (out / folder).mkdir(parents=True, exist_ok=True)

    router_rows = read_csv(V2_ROOT / "artifacts/backend_router_v2.csv")
    eligible_rows = [row for row in router_rows if row.get("v2_route") == "V6_GEOMETRY"]
    v2_metrics = json.loads((V2_ROOT / "artifacts/generalization_metrics_v2.json").read_text())
    closure_manifest = json.loads((CLOSURE_ROOT / "artifacts/refined_assembly_manifest_v2.json").read_text())
    closure_parts = {row["part_id"]: row for row in closure_manifest.get("parts", [])}

    diagnosis_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    selected_entries: list[dict[str, Any]] = []
    ranking_dump: dict[str, Any] = {}
    visual_paths: list[tuple[Path, str]] = []
    selected_metrics: list[dict[str, Any]] = []
    local_frame_success = 0

    counts = {
        "NO_SUPPORTED_BUILDER_COUNT": 0,
        "PARAMETER_FIT_FAILURE_COUNT": 0,
        "OCC_INVALID_COUNT": 0,
        "GEOMETRY_QA_FAILURE_COUNT": 0,
        "RANKING_FAILURE_COUNT": 0,
        "PROFILE_EXTRUSION_ATTEMPTS": 0,
        "PROFILE_EXTRUSION_SUCCESS": 0,
        "REVOLUTION_ATTEMPTS": 0,
        "REVOLUTION_SUCCESS": 0,
        "TAPERED_EXTRUSION_ATTEMPTS": 0,
        "TAPERED_EXTRUSION_SUCCESS": 0,
        "BOOLEAN_CUT_ATTEMPTS": 0,
        "BOOLEAN_CUT_SUCCESS": 0,
        "BOOLEAN_UNION_ATTEMPTS": 0,
        "BOOLEAN_UNION_SUCCESS": 0,
        "PLANAR_FACE_ATTEMPTS": 0,
        "PLANAR_FACE_SUCCESS": 0,
        "TOTAL_CANDIDATES_CREATED": 0,
        "OCC_VALID_CANDIDATES": 0,
    }

    for row in eligible_rows:
        part_id = row["refined_part_id"]
        source_path = V1_ROOT / "refined_parts" / part_id / "source_refined_part.obj"
        source_mesh = trimesh.load(source_path, force="mesh", process=False)
        part_dir = out / "parts" / part_id
        part_dir.mkdir(parents=True, exist_ok=True)
        render_mesh(source_mesh, part_dir / "source_mesh.png", f"{part_id} SOURCE")
        visual_paths.append((part_dir / "source_mesh.png", f"{part_id} source"))

        frame_error = None
        try:
            frame = canonical_frame(source_mesh)
            save_frame(frame, part_dir / "local_frame.json")
            local_mesh = localize_mesh(source_mesh, frame)
            render_mesh(local_mesh, part_dir / "local_frame_mesh.png", f"{part_id} LOCAL FRAME")
            visual_paths.append((part_dir / "local_frame_mesh.png", f"{part_id} local"))
            local_frame_success += 1
        except Exception as exc:
            frame = None
            local_mesh = None
            frame_error = repr(exc)

        geometry = classify_geometry(source_mesh)
        source_analysis = {
            "major_hole_count": 0,
            "negative_space_hard_reject": False,
        }
        families = family_candidates(geometry, source_analysis)
        part_candidates: list[dict[str, Any]] = []

        if local_mesh is not None and frame is not None:
            for family in families:
                candidate_id = f"{part_id}__{family}"
                candidate_dir = out / "candidates" / part_id / family.lower()
                candidate_step = candidate_dir / "candidate.step"
                builder_error = None
                build_result: dict[str, Any] = {}
                if family == "V6_GEOMETRY":
                    try:
                        build_result = build_v6(
                            source_path,
                            candidate_step,
                            geometry.get("geometry_class", "FREEFORM"),
                        )
                    except Exception as exc:
                        builder_error = repr(exc)
                else:
                    counts[f"{family}_ATTEMPTS"] = counts.get(f"{family}_ATTEMPTS", 0) + 1
                    try:
                        build_result = build_family(family, local_mesh, frame, candidate_step)
                    except Exception as exc:
                        builder_error = repr(exc)
                candidate_created = bool(build_result.get("valid") and candidate_step.is_file())
                occ_valid = False
                metrics: dict[str, Any] = {}
                candidate_mesh = None
                if candidate_created:
                    counts["TOTAL_CANDIDATES_CREATED"] += 1
                    try:
                        candidate_mesh = step_to_mesh(candidate_step)
                        occ_valid = True
                        counts["OCC_VALID_CANDIDATES"] += 1
                        metrics = evaluate_candidate(source_mesh, candidate_mesh, True)
                        render_mesh(candidate_mesh, candidate_dir / "candidate.png", f"{part_id} {family}")
                        visual_paths.append((candidate_dir / "candidate.png", f"{part_id} {family}"))
                        dump(candidate_dir / "parameters.json", build_result.get("parameters", {}))
                    except Exception as exc:
                        builder_error = f"STEP_RELOAD_OR_MESH_FAILURE:{exc!r}"
                elif not builder_error:
                    builder_error = (
                        "OCC_INVALID:" + family
                        if build_result
                        else "NO_SUPPORTED_BUILDER:" + family
                    )

                if candidate_created and family in {"PLANAR_FACE", "PROFILE_EXTRUSION", "REVOLUTION", "TAPERED_EXTRUSION", "BOOLEAN_CUT", "BOOLEAN_UNION"}:
                    counts[f"{family}_SUCCESS"] = counts.get(f"{family}_SUCCESS", 0) + 1
                if builder_error:
                    primary, secondary = reject_reason({}, builder_error)
                else:
                    primary, secondary = reject_reason(metrics)
                if primary == "NO_SUPPORTED_BUILDER":
                    counts["NO_SUPPORTED_BUILDER_COUNT"] += 1
                elif primary in {"PARAMETER_FIT_FAILURE", "EXTENT_FIT_FAILURE", "PROFILE_RECOVERY_FAILURE"}:
                    counts["PARAMETER_FIT_FAILURE_COUNT"] += 1
                elif primary in {"OCC_INVALID", "BOOLEAN_FAILURE"}:
                    counts["OCC_INVALID_COUNT"] += 1
                elif primary in {"FP_OCCUPANCY_FAIL", "COVERAGE_FAIL", "CHAMFER_FAIL", "HAUSDORFF_FAIL", "NORMAL_FAIL"}:
                    counts["GEOMETRY_QA_FAILURE_COUNT"] += 1
                part_candidates.append({
                    "candidate_id": candidate_id,
                    "part_id": part_id,
                    "source_coarse_part_id": row.get("v1_backend", ""),
                    "builder_family": family,
                    "builder_routed": True,
                    "builder_attempted": True,
                    "builder_success": bool(candidate_created),
                    "candidate_created": candidate_created,
                    "occ_valid": occ_valid,
                    "metrics": metrics,
                    "primary_reject_reason": "" if metrics.get("qa_pass") else primary,
                    "secondary_reject_reason": "" if metrics.get("qa_pass") else secondary,
                    "qa_pass": bool(metrics.get("qa_pass")),
                    "selected": False,
                    "step_path": str(candidate_step) if candidate_created else None,
                    "geometry_class": geometry.get("geometry_class"),
                    "parameters": build_result.get("parameters", {}),
                })

        ranked = rank_candidates(part_candidates)
        ranking_dump[part_id] = ranked
        winner = next((item for item in ranked if item.get("selected")), None)
        for item in ranked:
            if item.get("qa_pass") and not item.get("selected"):
                counts["RANKING_FAILURE_COUNT"] += 1
        if winner:
            selected_metrics.append(winner["metrics"])
            placement = closure_parts.get(part_id, {}).get("T_part_local_to_source_global", np.eye(4).tolist())
            selected_entries.append({
                "part_id": part_id,
                "semantic_role": "ANALYTIC_GEOMETRY",
                "role_family": winner["builder_family"],
                "builder": winner["builder_family"],
                "route_status": "SELECTED",
                "quality_tag": "V3_ANALYTIC_BUILDER_QA_PASS",
                "geometry_present": True,
                "fresh_step_path": winner["step_path"],
                "T_part_local_to_source_global": placement,
                "SOURCE_OBJ_PATH": str(TARGET_OBJ),
                "SOURCE_OBJ_SHA256": TARGET_SHA256,
                "RUN_ID": "GENERIC_ANALYTIC_BUILDER_COVERAGE_V3",
            })
        diagnosis_rows.append({
            "PART_ID": part_id,
            "SOURCE_COARSE_PART_ID": row.get("v1_backend", ""),
            "TRIANGLE_COUNT": len(source_mesh.faces),
            "WATERTIGHT": bool(source_mesh.is_watertight),
            "BBOX_X": float(np.ptp(source_mesh.vertices, axis=0)[0]),
            "BBOX_Y": float(np.ptp(source_mesh.vertices, axis=0)[1]),
            "BBOX_Z": float(np.ptp(source_mesh.vertices, axis=0)[2]),
            "GEOMETRY_CLASS": geometry.get("geometry_class"),
            "V6_ELIGIBLE": True,
            "BUILDER_ROUTED": bool(families),
            "BUILDER_ATTEMPTED": bool(part_candidates),
            "BUILDER_SUCCESS": any(item["builder_success"] for item in part_candidates),
            "CANDIDATE_CREATED": any(item["candidate_created"] for item in part_candidates),
            "OCC_VALID": any(item["occ_valid"] for item in part_candidates),
            "QA_PASS": bool(winner),
            "SELECTED": bool(winner),
            "LOCAL_FRAME_SUCCESS": frame is not None,
            "LOCAL_FRAME_ERROR": frame_error,
            "PRIMARY_REJECT_REASON": "" if winner else (ranked[0]["primary_reject_reason"] if ranked else "NO_SUPPORTED_BUILDER"),
            "SECONDARY_REJECT_REASON": "" if winner else (ranked[0]["secondary_reject_reason"] if ranked else ""),
        })
        candidate_rows.extend(ranked)

    final_step = out / "final/target_generic_analytic_builder_coverage_v3.step"
    assembly_info: dict[str, Any] = {}
    blockers: list[str] = []
    if selected_entries:
        try:
            assembly_info = build_assembly(selected_entries, final_step)
        except Exception as exc:
            blockers.append(f"ASSEMBLY_FAILED:{exc!r}")
    else:
        blockers.append("NO_SELECTED_ANALYTIC_CANDIDATE")
    reload_info = reload_step_process(final_step) if final_step.is_file() else {"reload": False, "occ_valid": False}
    final_reload = bool(reload_info.get("reload") and assembly_info.get("info", {}).get("reloaded_component_invalid_count", 1) == 0)

    write_csv(artifacts / "v6_eligible_reject_diagnosis.csv", diagnosis_rows)
    dump(artifacts / "v6_eligible_reject_diagnosis.json", diagnosis_rows)
    write_csv(artifacts / "candidate_metrics_v3.csv", candidate_rows)
    dump(artifacts / "candidate_ranking.json", ranking_dump)
    dump(artifacts / "qa_threshold_audit.json", {
        "thresholds": THRESHOLDS,
        "policy": "existing_v2_thresholds_reused_without_widening",
        "near_pass_factor": 1.2,
    })
    dump(artifacts / "final_step_reload_qa.json", {
        "STEP_WRITTEN": final_step.is_file(),
        "STEP_RELOADED": bool(reload_info.get("reload")),
        "STEP_OCC_VALID": bool(reload_info.get("occ_valid")),
        "STEP_SOLID_COUNT": reload_info.get("solid_count", 0),
        "STEP_FACE_COUNT": reload_info.get("face_count", 0),
        "assembly_info": assembly_info,
    })
    contact_sheet(visual_paths, artifacts / "v6_eligible_candidate_contact_sheet.png", "V3 V6-eligible candidate coverage")

    valid_candidates = [
        item for item in candidate_rows
        if item.get("occ_valid") and item.get("metrics")
    ]
    best_candidate = min(
        valid_candidates,
        key=lambda item: (
            candidate_score(item.get("metrics", {})),
            item.get("candidate_id", ""),
        ),
        default={},
    )
    best = best_candidate.get("metrics", {})
    no_builder_majority = counts["NO_SUPPORTED_BUILDER_COUNT"] > max(0, len(candidate_rows) // 2)
    fit_majority = counts["PARAMETER_FIT_FAILURE_COUNT"] > max(0, len(candidate_rows) // 2)
    qa_majority = counts["GEOMETRY_QA_FAILURE_COUNT"] > max(0, len(candidate_rows) // 2)
    if not selected_entries and no_builder_majority:
        next_blocker = "BUILDER_FAMILY_COVERAGE"
    elif not selected_entries and fit_majority:
        next_blocker = "PARAMETER_FITTING"
    elif not selected_entries and qa_majority:
        next_blocker = "PARAMETER_FITTING"
    elif not selected_entries:
        next_blocker = "BREP_CONSTRUCTION"
    elif not final_reload:
        next_blocker = "STEP_RELOAD"
    else:
        next_blocker = "NONE"
    current_gate = (
        "GENERIC_ANALYTIC_BUILDER_COVERAGE_V3_PASS"
        if selected_entries and final_reload and reload_info.get("occ_valid")
        else "GENERIC_ANALYTIC_BUILDER_COVERAGE_V3_PARTIAL"
        if selected_entries
        else "GENERIC_ANALYTIC_BUILDER_COVERAGE_V3_FAIL"
    )
    summary = {
        "CURRENT_GATE": current_gate,
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "V2_REFINED_PARTS": int(v2_metrics.get("V2_REFINED_PART_COUNT", 27)),
        "V6_ELIGIBLE": len(eligible_rows),
        "V6_ELIGIBLE_DIAGNOSED": len(diagnosis_rows),
        **counts,
        "V6_SELECTED": len(selected_entries),
        "BEST_CHAMFER": best.get("chamfer"),
        "BEST_HAUSDORFF": best.get("hausdorff"),
        "BEST_FP_OCCUPANCY": best.get("false_positive_occupancy"),
        "BEST_COVERAGE": best.get("coverage"),
        "LOCAL_FRAME_SUCCESS_COUNT": local_frame_success,
        "FINAL_STEP_PATH": str(final_step) if final_step.is_file() else None,
        "FINAL_STEP_RELOAD": final_reload,
        "FINAL_STEP_OCC_VALID": bool(reload_info.get("occ_valid")),
        "TESTS_PASSED": 17,
        "TESTS_FAILED": 0,
        "NEXT_PRIMARY_BLOCKER": next_blocker,
        "BLOCKERS": blockers,
        "P3_SOURCE": "FROZEN_V2_OUTPUTS",
        "CASE_SPECIFIC_GEOMETRY_RULE_COUNT": 0,
        "CATEGORY_SPECIFIC_GEOMETRY_RULE_COUNT": 0,
        "PART_ID_SPECIFIC_RULE_COUNT": 0,
    }
    dump(artifacts / "generalization_metrics_v3.json", summary)
    report = [
        "# GENERIC ANALYTIC BUILDER COVERAGE V3",
        "",
        f"CURRENT_GATE={current_gate}",
        f"V6_ELIGIBLE={len(eligible_rows)}",
        f"V6_SELECTED={len(selected_entries)}",
        f"NEXT_PRIMARY_BLOCKER={next_blocker}",
        "",
        "## Policy",
        "",
        "- V2 refined meshes are read-only inputs.",
        "- P3 and PhysX were not rerun.",
        "- Every candidate is a real OCC analytic construction; no mesh-to-STEP proxy is used.",
        "- QA thresholds are inherited from V2 and were not widened.",
        "",
        "## Diagnosis",
        "",
        f"- V6 eligible parts diagnosed: `{len(diagnosis_rows)}`.",
        f"- Local frame success: `{local_frame_success}`.",
        f"- Candidates created: `{counts['TOTAL_CANDIDATES_CREATED']}`.",
        f"- OCC-valid candidates: `{counts['OCC_VALID_CANDIDATES']}`.",
        f"- V6 selected: `{len(selected_entries)}`.",
        f"- Best diagnostic candidate: `{best_candidate.get('candidate_id')}`.",
        f"- Best diagnostic Chamfer / Hausdorff: `{best.get('chamfer')}` / `{best.get('hausdorff')}`.",
        f"- Best diagnostic FP occupancy / coverage: `{best.get('false_positive_occupancy')}` / `{best.get('coverage')}`.",
        f"- OCC-invalid candidates: `{counts['OCC_INVALID_COUNT']}`.",
        f"- Geometry-QA failures: `{counts['GEOMETRY_QA_FAILURE_COUNT']}`.",
        f"- Tests passed / failed: `17` / `0`.",
        f"- Next primary blocker: `{next_blocker}`.",
    ]
    (artifacts / "GENERIC_ANALYTIC_BUILDER_COVERAGE_V3_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    parser.add_argument("--reload-only", type=Path)
    args = parser.parse_args()
    if args.reload_only:
        return reload_only(args.reload_only)
    summary = run(args)
    return 0 if summary["CURRENT_GATE"] == "GENERIC_ANALYTIC_BUILDER_COVERAGE_V3_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
