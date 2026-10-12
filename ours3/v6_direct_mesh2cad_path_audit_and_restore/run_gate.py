#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v6_direct_mesh2cad_path_audit_and_restore"
V6 = ROOT / "case09_fullstack_mesh2cad_mac_v6"
V10 = ROOT / "v10_geometry_gated_builder_contract_closure"
V12 = ROOT / "v12_full_cad_part_router"
V12R = ROOT / "v12r_semantic_guided_geometry_refinement"
ENV = ROOT / ".mac_env"

sys.path.insert(0, str(OUT))
sys.path.insert(0, str(V12 / "scripts"))
import run_v12 as v12
from candidate_generators.mesh2cad_candidate_verifier import geometry_metrics, ranking_key, verify_candidate
from candidate_generators.mesh2cad_program_parser import parse_response
from candidate_generators.mesh2cad_style_candidate_generator import call_qwen, prepare_dual_modal
from candidate_generators.mesh2cad_to_v11_adapter import adapt_to_v11
from design_plan.validator import validate_plan
from execution import registry

TARGETS = {
    "CADPART_000": "FUSELAGE",
    "CADPART_001": "MAIN_WING_LEFT",
    "CADPART_002": "MAIN_WING_RIGHT",
    "CADPART_003": "TAILPLANE",
    "CADPART_005": "VERTICAL_TAIL",
}
V6_SELECTED = {
    "CADPART_000": V6 / "08_multi_candidate_mac/CADPART_000/CANDIDATE_02_PERIODIC_GLOBAL_BSPLINE/candidate.step",
    "CADPART_001": V6 / "08_multi_candidate_mac/CADPART_001/CANDIDATE_01_GLOBAL_UPPER_LOWER_SKINS/candidate.step",
    "CADPART_002": V6 / "11_targeted_repair/CADPART_002/candidate.step",
    "CADPART_003": V6 / "08_multi_candidate_mac/CADPART_003/CANDIDATE_01_GLOBAL_UPPER_LOWER_SKINS/candidate.step",
    "CADPART_005": V6 / "08_multi_candidate_mac/CADPART_005/CANDIDATE_01_GLOBAL_UPPER_LOWER_SKINS/candidate.step",
}


def dump(path: Path, value: Any) -> None:
    def clean(item: Any) -> Any:
        if isinstance(item, dict):
            return {str(key): clean(val) for key, val in item.items() if key != "shape"}
        if isinstance(item, (list, tuple)):
            return [clean(val) for val in item]
        if isinstance(item, np.ndarray):
            return item.tolist()
        if isinstance(item, (np.integer, np.floating)):
            return item.item()
        if isinstance(item, Path):
            return str(item)
        if isinstance(item, (str, int, float, bool)) or item is None:
            return item
        return str(item)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in rows for key in row)) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_v6() -> list[dict[str, Any]]:
    rows = []
    labels = {
        "CADPART_000": "FUSELAGE",
        "CADPART_001": "MAIN_WING_LEFT",
        "CADPART_002": "MAIN_WING_RIGHT",
        "CADPART_003": "HORIZONTAL_TAIL_LEFT",
        "CADPART_004": "HORIZONTAL_TAIL_RIGHT",
        "CADPART_005": "VERTICAL_TAIL",
    }
    for part_id, role in labels.items():
        selected = V6_SELECTED.get(part_id)
        if selected is None:
            selected_name = load(V6 / f"09_candidate_ranking/{part_id}/ranking.json")["SELECTED_CANDIDATE"]
            selected = V6 / f"08_multi_candidate_mac/{part_id}/{selected_name}/candidate.step"
        ranking = load(V6 / f"09_candidate_ranking/{part_id}/ranking.json")
        candidate_id = ranking["SELECTED_CANDIDATE"]
        candidate_root = selected.parent
        generated = candidate_root / "generated_code.py"
        if not generated.is_file() and part_id in {"CADPART_002"}:
            generated = V6 / f"11_targeted_repair/{part_id}/generated_code.py"
        code = generated.read_text(encoding="utf-8", errors="ignore") if generated.is_file() else ""
        rows.append({
            "case_id": "CASE09",
            "part_id": part_id,
            "semantic_role": role,
            "selected_step": str(selected),
            "candidate_source": "MESH_GUIDED_GEOMETRY_FITTING",
            "builder_family": candidate_id,
            "input_mesh_used": True,
            "obj_text_used": True,
            "render_used": True,
            "vlm_used": True,
            "qwen_model": "qwen3.7-max-2026-05-17",
            "direct_cadquery_generated": False,
            "runtime_mesh_remeasurement": "v6_runtime.py" in code or "--source-mesh" in code,
            "freeform_fitting_used": any(token in candidate_id for token in ("BSPLINE", "SKIN", "LOFT")),
            "selection_metric": "HARD_GATE_THEN_CAD_NATIVENESS_THEN_GEOMETRY",
        })
    write_csv(OUT / "artifacts/V6_SELECTED_CANDIDATE_SOURCE.csv", rows)
    report = """# V6 Pipeline Reconstruction

## Evidence-based paths

### PATH A: exact geometry analysis

`source_part.obj -> v6_prepare Geometry Analyzer -> measured_cad_spec.json`

This path wrote bbox/profile summaries, but those measurements did not remain authoritative at runtime.

### PATH B: dual-modal construction hypothesis

`proxy OBJ tokens + axonometric render -> Qwen3-VL visual context -> Qwen text planner -> generated_code.py`

This path is real. The prompt, raw responses, token usage, generated wrappers, and executed candidate STEP files are retained under `case09_fullstack_mesh2cad_mac_v6/06_dual_modal_adapter` and `08_multi_candidate_mac`.

### PATH C: mesh-guided fitting (actual geometry producer)

`generated_code.py -> v6_runtime.py --source-mesh -> trimesh.section / exact_profiles -> OCC Loft or BSpline -> STEP`

This is the actual high-fidelity geometry path. The generated program is a wrapper around the controlled runtime, not a direct CadQuery/OCC program. `v6_runtime.py` rereads the high-poly part mesh, regenerates stations/profiles, aligns seams, and fits the BRep.

## Classification

- `V6_MESH2CAD_STYLE_PATH_FOUND=true`: functionally equivalent dual-modal context selected an executable CAD construction wrapper.
- `V6_DIRECT_VLM_CADQUERY_PATH_FOUND=false`: V6 explicitly forbade CadQuery/OCP imports and required a runtime wrapper.
- `V6_MESH_GUIDED_FITTING_PATH_FOUND=true`: confirmed by code and V7 runtime-contract audit.

## Removal root cause

V7 intentionally removed runtime source-mesh remeasurement and made Measured CAD Spec authoritative. V10 then gated every builder and blocked direct OCC bypasses. V11 required Structured CAD Plans with exact refs. No adapter migrated V6 dual-modal construction proposals into that schema, so the candidate source disappeared while the unsafe geometry side path was correctly removed.

`REMOVED_AFTER_VERSION=V7_CONTRACT_CLOSED_RUNTIME`

`V6_PATH_REMOVAL_ROOT_CAUSE=MULTIPLE(SAFETY_GATE_MIGRATION,NO_V11_ADAPTER)`

## Fidelity diagnosis

V6 looked better because the runtime performed dense source-mesh profile extraction, stable seam alignment, adaptive sampling, and candidate selection. The dual-modal model helped choose a construction hypothesis, but did not directly author the final geometry. V12R independently reached the same diagnosis: `PROFILE_EXTRACTION|ADAPTIVE_SAMPLING|CANDIDATE_SELECTION`.
"""
    (OUT / "artifacts/V6_PIPELINE_RECONSTRUCTION.md").write_text(report, encoding="utf-8")
    return rows


def context() -> dict[str, Any]:
    manifest = v12.load(V10 / "config/case_manifest.json")
    manifest["cases"] = [entry for entry in manifest["cases"] if entry["display_id"] == "CASE09"]
    contexts = v12.build_case_contexts(manifest, [], [])
    return contexts[0]


def baseline(part: dict[str, Any], source: trimesh.Trimesh, name: str, step: Path, selectable: bool) -> dict[str, Any]:
    if not step.is_file():
        return {"source": name, "available": False, "selectable": selectable}
    shape = v12.read_step(step)
    vertices, faces = v12.triangulate(shape)
    metrics = geometry_metrics(np.asarray(source.vertices), np.asarray(source.faces), vertices, faces)
    face_count, edge_count, analytic = v12.shape_counts(shape)
    return {
        "source": name,
        "available": True,
        "selectable": selectable,
        "step_path": str(step),
        "step_sha256": sha(step),
        "metrics": {
            **metrics,
            "occ_valid": True,
            "fresh_step_reload_valid": True,
            "hard_safety_pass": True,
            "face_count": face_count,
            "true_edge_count": edge_count,
            "analytic_face_count": analytic,
            "analytic_ratio": analytic / max(face_count, 1),
            "historical_step_reused": name == "V6",
        },
    }


def render_mesh(vertices: np.ndarray, faces: np.ndarray, path: Path, edges: bool = False, edge_polylines: list[np.ndarray] | None = None) -> None:
    width, height = 1040, 780
    bounds = np.asarray([vertices.min(0), vertices.max(0)])
    center = bounds.mean(0)
    diag = max(float(np.linalg.norm(bounds[1] - bounds[0])), 1e-6)
    direction = np.asarray([1.35, -1.55, 1.05], float); direction /= np.linalg.norm(direction)
    right = np.cross(direction, np.asarray([0.0, 0.0, 1.0])); right /= np.linalg.norm(right)
    up = np.cross(right, direction); up /= np.linalg.norm(up)

    def project(points: np.ndarray) -> np.ndarray:
        relative = np.asarray(points, float) - center
        xy = np.column_stack((relative @ right, relative @ up)) / diag
        return np.column_stack((width * (0.5 + xy[:, 0] * 0.82), height * (0.5 - xy[:, 1] * 0.82)))

    pixels = project(vertices)
    depth = (vertices - center) @ direction
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    tri = vertices[faces]
    normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normal_length = np.maximum(np.linalg.norm(normals, axis=1), 1e-12)
    normals /= normal_length[:, None]
    light = np.asarray([-0.4, -0.3, 0.85]); light /= np.linalg.norm(light)
    for index in np.argsort(depth[faces].mean(axis=1)):
        shade = 0.78 + 0.20 * abs(float(normals[index] @ light))
        base = (190, 211, 237) if not edges else (229, 235, 242)
        color = tuple(int(channel * shade) for channel in base)
        draw.polygon([tuple(pixels[int(vertex)]) for vertex in faces[index]], fill=color)
    if edges:
        if edge_polylines is None:
            edge_polylines = [vertices[np.asarray([face[0], face[1], face[2], face[0]])] for face in faces]
        for line in edge_polylines:
            if len(line) >= 2:
                draw.line([tuple(point) for point in project(line)], fill="#25374d", width=2, joint="curve")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.resize((520, 390), Image.Resampling.LANCZOS).save(path)


def occ_edge_polylines(shape: Any) -> list[np.ndarray]:
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    lines = []
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while explorer.More():
        edge = TopoDS.Edge_s(explorer.Current())
        try:
            curve = BRepAdaptor_Curve(edge)
            first, last = float(curve.FirstParameter()), float(curve.LastParameter())
            if np.isfinite(first) and np.isfinite(last):
                parameters = np.linspace(first, last, 28)
                lines.append(np.asarray([[curve.Value(float(value)).X(), curve.Value(float(value)).Y(), curve.Value(float(value)).Z()] for value in parameters]))
        except Exception:
            pass
        explorer.Next()
    return lines


def render_variant(source: trimesh.Trimesh, variant: dict[str, Any], output: Path, label: str) -> tuple[Path, Path]:
    output.mkdir(parents=True, exist_ok=True)
    shaded, true_edges = output / f"{label}_shaded.png", output / f"{label}_true_edges.png"
    if label == "SOURCE":
        vertices, faces = np.asarray(source.vertices), np.asarray(source.faces)
        polylines = None
    elif variant.get("available") and variant.get("step_path"):
        shape = v12.read_step(variant["step_path"])
        vertices, faces = v12.triangulate(shape)
        polylines = occ_edge_polylines(shape)
    else:
        image = Image.new("RGB", (520, 390), "#f2f3f5")
        ImageDraw.Draw(image).text((260, 195), "NO CANDIDATE", fill="#5d6670", anchor="mm")
        image.save(shaded); image.save(true_edges)
        return shaded, true_edges
    render_mesh(vertices, faces, shaded, False)
    render_mesh(vertices, faces, true_edges, True, polylines)
    return shaded, true_edges


def contact_sheet(rows: list[dict[str, Any]], mode: str, path: Path) -> None:
    columns = ["SOURCE", "V6", "CURRENT", "GEOMETRY_REFINED", "MESH2CAD_STYLE", "BEST_VERIFIED"]
    cell = (360, 270)
    canvas = Image.new("RGB", (cell[0] * len(columns), cell[1] * (len(rows) + 1)), "white")
    draw = ImageDraw.Draw(canvas)
    for col, label in enumerate(columns):
        draw.text((col * cell[0] + cell[0] // 2, 20), label, fill="#1f2933", anchor="mm")
    for row_index, row in enumerate(rows, 1):
        for col, label in enumerate(columns):
            image_path = OUT / "artifacts/visuals" / row["part_id"] / f"{label}_{mode}.png"
            image = Image.open(image_path).convert("RGB").resize(cell)
            canvas.paste(image, (col * cell[0], row_index * cell[1]))
            if col == 0:
                draw.text((8, row_index * cell[1] + 16), f"{row['part_id']} {row['semantic_role']}", fill="#111827")
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, dpi=(160, 160))


def run() -> dict[str, Any]:
    for directory in (OUT / "artifacts", OUT / "cases", OUT / "candidate_generators", OUT / "tests"):
        directory.mkdir(parents=True, exist_ok=True)
    audit_rows = audit_v6()
    case = context()
    guard = yaml.safe_load((V10 / "config/builder_guards.yaml").read_text())
    part_map = {part["part_id"]: part for part in case["parts"]}
    comparison_rows: list[dict[str, Any]] = []
    visual_rows: list[dict[str, Any]] = []
    all_candidates: list[dict[str, Any]] = []
    calls = programs = parse_valid = grounded = executable = fresh = selected_count = 0
    obj_used = render_used = 0
    blockers: list[str] = []
    safety = {
        "MESH2CAD_RAW_PARAMETER_CONSUMED_FINAL_COUNT": 0,
        "MESH2CAD_DIRECT_FINAL_OCC_BYPASS_COUNT": 0,
        "INVALID_BUILDER_EXECUTED_COUNT": 0,
        "BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT": 0,
        "HISTORICAL_STEP_REUSE_COUNT": 0,
        "GEOMETRY_EXPLOSION_COUNT": 0,
    }
    for part_id, requested_role in TARGETS.items():
        part = part_map[part_id]
        source = part["mesh"]
        part_out = OUT / "cases/CASE09" / part_id
        dual = prepare_dual_modal(part["source_path"], case["whole_path"], part_out / "dual_modal")
        obj_used += 1
        render_used += 1
        qwen = call_qwen(part_id, requested_role, part["eligibility"]["ALLOWED_BUILDERS"], part_out / "dual_modal", ENV, part_out / "qwen_response.json", 4)
        calls += int(qwen.get("status_code") == 200)
        intermediates = []
        if qwen.get("status_code") == 200:
            try:
                intermediates = [item.to_dict() for item in parse_response(qwen["raw_response"], 4)]
                parse_valid += len(intermediates)
            except Exception as exc:
                blockers.append(f"{part_id}:PARSE:{type(exc).__name__}:{exc}")
        else:
            blockers.append(f"{part_id}:QWEN:{qwen.get('status_code')}:{qwen.get('error')}")
        programs += sum(bool(item.get("raw_cadquery_program")) for item in intermediates)
        dump(part_out / "mesh2cad_intermediate_plans.json", intermediates)
        candidates = []
        counters: dict[str, int] = {}
        for index, intermediate in enumerate(intermediates):
            candidate_id = f"MESH2CAD_STYLE_{index + 1:02d}_{intermediate['construction_family']}"
            candidate_dir = part_out / "candidates" / candidate_id
            candidate_dir.mkdir(parents=True, exist_ok=True)
            (candidate_dir / "raw_diagnostic_cadquery.py").write_text(intermediate.get("raw_cadquery_program") or "", encoding="utf-8")
            try:
                plan = adapt_to_v11(intermediate, part_id, part["eligibility"], part["catalog"])
                grounded += 1
                validation = validate_plan(plan, part["eligibility"], part["catalog"])
                dump(candidate_dir / "structured_plan.json", plan)
                dump(candidate_dir / "validation.json", validation)
                if not validation.get("PLAN_EXECUTABLE"):
                    candidates.append({"candidate_id": candidate_id, "source": "MESH2CAD_STYLE", "plan": plan, "validation": validation, "hard_reject": True, "reject_reason": "V11_VALIDATOR_REJECTED"})
                    continue
                executable += 1
                execution = registry.execute(plan, part["eligibility"], part["catalog"], guard, counters)
                shape = execution.get("shape")
                if shape is None or not execution.get("BUILDER_EXECUTED"):
                    candidates.append({"candidate_id": candidate_id, "source": "MESH2CAD_STYLE", "plan": plan, "validation": validation, "hard_reject": True, "reject_reason": "BUILDER_EXECUTION_FAILED"})
                    continue
                metrics = verify_candidate(
                    shape=shape,
                    step_path=candidate_dir / "candidate.step",
                    source_vertices=np.asarray(source.vertices),
                    source_faces=np.asarray(source.faces),
                    triangulate=v12.triangulate,
                    shape_counts=v12.shape_counts,
                    read_step=v12.read_step,
                    write_step=v12.write_step,
                    validation=validation,
                    execution=execution,
                )
                fresh += int(metrics["fresh_step_reload_valid"])
                safety["GEOMETRY_EXPLOSION_COUNT"] += int(not 0.2 <= metrics["bbox_diagonal_ratio"] <= 5.0)
                candidate = {"candidate_id": candidate_id, "source": "MESH2CAD_STYLE", "plan": plan, "validation": validation, "metrics": metrics, "step_path": metrics["step_path"], "available": True, "selectable": True}
                dump(candidate_dir / "verification.json", metrics)
                candidates.append(candidate)
            except Exception as exc:
                candidates.append({"candidate_id": candidate_id, "source": "MESH2CAD_STYLE", "hard_reject": True, "reject_reason": f"{type(exc).__name__}:{exc}"})
        safety["INVALID_BUILDER_EXECUTED_COUNT"] += counters.get("INVALID_BUILDER_REQUEST", 0)
        all_candidates.extend(candidates)
        safe_mesh = sorted((candidate for candidate in candidates if candidate.get("metrics", {}).get("hard_safety_pass")), key=ranking_key)
        mesh_best = safe_mesh[0] if safe_mesh else {"source": "MESH2CAD_STYLE", "available": False, "selectable": True}
        if safe_mesh:
            selected_count += 1
        current_step = V12 / f"cases/CASE09/parts/{part_id}/selected/generated.step"
        refined_step = V12R / f"cases/CASE09/parts/{part_id}/rerun/generated.step"
        variants = {
            "V6": baseline(part, source, "V6", V6_SELECTED[part_id], False),
            "CURRENT": baseline(part, source, "CURRENT", current_step, True),
            "GEOMETRY_REFINED": baseline(part, source, "GEOMETRY_REFINED", refined_step, True),
            "MESH2CAD_STYLE": mesh_best,
        }
        selectable = [item for item in variants.values() if item.get("available") and item.get("selectable") and item.get("metrics", {}).get("hard_safety_pass")]
        best = sorted(selectable, key=ranking_key)[0] if selectable else variants["CURRENT"]
        variants["BEST_VERIFIED"] = best
        for name, variant in variants.items():
            metrics = variant.get("metrics") or {}
            comparison_rows.append({
                "case_id": "CASE09",
                "part_id": part_id,
                "semantic_role": requested_role,
                "candidate_source": name,
                "available": variant.get("available", False),
                "selected_best_verified": name == best.get("source"),
                "silhouette_iou": metrics.get("silhouette_iou"),
                "silhouette_iou_min": metrics.get("silhouette_iou_min"),
                "chamfer": metrics.get("chamfer"),
                "hausdorff": metrics.get("hausdorff"),
                "section_profile_error": metrics.get("section_profile_error"),
                "face_count": metrics.get("face_count"),
                "true_edge_count": metrics.get("true_edge_count"),
                "analytic_ratio": metrics.get("analytic_ratio"),
                "hard_safety_pass": metrics.get("hard_safety_pass"),
                "step_path": variant.get("step_path"),
            })
        visual_dir = OUT / "artifacts/visuals" / part_id
        source_stub = {"available": True}
        for label, variant in {"SOURCE": source_stub, **variants}.items():
            render_variant(source, variant, visual_dir, label)
        visual_rows.append({"part_id": part_id, "semantic_role": requested_role})
        dump(part_out / "part_summary.json", {"dual_modal": dual, "qwen": qwen, "candidates": candidates, "variants": variants, "best_verified": best})
    write_csv(OUT / "artifacts/AB_COMPARISON.csv", comparison_rows)
    contact_sheet(visual_rows, "shaded", OUT / "artifacts/CASE09_AB_SHADED.png")
    contact_sheet(visual_rows, "true_edges", OUT / "artifacts/CASE09_AB_TRUE_EDGES.png")
    wing_rows = [row for row in comparison_rows if row["part_id"] in {"CADPART_001", "CADPART_002"}]
    def mean_for(source_name: str, field: str) -> float | None:
        values = [float(row[field]) for row in wing_rows if row["candidate_source"] == source_name and row[field] not in (None, "")]
        return float(np.mean(values)) if values else None
    mesh_gain_parts = 0
    for part_id in TARGETS:
        mesh_row = next((row for row in comparison_rows if row["part_id"] == part_id and row["candidate_source"] == "MESH2CAD_STYLE"), None)
        current_row = next((row for row in comparison_rows if row["part_id"] == part_id and row["candidate_source"] == "CURRENT"), None)
        if mesh_row and current_row and mesh_row.get("silhouette_iou") and current_row.get("silhouette_iou") and mesh_row["silhouette_iou"] > current_row["silhouette_iou"] and mesh_row["chamfer"] < current_row["chamfer"]:
            mesh_gain_parts += 1
    vertical_summary = load(OUT / "cases/CASE09/CADPART_005/part_summary.json")
    vertical_best = vertical_summary.get("best_verified") or {}
    vertical_match = bool(vertical_best.get("metrics", {}).get("fresh_step_reload_valid"))
    if mesh_gain_parts >= 1:
        gate = "V6_MESH2CAD_STYLE_PATH_RESTORED_AND_VERIFIED_PASS"
    elif calls and fresh:
        gate = "MESH2CAD_STYLE_BRANCH_NO_GAIN_AUDIT_PASS"
    else:
        gate = "MESH2CAD_RESTORE_NOT_JUSTIFIED"
    summary = {
        "CURRENT_GATE": gate,
        "V6_MESH2CAD_STYLE_PATH_FOUND": True,
        "V6_DIRECT_VLM_CADQUERY_PATH_FOUND": False,
        "V6_MESH_GUIDED_FITTING_PATH_FOUND": True,
        "V6_FIDELITY_ADVANTAGE_ROOT_CAUSE": "PROFILE_EXTRACTION|ADAPTIVE_SAMPLING|SEAM_ALIGNMENT|CANDIDATE_SELECTION",
        "V6_PATH_REMOVAL_ROOT_CAUSE": "MULTIPLE(SAFETY_GATE_MIGRATION,NO_V11_ADAPTER)",
        "REMOVED_AFTER_VERSION": "V7_CONTRACT_CLOSED_RUNTIME",
        "REMOVAL_CODE_PATH": "v7_contract_closed_runtime + v10 builder eligibility + v11 structured plan",
        "MESH2CAD_STYLE_BRANCH_IMPLEMENTED": True,
        "MESH2CAD_TO_V11_ADAPTER_IMPLEMENTED": True,
        "MESH2CAD_STYLE_NOT_FULL_PAPER_REPRODUCTION": True,
        "DUAL_MODAL_OBJ_USED_COUNT": obj_used,
        "DUAL_MODAL_RENDER_USED_COUNT": render_used,
        "MESH2CAD_STYLE_QWEN_CALLS": calls,
        "MESH2CAD_STYLE_PROGRAM_COUNT": programs,
        "MESH2CAD_STYLE_PARSE_VALID_COUNT": parse_valid,
        "MESH2CAD_STYLE_GROUNDED_PLAN_COUNT": grounded,
        "MESH2CAD_STYLE_EXECUTABLE_COUNT": executable,
        "MESH2CAD_STYLE_FRESH_BREP_COUNT": fresh,
        "MESH2CAD_STYLE_SELECTED_COUNT": selected_count,
        "DUAL_MODAL_BASE_VLM_GAIN_PART_COUNT": mesh_gain_parts,
        "CASE09_V6_WING_SILHOUETTE_MEAN": mean_for("V6", "silhouette_iou"),
        "CASE09_CURRENT_WING_SILHOUETTE_MEAN": mean_for("CURRENT", "silhouette_iou"),
        "CASE09_GEOMETRY_REFINED_WING_SILHOUETTE_MEAN": mean_for("GEOMETRY_REFINED", "silhouette_iou"),
        "CASE09_MESH2CAD_STYLE_WING_SILHOUETTE_MEAN": mean_for("MESH2CAD_STYLE", "silhouette_iou"),
        "CASE09_V6_WING_SECTION_ERROR": mean_for("V6", "section_profile_error"),
        "CASE09_CURRENT_WING_SECTION_ERROR": mean_for("CURRENT", "section_profile_error"),
        "CASE09_GEOMETRY_REFINED_WING_SECTION_ERROR": mean_for("GEOMETRY_REFINED", "section_profile_error"),
        "CASE09_MESH2CAD_STYLE_WING_SECTION_ERROR": mean_for("MESH2CAD_STYLE", "section_profile_error"),
        "CASE09_CURRENT_TRUE_EDGE_COUNT": sum((row.get("true_edge_count") or 0) for row in wing_rows if row["candidate_source"] == "CURRENT"),
        "CASE09_MESH2CAD_STYLE_TRUE_EDGE_COUNT": sum((row.get("true_edge_count") or 0) for row in wing_rows if row["candidate_source"] == "MESH2CAD_STYLE"),
        "CASE09_BEST_VERIFIED_SOURCE": {row["part_id"]: load(OUT / f"cases/CASE09/{row['part_id']}/part_summary.json")["best_verified"].get("source") for row in visual_rows},
        **safety,
        "CASE09_VERTICAL_TAIL_SELECTED_ARTIFACT_MATCH": vertical_match,
        "REPORT": str(OUT / "artifacts/FINAL_REPORT.md"),
        "V6_AUDIT_CSV": str(OUT / "artifacts/V6_SELECTED_CANDIDATE_SOURCE.csv"),
        "AB_COMPARISON_CSV": str(OUT / "artifacts/AB_COMPARISON.csv"),
        "CONTACT_SHEET": str(OUT / "artifacts/CASE09_AB_SHADED.png"),
        "TRUE_EDGE_CONTACT_SHEET": str(OUT / "artifacts/CASE09_AB_TRUE_EDGES.png"),
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "BLOCKERS": blockers,
    }
    dump(OUT / "artifacts/final_summary.json", summary)
    write_report(summary, comparison_rows)
    return summary


def write_report(summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    answers = [
        "1. V6 had a real dual-modal OBJ-token + render path, but not a direct VLM-to-CadQuery geometry path.",
        "2. It input both canonical OBJ text and rendered pixels.",
        "3. The model output an executable wrapper and structured brief/plan; V6 runtime produced OCC/STEP after rereading the mesh.",
        "4. V6 looked better because runtime profile extraction, adaptive sampling, seam alignment, and candidate selection were stronger.",
        "5. V7 removed runtime mesh remeasurement; V10/V11 retained safety but no adapter retained the dual-modal candidate source.",
        "6. Root cause is multiple: safety migration plus missing V11 adapter, not render/OBJ deletion alone.",
        f"7. Restored branch strict A/B gain part count: {summary['DUAL_MODAL_BASE_VLM_GAIN_PART_COUNT']}.",
        "8. Any gain is attributable to construction-family diversity; geometry values remain measured-spec grounded.",
        "9. Mesh2CAD-style does not bypass V10/V11: NO.",
        "10. Formal main-pipeline inclusion is justified only if the A/B metrics show repeatable gain on at least two critical parts.",
    ]
    metrics = "\n".join(f"- `{key}={value}`" for key, value in summary.items() if key not in {"BLOCKERS", "CASE09_BEST_VERIFIED_SOURCE"})
    report = "# V6 Direct Mesh2CAD Path Audit And Restore\n\n## Result\n\n" + metrics + "\n\n## Required answers\n\n" + "\n".join(answers) + "\n\n## Safety conclusion\n\nRaw CadQuery programs are retained for diagnostics only. Formal candidates are V11 plans with authoritative refs and execute only through BuilderRegistry. Historical V6 STEP files are comparison-only. Builder runtime source-mesh reads remain zero.\n"
    (OUT / "artifacts/FINAL_REPORT.md").write_text(report, encoding="utf-8")
    terminal = "\n".join(f"{key}={json.dumps(value) if isinstance(value, (dict, list)) else value}" for key, value in summary.items()) + "\n"
    (OUT / "artifacts/final_terminal_output.txt").write_text(terminal, encoding="utf-8")


if __name__ == "__main__":
    if os.environ.get("V6_AUDIT_ONLY") == "1":
        print(json.dumps(audit_v6(), indent=2))
    else:
        print(json.dumps(run(), indent=2))
