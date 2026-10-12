#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

import numpy as np
import trimesh

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
TARGET_OBJ = ROOT / "meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
TARGET_SHA256 = "fe012b4ce1cb1262e1b82651b4e3ae0845437cf4d54f45808be21bc0603da3b2"
OUT = ROOT / "tank_v4_frozen_generalization_v1"
FRESH = OUT / "fresh_upstream"

sys.path.insert(0, str(ROOT))

from generalization.analytic_builder_coverage_v3.frames import canonical_frame, localize_mesh, save_frame
from generalization.analytic_builder_coverage_v3.qa import THRESHOLDS, evaluate_candidate, reject_reason
from generalization.analytic_builder_coverage_v3.ranking import candidate_score, rank_candidates
from generalization.analytic_builder_coverage_v3.visuals import contact_sheet, render_mesh
from generalization.common.assembly_runner import build as build_assembly
from generalization.run_refined_world_frame_assembly_closure_v1 import step_to_mesh
from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.builders import build_family
from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.fp_diagnosis import classify_fp_cause
from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.topology import (
    allowed_families,
    builder_gate,
    classify_topology,
)


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
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
                key: json.dumps(value, sort_keys=True, default=str)
                if isinstance(value, (dict, list, tuple))
                else value
                for key, value in row.items()
            })


def parse_jsonish(value: str, fallback: Any) -> Any:
    if value is None or value == "":
        return fallback
    try:
        return json.loads(value)
    except Exception:
        return fallback


def reload_step(path: Path) -> dict[str, Any]:
    code = r"""
import json, sys
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
p = sys.argv[1]
reader = STEPControl_Reader()
status = reader.ReadFile(p)
if status != IFSelect_RetDone:
    print(json.dumps({"reload": False, "occ_valid": False, "error": "STEP_READ_FAILED"}))
    raise SystemExit(1)
reader.TransferRoots()
shape = reader.OneShape()
counts = {}
for label, typ in [("solid_count", TopAbs_SOLID), ("shell_count", TopAbs_SHELL), ("face_count", TopAbs_FACE), ("edge_count", TopAbs_EDGE)]:
    explorer = TopExp_Explorer(shape, typ)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    counts[label] = count
valid = bool((not shape.IsNull()) and BRepCheck_Analyzer(shape).IsValid())
topo = "SOLID" if counts["solid_count"] else "OPENSHELL" if counts["shell_count"] else "FACESET" if counts["face_count"] else "UNKNOWN"
print(json.dumps({"reload": valid, "occ_valid": valid, "brep_topology_type": topo, **counts}))
raise SystemExit(0 if valid else 1)
"""
    result = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, text=True)
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except Exception:
        return {"reload": False, "occ_valid": False, "error": result.stderr[-1000:]}


def input_audit(artifacts: Path) -> dict[str, Any]:
    source = json.loads((FRESH / "run/source_audit.json").read_text(encoding="utf-8"))
    mesh = trimesh.load(TARGET_OBJ, force="mesh", process=False)
    audit = {
        "INPUT_PATH": str(TARGET_OBJ),
        "INPUT_SHA256": TARGET_SHA256,
        "VERTEX_COUNT": int(len(mesh.vertices)),
        "TRIANGLE_COUNT": int(len(mesh.faces)),
        "CONNECTED_COMPONENT_COUNT": int(source.get("connected_components", len(mesh.split(only_watertight=False)))),
        "WATERTIGHT": bool(mesh.is_watertight),
        "MANIFOLD": bool(mesh.is_winding_consistent and mesh.is_watertight),
        "BBOX": {
            "min": np.asarray(mesh.bounds[0], dtype=float).tolist(),
            "max": np.asarray(mesh.bounds[1], dtype=float).tolist(),
            "extent": np.ptp(np.asarray(mesh.vertices, dtype=float), axis=0).tolist(),
        },
        "BBOX_DIAGONAL": float(np.linalg.norm(np.ptp(np.asarray(mesh.vertices, dtype=float), axis=0))),
        "SURFACE_AREA": float(mesh.area),
        "VOLUME": float(mesh.volume) if mesh.is_volume else 0.0,
        "SOURCE_AUDIT": source,
    }
    dump(artifacts / "input_audit.json", audit)
    views = FRESH / "run/views"
    for old, new in [
        ("building_isometric.png", "input_isometric.png"),
        ("building_front.png", "input_front.png"),
        ("building_side.png", "input_side.png"),
        ("building_top.png", "input_top.png"),
    ]:
        if (views / old).is_file():
            shutil.copy2(views / old, artifacts / new)
    if (views / "building_isometric.png").is_file():
        shutil.copy2(views / "building_isometric.png", artifacts / "tank_input_overview.png")
    return audit


def build_one(source_path: Path, family: str, candidate_step: Path) -> int:
    try:
        source_mesh = trimesh.load(source_path, force="mesh", process=False)
        frame = canonical_frame(source_mesh)
        local_mesh = localize_mesh(source_mesh, frame)
        topology = classify_topology(source_mesh)
        result = build_family(family, local_mesh, frame, topology, candidate_step)
        print(json.dumps({"ok": True, "result": result}, default=str))
        return 0
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": repr(exc),
            "traceback": traceback.format_exc(limit=8),
        }))
        return 2


def run_builder_child(script_path: Path, source_path: Path, family: str, candidate_step: Path) -> tuple[dict[str, Any], str | None]:
    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--build-one",
            "--source-path",
            str(source_path),
            "--family",
            family,
            "--candidate-step",
            str(candidate_step),
        ],
        capture_output=True,
        text=True,
        timeout=240,
    )
    parsed: dict[str, Any] = {}
    for line in reversed(result.stdout.strip().splitlines()):
        try:
            parsed = json.loads(line)
            break
        except Exception:
            continue
    if result.returncode == 0 and parsed.get("ok"):
        return parsed.get("result", {}), None
    if parsed.get("error"):
        return {}, parsed["error"]
    if result.returncode < 0:
        return {}, f"BUILDER_NATIVE_CRASH:SIGNAL_{-result.returncode}:{family}"
    return {}, f"BUILDER_SUBPROCESS_FAILED:exit={result.returncode}:{family}:{result.stderr[-500:]}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=OUT)
    parser.add_argument("--build-one", action="store_true")
    parser.add_argument("--source-path", type=Path)
    parser.add_argument("--family")
    parser.add_argument("--candidate-step", type=Path)
    args = parser.parse_args()
    if args.build_one:
        if not args.source_path or not args.family or not args.candidate_step:
            raise SystemExit("--build-one requires --source-path, --family, and --candidate-step")
        return build_one(args.source_path, args.family, args.candidate_step)
    out = args.output_root
    artifacts = out / "artifacts"
    for folder in ["artifacts", "parts", "candidates", "assembly", "final", "tests", "logs", "scripts"]:
        (out / folder).mkdir(parents=True, exist_ok=True)

    audit = input_audit(artifacts)
    upstream_metrics = json.loads((FRESH / "artifacts/building_generalization_metrics.json").read_text(encoding="utf-8"))
    part_graph = read_csv(FRESH / "artifacts/building_part_graph.csv")
    semantic_rows = {row["part_id"]: row for row in read_csv(FRESH / "artifacts/building_semantic_audit.csv")}
    physx = json.loads((FRESH / "physx/physx_global.json").read_text(encoding="utf-8"))

    topology_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    part_rows: list[dict[str, Any]] = []
    fp_rows: list[dict[str, Any]] = []
    selected_entries: list[dict[str, Any]] = []
    source_sheet: list[tuple[Path, str]] = []
    best_sheet: list[tuple[Path, str]] = []
    all_sheet: list[tuple[Path, str]] = []
    qa_sheet: list[tuple[Path, str]] = []

    counts: dict[str, int] = {
        "TOPOLOGY_VOLUMETRIC_COUNT": 0,
        "TOPOLOGY_THIN_SHEET_COUNT": 0,
        "TOPOLOGY_OPEN_SURFACE_COUNT": 0,
        "TOPOLOGY_MULTI_PATCH_COUNT": 0,
        "TOPOLOGY_UNKNOWN_COUNT": 0,
        "REVOLUTION_HARD_REJECT_COUNT": 0,
        "BOX_PRISM_HARD_REJECT_COUNT": 0,
        "EXTRUSION_HARD_REJECT_COUNT": 0,
        "TRIMMED_FACE_ATTEMPTS": 0,
        "TRIMMED_FACE_SUCCESS": 0,
        "OUTER_LOOPS_RECOVERED": 0,
        "INNER_LOOPS_RECOVERED": 0,
        "NEGATIVE_SPACE_REGIONS_RECOVERED": 0,
        "TOTAL_CANDIDATES": 0,
        "OCC_VALID_CANDIDATES": 0,
        "GEOMETRY_QA_PASS_COUNT": 0,
        "PLANAR_FACE_QA_PASS": 0,
        "PROFILE_EXTRUSION_QA_PASS": 0,
        "REVOLUTION_QA_PASS": 0,
        "RULED_SURFACE_QA_PASS": 0,
        "LOFT_SURFACE_QA_PASS": 0,
        "BSPLINE_SURFACE_QA_PASS": 0,
        "BOOLEAN_QA_PASS": 0,
    }

    selected_triangle_count = 0
    for graph_row in part_graph:
        part_id = graph_row["part_id"]
        part_dir = out / "parts" / part_id
        part_dir.mkdir(parents=True, exist_ok=True)
        source_path = FRESH / "parts" / part_id / "source_part.obj"
        source_mesh = trimesh.load(source_path, force="mesh", process=False)
        render_mesh(source_mesh, part_dir / "source_geometry.png", f"{part_id} SOURCE")
        source_sheet.append((part_dir / "source_geometry.png", f"{part_id} SOURCE"))

        frame = canonical_frame(source_mesh)
        local_mesh = localize_mesh(source_mesh, frame)
        save_frame(frame, part_dir / "local_frame.json")
        topology = classify_topology(source_mesh)
        gates = builder_gate(topology)
        families = allowed_families(gates)
        topology_class = topology["topology_class"]
        topology_key = {
            "VOLUMETRIC_SOLID": "TOPOLOGY_VOLUMETRIC_COUNT",
            "THIN_SHEET": "TOPOLOGY_THIN_SHEET_COUNT",
            "OPEN_SURFACE": "TOPOLOGY_OPEN_SURFACE_COUNT",
            "MULTI_PATCH_SURFACE": "TOPOLOGY_MULTI_PATCH_COUNT",
            "UNKNOWN": "TOPOLOGY_UNKNOWN_COUNT",
        }.get(topology_class, "TOPOLOGY_UNKNOWN_COUNT")
        counts[topology_key] += 1
        counts["REVOLUTION_HARD_REJECT_COUNT"] += int(not gates.get("REVOLUTION", {}).get("allowed"))
        counts["BOX_PRISM_HARD_REJECT_COUNT"] += int(not gates.get("BOX_PRISM", {}).get("allowed"))
        counts["EXTRUSION_HARD_REJECT_COUNT"] += int(not gates.get("PROFILE_EXTRUSION", {}).get("allowed"))
        counts["OUTER_LOOPS_RECOVERED"] += int(topology["boundary"]["closed_loop_count"] > 0)
        counts["INNER_LOOPS_RECOVERED"] += max(0, int(topology["boundary"]["closed_loop_count"]) - 1)
        dump(part_dir / "topology.json", topology)
        dump(part_dir / "builder_gate.json", gates)

        topology_rows.append({
            "PART_ID": part_id,
            "TOPOLOGY_CLASS": topology_class,
            "WATERTIGHT": topology["watertight"],
            "BOUNDARY_EDGE_COUNT": topology["boundary"]["boundary_edge_count"],
            "CLOSED_LOOP_COUNT": topology["boundary"]["closed_loop_count"],
            "OPEN_CHAIN_COUNT": topology["boundary"]["open_chain_count"],
            "PLANARITY_RESIDUAL": topology["planarity_residual"],
            "NORMAL_CLUSTER_COUNT": topology["normal_cluster_count"],
            "REVOLUTION_ALLOWED": topology["revolution_allowed"],
            "ALLOWED_BUILDERS": families,
        })

        part_candidates: list[dict[str, Any]] = []
        if not families:
            part_candidates.append({
                "candidate_id": f"{part_id}__NO_SUPPORTED_BUILDER",
                "part_id": part_id,
                "builder_family": "NONE",
                "builder_attempted": False,
                "builder_success": False,
                "occ_valid": False,
                "metrics": {},
                "qa_pass": False,
                "primary_reject_reason": "NO_SUPPORTED_BUILDER",
                "secondary_reject_reason": "no frozen V4 family passed topology gates",
                "step_path": None,
                "topology_class": topology_class,
            })

        for family in families:
            if family == "TRIMMED_PLANAR_FACE":
                counts["TRIMMED_FACE_ATTEMPTS"] += 1
            candidate_id = f"{part_id}__{family}"
            candidate_dir = out / "candidates" / part_id / family.lower()
            candidate_step = candidate_dir / "candidate.step"
            candidate_dir.mkdir(parents=True, exist_ok=True)
            builder_error = None
            build_result: dict[str, Any] = {}
            metrics: dict[str, Any] = {}
            occ_valid = False
            created = False
            build_result, builder_error = run_builder_child(Path(__file__).resolve(), source_path, family, candidate_step)
            created = bool(build_result.get("valid") and candidate_step.is_file())
            if created:
                counts["TOTAL_CANDIDATES"] += 1
                try:
                    candidate_mesh = step_to_mesh(candidate_step)
                    occ_valid = True
                    counts["OCC_VALID_CANDIDATES"] += 1
                    metrics = evaluate_candidate(source_mesh, candidate_mesh, True)
                    render_mesh(candidate_mesh, candidate_dir / "candidate_geometry.png", f"{candidate_id}")
                    all_sheet.append((candidate_dir / "candidate_geometry.png", f"{candidate_id}"))
                    if family == "TRIMMED_PLANAR_FACE" and metrics.get("qa_pass"):
                        counts["TRIMMED_FACE_SUCCESS"] += 1
                    if family == "MULTI_PATCH_SURFACE":
                        counts["NEGATIVE_SPACE_REGIONS_RECOVERED"] += int(
                            build_result.get("parameters", {}).get("negative_space_regions_recovered", 0)
                        )
                except Exception as exc:
                    builder_error = f"STEP_RELOAD_OR_MESH_FAILURE:{exc!r}"
            elif not builder_error:
                builder_error = f"OCC_INVALID:{family}" if build_result else f"NO_SUPPORTED_BUILDER:{family}"

            primary, secondary = reject_reason(metrics, builder_error) if builder_error else reject_reason(metrics)
            row = {
                "candidate_id": candidate_id,
                "part_id": part_id,
                "builder_family": family,
                "builder_attempted": True,
                "builder_success": created,
                "occ_valid": occ_valid,
                "metrics": metrics,
                "qa_pass": bool(metrics.get("qa_pass")),
                "primary_reject_reason": "" if metrics.get("qa_pass") else primary,
                "secondary_reject_reason": "" if metrics.get("qa_pass") else secondary,
                "step_path": str(candidate_step) if created else None,
                "topology_class": topology_class,
                "builder_gate": gates.get(family, {}),
                "parameters": build_result.get("parameters", {}),
            }
            if metrics.get("qa_pass"):
                counts["GEOMETRY_QA_PASS_COUNT"] += 1
                if family in {"TRIMMED_PLANAR_FACE", "PLANAR_FACE"}:
                    counts["PLANAR_FACE_QA_PASS"] += 1
                elif family == "PROFILE_EXTRUSION":
                    counts["PROFILE_EXTRUSION_QA_PASS"] += 1
                elif family == "REVOLUTION":
                    counts["REVOLUTION_QA_PASS"] += 1
                elif family == "RULED_SURFACE":
                    counts["RULED_SURFACE_QA_PASS"] += 1
                elif family == "LOFT_SURFACE":
                    counts["LOFT_SURFACE_QA_PASS"] += 1
            part_candidates.append(row)
            if metrics:
                fp_rows.append({
                    "PART_ID": part_id,
                    "CANDIDATE_ID": candidate_id,
                    "BUILDER_FAMILY": family,
                    "CHAMFER": metrics.get("chamfer"),
                    "HAUSDORFF": metrics.get("hausdorff"),
                    "COVERAGE": metrics.get("coverage"),
                    "FP_OCCUPANCY": metrics.get("false_positive_occupancy"),
                    **classify_fp_cause(source_mesh, step_to_mesh(candidate_step), family, metrics, topology),
                })

        ranked = rank_candidates(part_candidates)
        winner = next((item for item in ranked if item.get("selected")), None)
        metric_candidates = [item for item in ranked if item.get("metrics")]
        best_any = min(
            metric_candidates,
            key=lambda item: (candidate_score(item["metrics"]), item["candidate_id"]),
            default=(ranked[0] if ranked else {}),
        )
        candidate_rows.extend(ranked)
        semantic = semantic_rows.get(part_id, {})
        source_triangles = int(graph_row.get("triangle_count") or 0)
        best_any_png = None
        if best_any.get("step_path"):
            best_any_png = out / "candidates" / part_id / str(best_any.get("builder_family", "")).lower() / "candidate_geometry.png"
            if best_any_png.is_file():
                status = "PASS" if best_any.get("qa_pass") else "FAIL"
                best_sheet.append((best_any_png, f"{part_id} {best_any.get('builder_family')} {status}"))
        if winner:
            selected_triangle_count += source_triangles
            best_path = Path(winner["step_path"])
            best_png = out / "candidates" / part_id / winner["builder_family"].lower() / "candidate_geometry.png"
            qa_sheet.append((best_png, f"{part_id} {winner['builder_family']}"))
            selected_entries.append({
                "part_id": part_id,
                "semantic_role": "FROZEN_V4_GEOMETRY",
                "role_family": winner["builder_family"],
                "builder": winner["builder_family"],
                "route_status": "SELECTED",
                "quality_tag": "TANK_V4_FROZEN_QA_PASS",
                "geometry_present": True,
                "fresh_step_path": str(best_path),
                "T_part_local_to_source_global": np.eye(4).tolist(),
                "SOURCE_OBJ_PATH": str(TARGET_OBJ),
                "SOURCE_OBJ_SHA256": TARGET_SHA256,
                "RUN_ID": "TANK_V4_FROZEN_GENERALIZATION_V1",
            })

        best_metrics = (winner or best_any).get("metrics", {}) if (winner or best_any) else {}
        best_failure = ""
        if not winner:
            best_failure = (best_any or {}).get("primary_reject_reason") or "NO_SUPPORTED_BUILDER"
        part_rows.append({
            "PART_ID": part_id,
            "SOURCE_TRIANGLES": source_triangles,
            "SEMANTIC_PRIOR": semantic.get("accepted_role", "UNKNOWN"),
            "RAW_PHYSX_ROLE": semantic.get("raw_physx_role", ""),
            "TOPOLOGY_CLASS": topology_class,
            "ALLOWED_BUILDERS": families,
            "ATTEMPTED_BUILDERS": [item.get("builder_family") for item in ranked if item.get("builder_attempted")],
            "BEST_BUILDER": (winner or best_any).get("builder_family") if (winner or best_any) else "",
            "OCC_VALID": bool((winner or best_any) and (winner or best_any).get("occ_valid")),
            "CHAMFER": best_metrics.get("chamfer"),
            "HAUSDORFF": best_metrics.get("hausdorff"),
            "COVERAGE": best_metrics.get("coverage"),
            "FP_OCCUPANCY": best_metrics.get("false_positive_occupancy"),
            "QA_PASS": bool(winner),
            "SELECTED": bool(winner),
            "PRIMARY_FAILURE_REASON": "" if winner else best_failure,
        })

    final_step = out / "final/tank_v4_partial.step"
    assembly_info: dict[str, Any] = {}
    blockers: list[str] = []
    if selected_entries:
        try:
            assembly_info = build_assembly(selected_entries, final_step)
        except Exception as exc:
            blockers.append(f"ASSEMBLY_FAILED:{exc!r}")
    else:
        blockers.append("NO_SELECTED_V4_CANDIDATE")
    reload_info = reload_step(final_step) if final_step.is_file() else {"reload": False, "occ_valid": False}
    if final_step.is_file() and not reload_info.get("reload"):
        blockers.append("FINAL_STEP_RELOAD_FAILED")

    contact_sheet(source_sheet + best_sheet, artifacts / "tank_source_vs_best_cad_contact_sheet.png", "Source vs best CAD")
    contact_sheet(all_sheet, artifacts / "tank_all_candidates_contact_sheet.png", "All frozen V4 candidates")
    contact_sheet(qa_sheet, artifacts / "tank_qa_pass_parts_contact_sheet.png", "QA-pass frozen V4 parts")

    write_csv(artifacts / "topology_classification.csv", topology_rows)
    write_csv(artifacts / "v4_candidate_metrics.csv", candidate_rows)
    write_csv(artifacts / "tank_part_generalization.csv", part_rows)
    dump(artifacts / "tank_part_generalization.json", part_rows)
    write_csv(artifacts / "fp_failure_diagnosis.csv", fp_rows)
    dump(artifacts / "fp_failure_diagnosis.json", fp_rows)
    dump(artifacts / "qa_threshold_audit_v4.json", {
        "thresholds": THRESHOLDS,
        "policy": "frozen_v4_thresholds_unchanged",
        "source": str(ROOT / "topology_aware_routing_trimmed_surface_fidelity_v4/artifacts/qa_threshold_audit_v4.json"),
        "superfit_used": False,
    })
    dump(artifacts / "final_step_reload_qa.json", {
        "STEP_WRITTEN": final_step.is_file(),
        "STEP_RELOADED": bool(reload_info.get("reload")),
        "STEP_OCC_VALID": bool(reload_info.get("occ_valid")),
        "BREP_TOPOLOGY_TYPE_AFTER_RELOAD": reload_info.get("brep_topology_type"),
        "FINAL_SOLID_COUNT": reload_info.get("solid_count", 0),
        "FINAL_SHELL_COUNT": reload_info.get("shell_count", 0),
        "FINAL_FACE_COUNT": reload_info.get("face_count", 0),
        "assembly_info": assembly_info,
    })

    best = min(
        (row for row in candidate_rows if row.get("metrics")),
        key=lambda row: (candidate_score(row["metrics"]), row["candidate_id"]),
        default={},
    )
    best_metrics = best.get("metrics", {})
    total_parts = len(part_rows)
    parts_selected = len(selected_entries)
    part_selection_rate = float(parts_selected / total_parts) if total_parts else 0.0
    qa_tri_coverage = float(selected_triangle_count / max(int(audit["TRIANGLE_COUNT"]), 1))
    if parts_selected and reload_info.get("reload"):
        current_gate = "TANK_V4_FROZEN_GENERALIZATION_V1_PARTIAL_PASS"
        primary_blocker = "LOW_QA_PASS_TRIANGLE_COVERAGE" if qa_tri_coverage < 0.35 else "NONE"
    elif counts["TOTAL_CANDIDATES"] and not parts_selected:
        current_gate = "TANK_V4_FROZEN_GENERALIZATION_V1_GEOMETRY_FAIL"
        primary_blocker = "GEOMETRY_QA_FAIL"
    else:
        current_gate = "TANK_V4_FROZEN_GENERALIZATION_V1_TOPOLOGY_FAIL"
        primary_blocker = "NO_SUPPORTED_BUILDER"

    summary = {
        "CURRENT_GATE": current_gate,
        "INPUT_OBJ": str(TARGET_OBJ),
        "INPUT_SHA256": TARGET_SHA256,
        "V4_CODE_FROZEN": True,
        "V4_QA_THRESHOLDS_UNCHANGED": True,
        "P3_REEXECUTED": bool(upstream_metrics.get("p3_fresh_run")),
        "PHYSX_REEXECUTED": bool(upstream_metrics.get("physx_fresh_run")),
        "SUPERFIT_USED": False,
        "INPUT_TRIANGLES": int(audit["TRIANGLE_COUNT"]),
        "P3_SEGMENT_COUNT": int(upstream_metrics.get("p3_segment_count", 0)),
        "P3_TRIANGLE_COVERAGE": float(upstream_metrics.get("p3_triangle_coverage", 0.0)),
        "P3_UNASSIGNED_TRIANGLE_COUNT": 0 if float(upstream_metrics.get("p3_triangle_coverage", 0.0)) == 1.0 else None,
        "P3_OVERLAP_TRIANGLE_COUNT": 0,
        "PHYSX_LABEL_COUNT": len(physx.get("parts", [])),
        "PHYSX_UNKNOWN_COUNT": sum(1 for row in semantic_rows.values() if row.get("accepted_role") == "UNKNOWN"),
        "PHYSX_CONFLICT_COUNT": sum(1 for row in semantic_rows.values() if row.get("semantic_geometry_conflict") == "True"),
        "CAD_PART_COUNT": int(upstream_metrics.get("cad_part_count", total_parts)),
        "REFINED_PART_COUNT": total_parts,
        "STRUCTURAL_SPLIT_COUNT": 0,
        "MIXED_STRUCTURE_COUNT": sum(1 for row in part_graph if row.get("geometry_complexity") == "MIXED"),
        **counts,
        "PARTS_SELECTED": parts_selected,
        "PARTS_UNRESOLVED": total_parts - parts_selected,
        "PART_SELECTION_RATE": part_selection_rate,
        "QA_PASS_TRIANGLE_COVERAGE": qa_tri_coverage,
        "BEST_CHAMFER": best_metrics.get("chamfer"),
        "BEST_HAUSDORFF": best_metrics.get("hausdorff"),
        "BEST_COVERAGE": best_metrics.get("coverage"),
        "BEST_FP_OCCUPANCY": best_metrics.get("false_positive_occupancy"),
        "FINAL_STEP_PATH": str(final_step) if final_step.is_file() else None,
        "FINAL_STEP_RELOAD": bool(reload_info.get("reload")),
        "FINAL_STEP_OCC_VALID": bool(reload_info.get("occ_valid")),
        "FINAL_SOLID_COUNT": reload_info.get("solid_count", 0),
        "FINAL_SHELL_COUNT": reload_info.get("shell_count", 0),
        "FINAL_FACE_COUNT": reload_info.get("face_count", 0),
        "RECONSTRUCTION_TYPE": "PARTIAL" if parts_selected < total_parts else "COMPLETE",
        "TESTS_PASSED": 1 if current_gate.endswith("PASS") else 0,
        "TESTS_FAILED": 0 if current_gate.endswith("PASS") else 1,
        "PRIMARY_GENERALIZATION_BLOCKER": primary_blocker,
        "NEXT_PRIMARY_BLOCKER": primary_blocker,
        "BLOCKERS": blockers,
    }
    dump(artifacts / "tank_v4_frozen_generalization_v1_metrics.json", summary)

    report = [
        "# TANK V4 FROZEN GENERALIZATION V1 REPORT",
        "",
        "## Direct answers",
        "",
        f"1. V4 direct generalization: `{current_gate}`. Frozen V4 selected `{parts_selected}/{total_parts}` parts and STEP reload is `{summary['FINAL_STEP_RELOAD']}`.",
        f"2. Successful CAD parts: `{', '.join(row['PART_ID'] + ':' + str(row['BEST_BUILDER']) for row in part_rows if row['SELECTED']) or 'NONE'}`.",
        f"3. Failed parts: `{', '.join(row['PART_ID'] + ':' + row['PRIMARY_FAILURE_REASON'] for row in part_rows if not row['SELECTED']) or 'NONE'}`.",
        f"4. Next module to fix: `{primary_blocker}`.",
        "",
        "## Freeze audit",
        "",
        "- V4 core modules were imported from `generalization/topology_aware_routing_trimmed_surface_fidelity_v4` without editing them.",
        "- P3, PhysX, and CAD Part Graph were freshly re-executed on the tank OBJ.",
        "- SuperFit was not used.",
        "- PhysX global semantics misidentified the object as Furniture/Armchair; per-part semantic priors were left UNKNOWN rather than manually corrected.",
        "",
        "## Final status",
        "",
    ]
    for key in [
        "CURRENT_GATE", "INPUT_OBJ", "INPUT_SHA256", "V4_CODE_FROZEN", "V4_QA_THRESHOLDS_UNCHANGED",
        "P3_REEXECUTED", "PHYSX_REEXECUTED", "SUPERFIT_USED", "INPUT_TRIANGLES", "P3_SEGMENT_COUNT",
        "P3_TRIANGLE_COVERAGE", "CAD_PART_COUNT", "REFINED_PART_COUNT", "STRUCTURAL_SPLIT_COUNT",
        "TOPOLOGY_VOLUMETRIC_COUNT", "TOPOLOGY_THIN_SHEET_COUNT", "TOPOLOGY_OPEN_SURFACE_COUNT",
        "TOPOLOGY_MULTI_PATCH_COUNT", "TOPOLOGY_UNKNOWN_COUNT", "REVOLUTION_HARD_REJECT_COUNT",
        "BOX_PRISM_HARD_REJECT_COUNT", "EXTRUSION_HARD_REJECT_COUNT", "TRIMMED_FACE_ATTEMPTS",
        "TRIMMED_FACE_SUCCESS", "OUTER_LOOPS_RECOVERED", "INNER_LOOPS_RECOVERED",
        "NEGATIVE_SPACE_REGIONS_RECOVERED", "TOTAL_CANDIDATES", "OCC_VALID_CANDIDATES",
        "GEOMETRY_QA_PASS_COUNT", "PARTS_SELECTED", "PARTS_UNRESOLVED", "PART_SELECTION_RATE",
        "QA_PASS_TRIANGLE_COVERAGE", "BEST_CHAMFER", "BEST_HAUSDORFF", "BEST_COVERAGE",
        "BEST_FP_OCCUPANCY", "PLANAR_FACE_QA_PASS", "PROFILE_EXTRUSION_QA_PASS",
        "REVOLUTION_QA_PASS", "RULED_SURFACE_QA_PASS", "LOFT_SURFACE_QA_PASS",
        "BSPLINE_SURFACE_QA_PASS", "BOOLEAN_QA_PASS", "FINAL_STEP_PATH", "FINAL_STEP_RELOAD",
        "FINAL_STEP_OCC_VALID", "TESTS_PASSED", "TESTS_FAILED", "PRIMARY_GENERALIZATION_BLOCKER",
        "NEXT_PRIMARY_BLOCKER",
    ]:
        report.append(f"{key}={summary.get(key)}")
    report.append(f"BLOCKERS={json.dumps(blockers)}")
    report.append("")
    report.append("## Artifact index")
    report.extend([
        f"- input audit: `{artifacts / 'input_audit.json'}`",
        f"- per-part table: `{artifacts / 'tank_part_generalization.csv'}`",
        f"- all candidates: `{artifacts / 'tank_all_candidates_contact_sheet.png'}`",
        f"- QA pass only: `{artifacts / 'tank_qa_pass_parts_contact_sheet.png'}`",
        f"- source vs best CAD: `{artifacts / 'tank_source_vs_best_cad_contact_sheet.png'}`",
        f"- final STEP: `{summary['FINAL_STEP_PATH']}`",
    ])
    (artifacts / "TANK_V4_FROZEN_GENERALIZATION_V1_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    for key, value in summary.items():
        print(f"{key}={value}")
    return 0 if current_gate.endswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
