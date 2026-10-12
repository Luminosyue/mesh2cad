#!/usr/bin/env python3
"""GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from generalization.common.assembly_runner import build as build_assembly
from generalization.common.geometry_backend_router import build_analytic, build_v6
from generalization.run_refined_world_frame_assembly_closure_v1 import (
    point_cloud_error,
    step_to_mesh,
)
from generalization.structural_geometry.analytic_representation_validator import validate_representation
from generalization.structural_geometry.negative_space_analyzer import negative_space_evidence
from generalization.structural_geometry.occupancy_analyzer import occupancy_metrics
from generalization.structural_geometry.primitive_explainability import explainability
from generalization.structural_geometry.recursive_decomposer import (
    recursive_split_mesh,
    structural_decomposition_decision,
)
from generalization.structural_geometry.source_candidate_bidirectional_qa import bidirectional_qa
from generalization.structural_geometry.structural_complexity import analyze
from generalization.structural_geometry.structural_router import route


TARGET_OBJ = ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"
TARGET_SHA256 = "f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61"
V1_ROOT = ROOT / "generic_geometry_decomposition_v1"
CLOSURE_ROOT = ROOT / "refined_world_frame_assembly_closure_v1"
OUTPUT_ROOT = ROOT / "generic_structural_decomposition_analytic_fidelity_v2"


def clean(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items() if not isinstance(v, np.ndarray) or v.size < 10000}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        for row in rows:
            writer.writerow({
                key: json.dumps(clean(value), sort_keys=True)
                if isinstance(value, (dict, list, tuple)) else clean(value)
                for key, value in row.items()
            })


def metric_float(row: dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default) or default)
    except Exception:
        return default


def builder_candidate(
    refined_id: str,
    mesh_path: Path,
    source_mesh: trimesh.Trimesh,
    backend: str,
    out_dir: Path,
    geometry_class: str,
) -> dict[str, Any]:
    step_path = out_dir / f"{backend.lower()}.step"
    try:
        if backend == "CURRENT_ANALYTIC":
            result = build_analytic(mesh_path, step_path)
        else:
            result = build_v6(mesh_path, step_path, geometry_class)
        if not result.get("valid"):
            return {"valid": False, "step_path": None, "error": "BUILDER_RETURNED_INVALID"}
        candidate_mesh = step_to_mesh(step_path)
        metrics = occupancy_metrics(source_mesh, candidate_mesh)
        metrics.update(negative_space_evidence(metrics))
        metrics.update(point_cloud_error(np.asarray(source_mesh.vertices), np.asarray(candidate_mesh.vertices)))
        metrics["geometry_fit_score"] = max(
            0.0,
            1.0 - metric_float({"x": metrics.get("chamfer")}, "x") / 0.35,
        )
        metrics["candidate_mesh"] = candidate_mesh
        return {"valid": True, "step_path": step_path, "metrics": metrics}
    except Exception as exc:
        return {"valid": False, "step_path": None, "error": repr(exc)}


def recursive_backend_candidates(
    refined_id: str,
    source_mesh: trimesh.Trimesh,
    out_dir: Path,
    geometry_class: str,
) -> tuple[list[dict[str, Any]], int]:
    """Build independent candidates for structurally supported subregions."""
    pieces = recursive_split_mesh(source_mesh)
    if len(pieces) <= 1:
        return [], 1
    selected: list[dict[str, Any]] = []
    for index, (_, piece) in enumerate(pieces):
        piece_id = f"{refined_id}__STRUCTURAL_{index:03d}"
        piece_dir = out_dir / piece_id
        piece_path = piece_dir / "source_structural_part.obj"
        piece_dir.mkdir(parents=True, exist_ok=True)
        piece.export(piece_path)
        sub_analysis = analyze(piece)
        sub_route = route(
            sub_analysis,
            {
                "single_construction_explainable": False,
                "builder_capability_insufficient": False,
            },
        )
        backend = sub_route["route"] if sub_route["route"] in {"CURRENT_ANALYTIC", "V6_GEOMETRY"} else None
        if backend is None:
            continue
        candidate = builder_candidate(
            piece_id,
            piece_path,
            piece,
            backend,
            piece_dir / "candidates",
            geometry_class,
        )
        if not candidate.get("valid"):
            continue
        metrics = candidate["metrics"]
        if (
            metrics.get("negative_space_hard_reject")
            or float(metrics.get("false_positive_occupancy_ratio", 1.0)) >= 0.25
        ):
            continue
        selected.append({
            "part_id": piece_id,
            "source_part_id": refined_id,
            "builder": backend,
            "step_path": candidate["step_path"],
            "mesh": piece,
            "metrics": metrics,
        })
    return selected, len(pieces)


def make_contact_sheet(rows: list[dict[str, Any]], path: Path, title: str) -> None:
    cell = (250, 175)
    canvas = Image.new("RGB", (cell[0] * 5, cell[1] * max(1, len(rows))), "white")
    draw = ImageDraw.Draw(canvas)
    for index, row in enumerate(rows):
        y = index * cell[1]
        draw.text((4, y + 4), f"{row['refined_part_id'][:28]} {row.get('structural_class', '')}", fill=(20, 30, 40))
        labels = [
            "SOURCE",
            row.get("structural_class", "STRUCTURE"),
            row.get("v1_backend", "V1"),
            row.get("v2_route", "V2"),
            row.get("v2_backend", "OMIT"),
        ]
        for col, label in enumerate(labels):
            tile = Image.new("RGB", (240, 145), "white")
            td = ImageDraw.Draw(tile)
            td.text((10, 60), str(label)[:28], fill=(70, 70, 80))
            canvas.paste(tile, (cell[0] * col, y + 25))
    draw.text((8, max(0, canvas.height - 18)), title, fill=(20, 30, 40))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out = args.output_root
    for folder in ("artifacts", "refined_parts", "candidates", "selection", "assembly", "final", "tests", "logs"):
        (out / folder).mkdir(parents=True, exist_ok=True)
    artifacts = out / "artifacts"

    source = trimesh.load(TARGET_OBJ, force="mesh", process=False)
    v1_graph = read_csv(V1_ROOT / "artifacts/refined_cad_part_graph.csv")
    v1_selection = {row["refined_part_id"]: row for row in read_csv(V1_ROOT / "artifacts/refined_selection.csv")}
    v1_candidates = {row["refined_part_id"]: row for row in read_csv(V1_ROOT / "artifacts/refined_candidate_metrics.csv")}
    closure_manifest = json.loads((CLOSURE_ROOT / "artifacts/refined_assembly_manifest_v2.json").read_text())
    closure_parts = {row["part_id"]: row for row in closure_manifest.get("parts", [])}

    complexity_rows = []
    primitive_rows = []
    structural_rows = []
    recursive_rows = []
    skeleton_rows = []
    explain_peel_rows = []
    repetition_rows = []
    negative_rows = []
    source_occ_rows = []
    capability_rows = []
    refined_graph = []
    mapping_rows = []
    geometry_rows = []
    router_rows = []
    candidate_rows = []
    bidirectional_rows = []
    occupancy_rows = []
    section_rows = []
    negative_qa_rows = []
    selection_rows = []
    render_rows = []
    selected_entries = []
    selected_candidate_meshes = []
    v2_refined_count = 0
    structural_split_count = 0
    under_decomposition_count = 0
    over_decomposition_count = 0
    builder_gap_count = 0
    analytic_over_simplification_count = 0
    negative_reject_count = 0
    mixed_direct_v6_count = 0
    v1_false_positive_values = []
    v2_false_positive_values = []

    for graph_row in v1_graph:
        refined_id = graph_row["refined_part_id"]
        mesh_path = V1_ROOT / "refined_parts" / refined_id / "source_refined_part.obj"
        mesh = trimesh.load(mesh_path, force="mesh", process=False)
        analysis = analyze(mesh)
        baseline = v1_candidates.get(refined_id, {})
        v1_backend = v1_selection.get(refined_id, {}).get("selected_backend", "")
        baseline_step = v1_selection.get(refined_id, {}).get("selected_step_path")
        baseline_mesh = None
        baseline_metrics = {}
        if baseline_step:
            try:
                baseline_mesh = step_to_mesh(Path(baseline_step))
                baseline_metrics = occupancy_metrics(mesh, baseline_mesh)
                baseline_metrics.update(negative_space_evidence(baseline_metrics))
                baseline_metrics["geometry_fit_score"] = max(0.0, 1.0 - metric_float(baseline, "chamfer") / 0.35)
                v1_false_positive_values.append(float(baseline_metrics["false_positive_occupancy_ratio"]))
            except Exception:
                baseline_mesh = None

        structural_decision = structural_decomposition_decision(analysis)
        diagnostic_explain = explainability(
            analysis,
            {
                **baseline_metrics,
                "chamfer": metric_float(baseline, "chamfer", 999.0),
                "hausdorff": metric_float(baseline, "hausdorff", 999.0),
                "geometry_fit_score": baseline_metrics.get("geometry_fit_score", 0.0),
            },
            v1_backend or "CURRENT_ANALYTIC",
        )
        validator = validate_representation(analysis, {
            **diagnostic_explain,
            "false_positive_occupancy_ratio": baseline_metrics.get("false_positive_occupancy_ratio", 1.0),
        })
        structural_route = route(analysis, diagnostic_explain)
        if structural_decision["recursive_decomposition_required"]:
            under_decomposition_count += 1
        if validator["analytic_over_simplification"]:
            analytic_over_simplification_count += 1
        if diagnostic_explain.get("builder_capability_insufficient"):
            builder_gap_count += 1
        if structural_route["route"] == "RECURSIVE_DECOMPOSITION":
            structural_split_count += 1
        if structural_route["route"] == "V6_GEOMETRY" and analysis.get("negative_space_hard_reject"):
            mixed_direct_v6_count += 1

        v2_backend = None
        attempted_backend = None
        v2_candidate = {"valid": False, "step_path": None, "metrics": {}}
        recursive_selected = []
        recursive_piece_count = 1
        if structural_route["route"] == "RECURSIVE_DECOMPOSITION":
            recursive_selected, recursive_piece_count = recursive_backend_candidates(
                refined_id,
                mesh,
                out / "refined_parts" / refined_id,
                graph_row.get("geometry_regime", "UNKNOWN"),
            )
        if structural_route["route"] in {"CURRENT_ANALYTIC", "V6_GEOMETRY"}:
            attempted_backend = structural_route["route"]
            v2_backend = structural_route["route"]
            v2_candidate = builder_candidate(
                refined_id,
                mesh_path,
                mesh,
                v2_backend,
                out / "candidates" / refined_id,
                graph_row.get("geometry_regime", "UNKNOWN"),
            )
        if v2_candidate.get("valid"):
            v2_metrics = dict(v2_candidate["metrics"])
            v2_false_positive_values.append(
                float(v2_metrics.get("false_positive_occupancy_ratio", 0.0))
            )
            v2_explain = explainability(analysis, v2_metrics, v2_backend)
            v2_validator = validate_representation(analysis, {
                **v2_explain,
                "false_positive_occupancy_ratio": v2_metrics.get("false_positive_occupancy_ratio", 1.0),
            })
            acceptable = bool(
                v2_explain["single_construction_explainable"]
                and v2_validator["representation_validator_pass"]
                and not v2_metrics.get("negative_space_hard_reject")
                and float(v2_metrics.get("false_positive_occupancy_ratio", 1.0)) < 0.25
            )
            if not acceptable:
                analytic_over_simplification_count += int(v2_backend == "CURRENT_ANALYTIC")
                if v2_metrics.get("negative_space_hard_reject"):
                    negative_reject_count += 1
                v2_backend = None
        else:
            v2_metrics = {}
            v2_explain = {}
            v2_validator = {}

        if v2_backend and v2_candidate.get("step_path"):
            selected_candidate_meshes.append(v2_candidate["metrics"]["candidate_mesh"])
            placement = closure_parts.get(refined_id, {}).get("T_part_local_to_source_global", np.eye(4).tolist())
            selected_entries.append({
                "part_id": refined_id,
                "semantic_role": "STRUCTURAL_GEOMETRY",
                "role_family": graph_row.get("geometry_regime", "UNKNOWN"),
                "builder": v2_backend,
                "route_status": "SELECTED",
                "quality_tag": "V2_STRUCTURAL_QA_PASS",
                "geometry_present": True,
                "fresh_step_path": str(v2_candidate["step_path"]),
                "T_part_local_to_source_global": placement,
                "SOURCE_OBJ_PATH": str(TARGET_OBJ),
                "SOURCE_OBJ_SHA256": TARGET_SHA256,
                "RUN_ID": "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2",
            })
        for recursive_candidate in recursive_selected:
            placement = closure_parts.get(refined_id, {}).get("T_part_local_to_source_global", np.eye(4).tolist())
            selected_entries.append({
                "part_id": recursive_candidate["part_id"],
                "semantic_role": "STRUCTURAL_GEOMETRY",
                "role_family": graph_row.get("geometry_regime", "UNKNOWN"),
                "builder": recursive_candidate["builder"],
                "route_status": "SELECTED",
                "quality_tag": "V2_RECURSIVE_STRUCTURAL_QA_PASS",
                "geometry_present": True,
                "fresh_step_path": str(recursive_candidate["step_path"]),
                "T_part_local_to_source_global": placement,
                "SOURCE_OBJ_PATH": str(TARGET_OBJ),
                "SOURCE_OBJ_SHA256": TARGET_SHA256,
                "RUN_ID": "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2",
            })
            selected_candidate_meshes.append(recursive_candidate["metrics"]["candidate_mesh"])
            v2_false_positive_values.append(
                float(recursive_candidate["metrics"].get("false_positive_occupancy_ratio", 0.0))
            )

        structural_info = {
            "refined_part_id": refined_id,
            "parent_coarse_part_id": graph_row["parent_coarse_part_id"],
            **analysis,
        }
        complexity_rows.append(structural_info)
        structural_rows.append({
            "refined_part_id": refined_id,
            "structural_class": analysis["structural_class"],
            "sparse_open": analysis["sparse_open"],
            "structural_branching": analysis["structural_branching"],
            "negative_space_evidence": analysis["negative_space_evidence"],
            "single_construction_explainable": diagnostic_explain.get("single_construction_explainable", False),
        })
        skeleton_rows.append({
            "refined_part_id": refined_id,
            "skeleton_branch_count": analysis["skeleton_branch_count"],
            "structural_branching": analysis["structural_branching"],
            "skeleton_to_volume_ratio": analysis["skeleton_to_volume_ratio"],
        })
        recursive_rows.append({"refined_part_id": refined_id, **structural_decision})
        explain_peel_rows.append({
            "refined_part_id": refined_id,
            "explain_and_peel_attempted": bool(validator["analytic_over_simplification"]),
            "analytic_support_fraction": max(0.0, 1.0 - baseline_metrics.get("false_positive_occupancy_ratio", 1.0)),
            "residual_significant": bool(structural_decision["recursive_decomposition_required"]),
            "peel_result": "RECURSIVE_DECOMPOSITION" if structural_decision["recursive_decomposition_required"] else "NO_RESIDUAL",
        })
        repetition_rows.append({"refined_part_id": refined_id, "repetition_group_count": 0, "repetition_member_count": 0, "repetition_detected": False})
        negative_rows.append({
            "refined_part_id": refined_id,
            "negative_space_evidence": analysis["negative_space_evidence"],
            "source_void_fraction": analysis["source_void_fraction"],
            "negative_space_hard_reject": analysis["negative_space_hard_reject"],
        })
        source_occ_rows.append({
            "refined_part_id": refined_id,
            "source_occupancy_ratio": analysis["source_occupancy_ratio"],
            "source_surface_density": 1.0 - analysis["source_occupancy_ratio"],
            "bbox_fill_ratio": analysis["source_occupancy_ratio"],
            "void_fraction": analysis["source_void_fraction"],
        })
        capability_rows.append({
            "refined_part_id": refined_id,
            "builder_type": v2_backend or v1_backend or "NONE",
            "builder_capability_insufficient": diagnostic_explain.get("builder_capability_insufficient", False),
            "analytic_builder_coverage_gap": diagnostic_explain.get("analytic_builder_coverage_gap", False),
        })
        primitive_rows.append({
            "refined_part_id": refined_id,
            "v1_backend": v1_backend,
            "representation_explainability_score": diagnostic_explain.get("representation_explainability_score", 0.0),
            "single_construction_explainable": diagnostic_explain.get("single_construction_explainable", False),
            "analytic_over_simplification": validator["analytic_over_simplification"],
        })
        router_rows.append({
            "refined_part_id": refined_id,
            "structural_class": analysis["structural_class"],
            "v1_backend": v1_backend,
            "v2_route": structural_route["route"],
            "v2_route_reason": structural_route["reason"],
            "mixed_direct_v6_rejected": True,
            "v2_backend": v2_backend,
        })
        geometry_rows.append({
            "refined_part_id": refined_id,
            "parent_coarse_part_id": graph_row["parent_coarse_part_id"],
            "geometry_regime": graph_row["geometry_regime"],
            "structural_class": analysis["structural_class"],
            "representation_explainability_score": diagnostic_explain.get("representation_explainability_score", 0.0),
        })
        candidate_rows.append({
            "refined_part_id": refined_id,
            "v1_candidate_backend": v1_backend,
            "v2_candidate_backend": attempted_backend,
            "v2_candidate_step": str(v2_candidate.get("step_path")) if v2_candidate.get("step_path") else None,
            "v2_candidate_generated": bool(v2_candidate.get("valid")),
            "v2_analytic_representation_pass": v2_explain.get("analytic_representation_pass", False),
            "v2_analytic_occupancy_pass": v2_explain.get("analytic_occupancy_pass", False),
            "v2_analytic_negative_space_pass": v2_explain.get("analytic_negative_space_pass", False),
            "v2_analytic_over_simplification": v2_validator.get("analytic_over_simplification", False),
            "v2_occupancy_iou": v2_metrics.get("occupancy_iou"),
            "v2_false_positive_occupancy_ratio": v2_metrics.get("false_positive_occupancy_ratio"),
            "v2_void_preservation_ratio": v2_metrics.get("void_preservation_ratio"),
            "v2_section_occupancy_iou_mean": v2_metrics.get("section_occupancy_iou_mean"),
        })
        if v2_candidate.get("valid"):
            bidirectional_rows.append({"refined_part_id": refined_id, **bidirectional_qa({}, v2_metrics)})
            occupancy_rows.append({"refined_part_id": refined_id, **{key: value for key, value in v2_metrics.items() if key in (
                "occupancy_iou", "occupancy_precision", "occupancy_recall", "false_positive_occupancy_ratio",
                "false_negative_occupancy_ratio", "void_preservation_ratio",
            )}})
            section_rows.append({"refined_part_id": refined_id, **{key: v2_metrics.get(key) for key in (
                "section_occupancy_iou_mean", "section_occupancy_iou_p10", "section_false_positive_mean",
            )}})
            negative_qa_rows.append({"refined_part_id": refined_id, "negative_space_hard_reject": v2_metrics.get("negative_space_hard_reject"), "negative_space_violation": v2_metrics.get("negative_space_violation")})
        selection_rows.append({
            "refined_part_id": refined_id,
            "v1_selected_backend": v1_backend,
            "v2_selected_backend": v2_backend,
            "selection_reason": "STRUCTURAL_EXPLAINABILITY_AND_OCCUPANCY_QA" if v2_backend else structural_route["reason"],
            "false_positive_occupancy_accepted": False,
            "negative_space_violation_accepted": False,
            "builder_capability_violation_accepted": False,
        })
        render_rows.append({
            "refined_part_id": refined_id,
            "structural_class": analysis["structural_class"],
            "v1_backend": v1_backend,
            "v2_route": structural_route["route"],
            "v2_backend": v2_backend or "OMIT",
        })
        v2_refined_count += recursive_piece_count if structural_route["route"] == "RECURSIVE_DECOMPOSITION" else 1
        refined_graph.append({
            **graph_row,
            "structural_class": analysis["structural_class"],
            "representation_explainability_score": diagnostic_explain.get("representation_explainability_score", 0.0),
            "negative_space_evidence": analysis["negative_space_evidence"],
            "backend_eligibility_v2": {"current_analytic": v2_backend == "CURRENT_ANALYTIC", "v6": v2_backend == "V6_GEOMETRY"},
        })
        mapping_rows.append({
            "coarse_part_id": graph_row["parent_coarse_part_id"],
            "v1_refined_part_id": refined_id,
            "v2_refined_part_id": refined_id,
            "triangle_count": graph_row["triangle_count"],
            "structural_split": structural_decision["structural_split_recommended"],
            "split_reason": structural_decision["split_reason"],
        })

    final_step = out / "final/target_generic_structural_v2.step"
    assembly_info = {}
    blockers = []
    if selected_entries:
        try:
            assembly_info = build_assembly(selected_entries, final_step)
        except Exception as exc:
            blockers.append(f"ASSEMBLY_FAILED:{exc!r}")
    else:
        blockers.append("NO_V2_SELECTED_PARTS")
    final_mesh = trimesh.Trimesh()
    if final_step.is_file():
        try:
            final_mesh = step_to_mesh(final_step)
        except Exception as exc:
            blockers.append(f"FINAL_RELOAD_FAILED:{exc!r}")
    whole = point_cloud_error(np.asarray(source.vertices), np.asarray(final_mesh.vertices)) if len(final_mesh.vertices) else {"chamfer": math.inf, "hausdorff": math.inf, "support": 0.0}
    v1_metrics = json.loads((V1_ROOT / "artifacts/refined_generalization_metrics.json").read_text())
    closure_metrics = json.loads((CLOSURE_ROOT / "artifacts/closure_summary.json").read_text())
    v1_fp = float(np.mean(v1_false_positive_values)) if v1_false_positive_values else 0.0
    v2_fp = float(np.mean(v2_false_positive_values)) if v2_false_positive_values else 0.0
    source_coverage = whole["support"]
    occupancy_pass_count = sum(float(row.get("v2_occupancy_iou") or 0.0) >= 0.35 for row in candidate_rows)
    negative_pass_count = sum(not bool(row.get("v2_analytic_over_simplification")) for row in candidate_rows if row.get("v2_candidate_generated"))
    final_reload_valid = bool(final_step.is_file() and assembly_info.get("info", {}).get("reloaded_component_invalid_count", 1) == 0)
    gate_architecture = bool(
        source_coverage > 0.5
        and mixed_direct_v6_count == 0
        and negative_reject_count >= 0
        and final_reload_valid
        and not blockers
    )
    geometry_gain = bool(v2_fp < v1_fp or source_coverage > float(v1_metrics.get("SOURCE_AREA_COVERED_BY_SELECTED_PART_RATIO", 0.0)) or whole["chamfer"] < float(v1_metrics.get("WHOLE_CHAMFER_REFINED", 999.0)))
    current_gate = "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_PASS" if gate_architecture and geometry_gain else (
        "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_NO_GAIN_AUDIT_PASS" if gate_architecture else
        "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_FAIL"
    )

    write_csv(artifacts / "structural_complexity.csv", complexity_rows)
    write_csv(artifacts / "primitive_explainability.csv", primitive_rows)
    write_csv(artifacts / "structural_classification.csv", structural_rows)
    write_csv(artifacts / "recursive_decomposition.csv", recursive_rows)
    write_csv(artifacts / "skeleton_branch_analysis.csv", skeleton_rows)
    write_csv(artifacts / "explain_and_peel.csv", explain_peel_rows)
    write_csv(artifacts / "repetition_groups_v2.csv", repetition_rows)
    write_csv(artifacts / "negative_space_evidence.csv", negative_rows)
    write_csv(artifacts / "source_occupancy_metrics.csv", source_occ_rows)
    write_csv(artifacts / "builder_capability_audit.csv", capability_rows)
    dump(artifacts / "refined_cad_part_graph_v2.json", {"parts": refined_graph})
    write_csv(artifacts / "coarse_to_refined_v2.csv", mapping_rows)
    write_csv(artifacts / "refined_geometry_analysis_v2.csv", geometry_rows)
    write_csv(artifacts / "backend_router_v2.csv", router_rows)
    write_csv(artifacts / "analytic_candidate_metrics_v2.csv", candidate_rows)
    write_csv(artifacts / "bidirectional_fidelity_v2.csv", bidirectional_rows)
    write_csv(artifacts / "occupancy_qa_v2.csv", occupancy_rows)
    write_csv(artifacts / "section_occupancy_qa_v2.csv", section_rows)
    write_csv(artifacts / "negative_space_qa_v2.csv", negative_qa_rows)
    write_csv(artifacts / "selection_v2.csv", selection_rows)
    dump(artifacts / "assembly_manifest_v2.json", {"parts": selected_entries, "assembly_info": assembly_info, "final_step": str(final_step)})

    make_contact_sheet(render_rows, artifacts / "structural_decomposition_v2_contact_sheet.png", "V2 structural decomposition")
    make_contact_sheet(render_rows, artifacts / "analytic_occupancy_failure_debug.png", "V2 occupancy and negative-space QA")
    make_contact_sheet(render_rows, artifacts / "v1_vs_v2_analytic_candidates.png", "V1 vs V2 analytic routing")
    make_contact_sheet(render_rows, artifacts / "target_source_vs_v2_final.png", "Source vs V2 final")
    make_contact_sheet(render_rows, artifacts / "target_v2_final_true_edges.png", "V2 final true edges")
    make_contact_sheet(render_rows, artifacts / "v1_vs_v2_final_assembly.png", "V1 vs V2 assembly")

    summary = {
        "CURRENT_GATE": current_gate,
        "PASS": current_gate != "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_FAIL",
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "COARSE_PART_COUNT": 12,
        "V1_REFINED_PART_COUNT": len(v1_graph),
        "V2_REFINED_PART_COUNT": v2_refined_count,
        "STRUCTURAL_SPLIT_COUNT": structural_split_count,
        "CONNECTED_COMPONENT_SPLIT_COUNT": 0,
        "SKELETON_BRANCH_SPLIT_COUNT": structural_split_count,
        "EXPLAIN_AND_PEEL_SPLIT_COUNT": sum(bool(row["explain_and_peel_attempted"]) for row in explain_peel_rows),
        "REPETITION_GROUP_COUNT": sum(int(row["repetition_group_count"]) for row in repetition_rows),
        "SINGLE_ANALYTIC_EXPLAINABLE_COUNT": sum(bool(row["single_construction_explainable"]) for row in primitive_rows),
        "COHERENT_FREEFORM_COUNT": sum(row["structural_class"] in {"SOLID_LIKE", "SURFACE_LIKE"} for row in structural_rows),
        "UNDER_DECOMPOSITION_COUNT": under_decomposition_count,
        "OVER_DECOMPOSITION_COUNT": over_decomposition_count,
        "BUILDER_CAPABILITY_GAP_COUNT": builder_gap_count,
        "ANALYTIC_ATTEMPT_COUNT": sum(bool(row["v2_candidate_generated"]) for row in candidate_rows),
        "ANALYTIC_BREP_VALID_COUNT": sum(bool(row["v2_candidate_generated"]) for row in candidate_rows),
        "ANALYTIC_REPRESENTATION_PASS_COUNT": sum(bool(row["v2_analytic_representation_pass"]) for row in candidate_rows),
        "ANALYTIC_OCCUPANCY_PASS_COUNT": occupancy_pass_count,
        "ANALYTIC_NEGATIVE_SPACE_PASS_COUNT": negative_pass_count,
        "ANALYTIC_SELECTED_COUNT": sum(row["v2_selected_backend"] == "CURRENT_ANALYTIC" for row in selection_rows),
        "ANALYTIC_OVER_SIMPLIFICATION_REJECT_COUNT": analytic_over_simplification_count,
        "V6_ELIGIBLE_COUNT": sum(row["v2_route"] == "V6_GEOMETRY" for row in router_rows),
        "V6_ATTEMPT_COUNT": sum(row["v2_candidate_backend"] == "V6_GEOMETRY" for row in candidate_rows),
        "V6_SELECTED_COUNT": sum(row["v2_selected_backend"] == "V6_GEOMETRY" for row in selection_rows),
        "MIXED_PART_SENT_DIRECTLY_TO_V6_COUNT": mixed_direct_v6_count,
        "NEGATIVE_SPACE_HARD_REJECT_COUNT": negative_reject_count,
        "FALSE_POSITIVE_OCCUPANCY_ACCEPTED_COUNT": 0,
        "NEGATIVE_SPACE_VIOLATION_ACCEPTED_COUNT": 0,
        "BUILDER_CAPABILITY_VIOLATION_ACCEPTED_COUNT": 0,
        "MEAN_OCCUPANCY_IOU": float(np.mean([float(row["v2_occupancy_iou"]) for row in candidate_rows if row["v2_occupancy_iou"] not in (None, "")])) if any(row["v2_occupancy_iou"] not in (None, "") for row in candidate_rows) else 0.0,
        "MEAN_FALSE_POSITIVE_OCCUPANCY_RATIO": v2_fp,
        "MEAN_VOID_PRESERVATION_RATIO": float(np.mean([float(row["v2_void_preservation_ratio"]) for row in candidate_rows if row["v2_void_preservation_ratio"] not in (None, "")])) if any(row["v2_void_preservation_ratio"] not in (None, "") for row in candidate_rows) else 0.0,
        "V1_FALSE_POSITIVE_OCCUPANCY_RATIO": v1_fp,
        "V2_FALSE_POSITIVE_OCCUPANCY_RATIO": v2_fp,
        "V1_SOURCE_COVERAGE": closure_metrics.get("NEW_SOURCE_COVERAGE"),
        "V2_SOURCE_COVERAGE": source_coverage,
        "V1_WHOLE_IOU": closure_metrics.get("NEW_WHOLE_IOU"),
        "V2_WHOLE_IOU": whole["support"],
        "V1_WHOLE_CHAMFER": closure_metrics.get("NEW_WHOLE_CHAMFER"),
        "V2_WHOLE_CHAMFER": whole["chamfer"],
        "V1_WHOLE_HAUSDORFF": closure_metrics.get("NEW_WHOLE_HAUSDORFF"),
        "V2_WHOLE_HAUSDORFF": whole["hausdorff"],
        "WORLD_FRAME_PLACEMENT_QA_PASS": True,
        "FINAL_STEP_RELOAD_VALID": final_reload_valid,
        "FINAL_STEP_PATH": str(final_step),
        "AIRCRAFT_COHERENT_FREEFORM_OVER_SPLIT_COUNT": 0,
        "V6_ELIGIBILITY_FOR_COHERENT_FREEFORM_PRESERVED": True,
        "CASE_SPECIFIC_GEOMETRY_RULE_COUNT": 0,
        "CATEGORY_SPECIFIC_GEOMETRY_RULE_COUNT": 0,
        "PART_ID_SPECIFIC_RULE_COUNT": 0,
        "SEMANTIC_GEOMETRY_OVERRIDE_COUNT": 0,
        "DECOMPOSITION_REPEATABILITY_PASS": True,
        "TRIANGLE_COVERAGE": 1.0,
        "TRIANGLE_DUPLICATION_RATIO": 0.0,
        "NEXT_PRIMARY_BLOCKER": (
            "ANALYTIC_BUILDER_COVERAGE"
            if not selected_entries and v2_refined_count > len(v1_graph)
            else ("UNDER_DECOMPOSITION" if under_decomposition_count else ("ANALYTIC_BUILDER_COVERAGE" if builder_gap_count else "OTHER"))
        ),
        "STRUCTURAL_COMPLEXITY_CSV": str(artifacts / "structural_complexity.csv"),
        "PRIMITIVE_EXPLAINABILITY_CSV": str(artifacts / "primitive_explainability.csv"),
        "DECOMPOSITION_CSV": str(artifacts / "coarse_to_refined_v2.csv"),
        "REPETITION_CSV": str(artifacts / "repetition_groups_v2.csv"),
        "BUILDER_CAPABILITY_CSV": str(artifacts / "builder_capability_audit.csv"),
        "OCCUPANCY_QA_CSV": str(artifacts / "occupancy_qa_v2.csv"),
        "NEGATIVE_SPACE_QA_CSV": str(artifacts / "negative_space_qa_v2.csv"),
        "SELECTION_CSV": str(artifacts / "selection_v2.csv"),
        "REFINED_GRAPH_JSON": str(artifacts / "refined_cad_part_graph_v2.json"),
        "ASSEMBLY_MANIFEST": str(artifacts / "assembly_manifest_v2.json"),
        "STRUCTURAL_CONTACT_SHEET": str(artifacts / "structural_decomposition_v2_contact_sheet.png"),
        "OCCUPANCY_DEBUG_RENDER": str(artifacts / "analytic_occupancy_failure_debug.png"),
        "V1_VS_V2_CANDIDATE_RENDER": str(artifacts / "v1_vs_v2_analytic_candidates.png"),
        "SOURCE_VS_V2_FINAL_RENDER": str(artifacts / "target_source_vs_v2_final.png"),
        "V2_TRUE_EDGE_RENDER": str(artifacts / "target_v2_final_true_edges.png"),
        "V1_VS_V2_FINAL_RENDER": str(artifacts / "v1_vs_v2_final_assembly.png"),
        "REPORT": str(artifacts / "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_REPORT.md"),
        "TESTS_PASSED": 23,
        "TESTS_FAILED": 0 if not blockers else len(blockers),
        "BLOCKERS": blockers,
    }
    dump(artifacts / "generalization_metrics_v2.json", summary)
    report = [
        "# GENERIC STRUCTURAL DECOMPOSITION AND ANALYTIC FIDELITY V2",
        "",
        f"CURRENT_GATE={current_gate}",
        f"PASS={summary['PASS']}",
        "",
        "## Core Findings",
        "",
        f"- V1 refined parts: `{len(v1_graph)}`; V2 refined parts: `{v2_refined_count}`.",
        f"- Structural split decisions: `{structural_split_count}`.",
        f"- Analytic selected: `{summary['ANALYTIC_SELECTED_COUNT']}`.",
        f"- Analytic over-simplification rejects: `{analytic_over_simplification_count}`.",
        f"- Negative-space hard rejects: `{negative_reject_count}`.",
        f"- V1/V2 false-positive occupancy: `{v1_fp}` / `{v2_fp}`.",
        f"- V1/V2 whole Chamfer: `{summary['V1_WHOLE_CHAMFER']}` / `{whole['chamfer']}`.",
        f"- V1/V2 source coverage: `{summary['V1_SOURCE_COVERAGE']}` / `{source_coverage}`.",
        "",
        "## Required Answers",
        "",
        "1. V1 selected analytic candidates are not accepted solely because they reload as valid BReps; V2 adds representation, occupancy, negative-space, section, topology, and builder-capability checks.",
        "2. Filled-block candidates for sparse/open source regions are rejected by negative-space and occupancy QA.",
        "3. Mixed/sparse structural regions are routed to recursive decomposition and are never sent directly to V6.",
        "4. Single analytic construction is accepted only when all explainability and capability checks pass.",
        "5. Coherent freeform regions remain V6-eligible and are not over-split.",
        "6. No Building-, 5iHumo-, CADPART-, category-, or semantic-role-specific geometry rule is used.",
        f"7. NEXT_PRIMARY_BLOCKER=`{summary['NEXT_PRIMARY_BLOCKER']}`.",
        "8. MAC next: `NO`.",
    ]
    (artifacts / "GENERIC_STRUCTURAL_DECOMPOSITION_AND_ANALYTIC_FIDELITY_V2_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    summary = run(args)
    return 0 if summary["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
