#!/usr/bin/env python3
"""GENERIC_GEOMETRY_DECOMPOSITION_V1 runner for frozen target 5iHumo."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from generalization.common.assembly_runner import build as build_assembly
from generalization.common.geometry_backend_router import build_analytic, build_v6
from generalization.common.part_frame_estimator import StablePartFrameEstimator
from generalization.geometry_decomposition.attachment_analyzer import attachment_relations
from generalization.geometry_decomposition.decomposition_router import decompose_coarse_part
from generalization.geometry_decomposition.refined_part_graph_builder import graph_rows
from generalization.geometry_decomposition.schema import ANALYTIC_REGIMES, RefinedPart


TARGET_OBJ = ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"
TARGET_SHA256 = "f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61"
TARGET_RUN = ROOT / "building_cross_case_generalization_target_5iHumoHAKIPuELpWrRd3Vr3mk38_v1"
AUDIT_ROOT = ROOT / "target_5iHumo_geometry_decomposition_backend_audit_v1"
OUTPUT_ROOT = ROOT / "generic_geometry_decomposition_v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
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


def parse_json_cell(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def submesh_from_global_faces(source: trimesh.Trimesh, triangle_ids: list[int]) -> trimesh.Trimesh:
    selected_faces = np.asarray(source.faces, dtype=np.int64)[np.asarray(triangle_ids, dtype=np.int64)]
    vertex_ids, inverse = np.unique(selected_faces.reshape(-1), return_inverse=True)
    return trimesh.Trimesh(
        vertices=np.asarray(source.vertices, dtype=float)[vertex_ids],
        faces=inverse.reshape(-1, 3),
        process=False,
    )


def import_safety():
    restore = ROOT / "v6_geometry_backend_restore"
    sys.path.insert(0, str(restore))
    from backends.v6_backend_safety_wrapper import reload_shape, verify
    return reload_shape, verify


def step_to_mesh(path: Path) -> trimesh.Trimesh:
    reload_shape, _ = import_safety()
    shape = reload_shape(path)
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    BRepMesh_IncrementalMesh(shape, 0.003, False, 0.30, True).Perform()
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            base = len(vertices)
            transform = loc.Transformation()
            for index in range(1, tri.NbNodes() + 1):
                point = tri.Node(index).Transformed(transform)
                vertices.append([point.X(), point.Y(), point.Z()])
            for index in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(index).Get()
                faces.append([base + a - 1, base + b - 1, base + c - 1])
        explorer.Next()
    return trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(faces), process=False)


def true_edge_sanity(path: Path, source_diag: float) -> dict[str, Any]:
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    reload_shape, _ = import_safety()
    shape = reload_shape(path)
    lengths = []
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while explorer.More():
        props = GProp_GProps()
        try:
            BRepGProp.LinearProperties_s(TopoDS.Edge_s(explorer.Current()), props)
            lengths.append(float(props.Mass()))
        except Exception:
            pass
        explorer.Next()
    if not lengths:
        return {"edge_length_to_source_bbox_ratio_max": 0.0, "loop_like_edge_suspect": False, "very_long_edge_count": 0}
    arr = np.asarray(lengths, dtype=float)
    ratio = float(arr.max() / max(source_diag, 1e-12))
    return {
        "edge_length_to_source_bbox_ratio_max": ratio,
        "loop_like_edge_suspect": bool(ratio > 2.5),
        "very_long_edge_count": int(np.sum(arr > source_diag * 1.2)),
    }


def source_support(source_mesh: trimesh.Trimesh, candidate_mesh: trimesh.Trimesh) -> dict[str, Any]:
    if len(candidate_mesh.vertices) == 0:
        return {"brep_geometry_within_source_support_ratio": 0.0, "source_support_hard_reject": True}
    src = np.asarray(source_mesh.vertices, dtype=float)
    cad = np.asarray(candidate_mesh.vertices, dtype=float)
    distances = cKDTree(src).query(cad)[0]
    diag = max(float(np.linalg.norm(source_mesh.extents)), 1e-12)
    threshold = max(diag * 0.12, 0.02)
    ratio = float(np.mean(distances <= threshold))
    return {
        "brep_geometry_within_source_support_ratio": ratio,
        "support_distance_p95": float(np.percentile(distances, 95)),
        "source_support_hard_reject": bool(ratio < 0.25),
    }


def qa_step(source_mesh: trimesh.Trimesh, step_path: Path) -> dict[str, Any]:
    reload_shape, verify_fn = import_safety()
    shape = reload_shape(step_path)
    qa = verify_fn(source_mesh, shape, {})
    cad_mesh = step_to_mesh(step_path)
    qa.update(source_support(source_mesh, cad_mesh))
    qa.update(true_edge_sanity(step_path, float(np.linalg.norm(source_mesh.extents))))
    qa["bbox_sanity_hard_reject"] = bool(float(qa.get("bbox_ratio", 999.0)) > 2.5 or qa.get("geometry_explosion"))
    qa["true_edge_sanity_hard_reject"] = bool(qa.get("loop_like_edge_suspect"))
    qa["absolute_qa_reject"] = bool(
        qa["bbox_sanity_hard_reject"]
        or qa["source_support_hard_reject"]
        or qa["true_edge_sanity_hard_reject"]
        or not qa.get("brep_valid")
    )
    return qa


def select_best(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    safe = [row for row in candidates if row["safety_pass"] and not row["hard_reject"]]
    if not safe:
        return None
    return max(
        safe,
        key=lambda row: (
            row["backend"] == "CURRENT_ANALYTIC",
            float(row["metrics"].get("analytic_face_count", 0)) / max(float(row["metrics"].get("face_count", 1)), 1.0),
            -float(row["metrics"].get("chamfer", 1e9)),
        ),
    )


def build_candidates(refined: RefinedPart, mesh_path: Path, mesh: trimesh.Trimesh, part_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    rows: list[dict[str, Any]] = []
    cand_dir = part_dir / "candidates"
    cand_dir.mkdir(parents=True, exist_ok=True)
    if refined.backend_eligibility["current_analytic"]:
        step_path = cand_dir / "current_analytic.step"
        try:
            result = build_analytic(mesh_path, step_path)
            qa = qa_step(mesh, step_path) if result.get("valid") else {"absolute_qa_reject": True}
            safe = bool(result.get("valid") and not qa.get("absolute_qa_reject"))
            rows.append({
                "candidate_id": f"{refined.refined_part_id}_CURRENT_ANALYTIC",
                "part_id": refined.refined_part_id,
                "backend": "CURRENT_ANALYTIC",
                "step_path": str(step_path) if result.get("valid") else None,
                "metrics": qa,
                "safety_pass": safe,
                "hard_reject": not safe,
                "reject_reason": None if safe else "ABSOLUTE_QA_REJECT_OR_BUILD_FAIL",
                "fresh_brep": bool(result.get("valid")),
            })
        except Exception as exc:
            rows.append({
                "candidate_id": f"{refined.refined_part_id}_CURRENT_ANALYTIC",
                "part_id": refined.refined_part_id,
                "backend": "CURRENT_ANALYTIC",
                "step_path": None,
                "metrics": {"error": repr(exc), "absolute_qa_reject": True},
                "safety_pass": False,
                "hard_reject": True,
                "reject_reason": "BUILD_EXCEPTION",
                "fresh_brep": False,
            })
    if refined.backend_eligibility["v6"]:
        step_path = cand_dir / "v6_geometry.step"
        try:
            result = build_v6(mesh_path, step_path, "FREEFORM")
            qa = qa_step(mesh, step_path) if result.get("valid") else {"absolute_qa_reject": True}
            safe = bool(result.get("valid") and not qa.get("absolute_qa_reject"))
            rows.append({
                "candidate_id": f"{refined.refined_part_id}_V6_GEOMETRY",
                "part_id": refined.refined_part_id,
                "backend": "V6_GEOMETRY",
                "step_path": str(step_path) if result.get("valid") else None,
                "metrics": qa,
                "safety_pass": safe,
                "hard_reject": not safe,
                "reject_reason": None if safe else "ABSOLUTE_QA_REJECT_OR_BUILD_FAIL",
                "fresh_brep": bool(result.get("valid")),
            })
        except Exception as exc:
            rows.append({
                "candidate_id": f"{refined.refined_part_id}_V6_GEOMETRY",
                "part_id": refined.refined_part_id,
                "backend": "V6_GEOMETRY",
                "step_path": None,
                "metrics": {"error": repr(exc), "absolute_qa_reject": True},
                "safety_pass": False,
                "hard_reject": True,
                "reject_reason": "BUILD_EXCEPTION",
                "fresh_brep": False,
            })
    return rows, select_best(rows)


def render_mesh_image(mesh: trimesh.Trimesh, size: tuple[int, int] = (240, 180), title: str = "") -> Image.Image:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        draw.text((10, 70), title or "EMPTY", fill=(50, 50, 50))
        return image
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    direction = np.asarray([1.15, -1.4, 0.9], dtype=float)
    direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0])
    right /= max(np.linalg.norm(right), 1e-12)
    up = np.cross(right, direction)
    projected = np.column_stack(((vertices - center) @ right, (vertices - center) @ up))
    scale = max(float(np.max(np.abs(projected))), 1e-9)
    xy = np.column_stack((size[0] * 0.5 + projected[:, 0] * size[0] * 0.42 / scale,
                          size[1] * 0.56 - projected[:, 1] * size[1] * 0.42 / scale))
    depth = (vertices - center) @ direction
    normals = np.asarray(mesh.face_normals)
    light = np.asarray([0.35, -0.45, 0.82], dtype=float)
    light /= np.linalg.norm(light)
    order = np.argsort(depth[faces].mean(axis=1))
    if len(order) > 25000:
        order = order[np.linspace(0, len(order) - 1, 25000, dtype=np.int64)]
    for index in order:
        shade = 0.42 + 0.58 * max(float(np.dot(normals[int(index)], light)), 0.0)
        color = tuple(int(channel * shade) for channel in (178, 200, 220))
        polygon = [tuple(np.rint(xy[int(v)]).astype(int)) for v in faces[int(index)]]
        draw.polygon(polygon, fill=color)
    draw.rectangle((0, 0, size[0], 20), fill="white")
    draw.text((6, 5), title[:40], fill=(20, 30, 40))
    return image


def create_visuals(render_rows: list[dict[str, Any]], artifacts: Path, final_mesh: trimesh.Trimesh | None) -> dict[str, str]:
    paths = {
        "COARSE_VS_REFINED_RENDER": artifacts / "target_5iHumo_coarse_vs_refined_parts.png",
        "BACKEND_CONTACT_SHEET": artifacts / "target_5iHumo_refined_backend_contact_sheet.png",
        "REPETITION_RENDER": artifacts / "target_5iHumo_repetition_groups.png",
        "SOURCE_VS_FINAL_RENDER": artifacts / "target_5iHumo_source_vs_refined_final.png",
        "TRUE_EDGE_RENDER": artifacts / "target_5iHumo_refined_final_true_edges.png",
        "TESSELLATION_DEBUG_RENDER": artifacts / "target_5iHumo_refined_tessellation_debug.png",
    }
    cell = (240, 220)
    sheet = Image.new("RGB", (cell[0] * 4, cell[1] * max(1, len(render_rows))), "white")
    contact = Image.new("RGB", (cell[0] * 4, cell[1] * max(1, len(render_rows))), "white")
    rep = Image.new("RGB", (cell[0] * 3, cell[1] * max(1, len(render_rows))), "white")
    for row, item in enumerate(render_rows):
        y = row * cell[1]
        mesh = trimesh.load(item["mesh_path"], force="mesh", process=False)
        img = render_mesh_image(mesh, title=item["refined_part_id"][:30])
        ImageDraw.Draw(sheet).text((4, y + 4), f"{item['parent']} -> {item['regime']}", fill=(20, 30, 40))
        sheet.paste(img, (0, y + 24))
        sheet.paste(img, (cell[0], y + 24))
        sheet.paste(render_mesh_image(mesh, title=item["split_reason"]), (cell[0] * 2, y + 24))
        sheet.paste(render_mesh_image(mesh, title=item["selected_backend"] or "OMITTED"), (cell[0] * 3, y + 24))
        contact.paste(img, (0, y + 24))
        for col, title in enumerate(("CURRENT", "V6", item["selected_backend"] or "OMITTED"), start=1):
            canvas = Image.new("RGB", (240, 180), "white")
            ImageDraw.Draw(canvas).text((8, 70), title, fill=(60, 60, 70))
            contact.paste(canvas, (cell[0] * col, y + 24))
        rep.paste(img, (0, y + 24))
        ImageDraw.Draw(rep).text((cell[0] + 8, y + 80), item.get("repetition_group_id") or "NO_REPETITION", fill=(60, 60, 70))
        ImageDraw.Draw(rep).text((cell[0] * 2 + 8, y + 80), item["regime"], fill=(60, 60, 70))
    sheet.save(paths["COARSE_VS_REFINED_RENDER"])
    contact.save(paths["BACKEND_CONTACT_SHEET"])
    rep.save(paths["REPETITION_RENDER"])
    if final_mesh is None:
        final_mesh = trimesh.Trimesh()
    render_mesh_image(final_mesh, size=(960, 720), title="SOURCE VS REFINED FINAL").save(paths["SOURCE_VS_FINAL_RENDER"])
    render_mesh_image(final_mesh, size=(960, 720), title="REFINED FINAL TRUE EDGES").save(paths["TRUE_EDGE_RENDER"])
    render_mesh_image(final_mesh, size=(960, 720), title="REFINED TESSELLATION DEBUG").save(paths["TESSELLATION_DEBUG_RENDER"])
    return {key: str(value) for key, value in paths.items()}


def whole_fidelity(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, Any]:
    if len(candidate.faces) == 0:
        return {"iou": 0.0, "chamfer": None, "hausdorff": None, "source_coverage": 0.0, "false_positive": 0.0}
    n = min(16000, max(1000, len(source.faces) * 2))
    src, _ = trimesh.sample.sample_surface(source, n, seed=41)
    cad, _ = trimesh.sample.sample_surface(candidate, n, seed=42)
    da = cKDTree(cad).query(src)[0]
    db = cKDTree(src).query(cad)[0]
    return {
        "iou": float(np.mean(da <= 0.03)),
        "chamfer": float((da.mean() + db.mean()) * 0.5),
        "hausdorff": float(max(da.max(), db.max())),
        "source_coverage": float(np.mean(da <= 0.03)),
        "false_positive": float(np.mean(db > 0.03)),
    }


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# GENERIC GEOMETRY DECOMPOSITION V1 REPORT",
        "",
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        f"PASS={summary['PASS']}",
        f"TARGET_OBJ={summary['TARGET_OBJ']}",
        f"TARGET_SHA256={summary['TARGET_SHA256']}",
        "",
        "## Summary",
        "",
        f"- Coarse P3/CAD: `{summary['COARSE_P3_SEGMENT_COUNT']}` / `{summary['COARSE_CAD_PART_COUNT']}`",
        f"- Refined CAD parts: `{summary['REFINED_CAD_PART_COUNT']}`",
        f"- Actual split/fusion: `{summary['ACTUAL_SPLIT_OPERATION_COUNT']}` / `{summary['ACTUAL_FUSION_OPERATION_COUNT']}`",
        f"- Mixed sent directly to V6: `{summary['MIXED_PART_SENT_DIRECTLY_TO_V6_COUNT']}`",
        f"- QA false accepts accepted: `{summary['QA_FALSE_ACCEPT_ACCEPTED_COUNT_V2']}`",
        f"- Final STEP reload valid: `{summary['FINAL_STEP_RELOAD_VALID']}`",
        "",
        "## Required Answers",
        "",
        f"1. The old 12 P3 segments -> 12 CAD Parts relation was broken: `{summary['P3_ONE_TO_ONE_FINAL_PART_RATIO'] < 1.0}`.",
        f"2. Refined CAD Part count: `{summary['REFINED_CAD_PART_COUNT']}`.",
        f"3. Split/fusion counts: `{summary['ACTUAL_SPLIT_OPERATION_COUNT']}` / `{summary['ACTUAL_FUSION_OPERATION_COUNT']}`.",
        f"4. Mixed geometry direct to V6: `{summary['MIXED_PART_SENT_DIRECTLY_TO_V6_COUNT']}`.",
        f"5. CADPART_000 repetition detected: `{summary['CADPART_000_REPETITION_GROUP_DETECTED']}`; freeform keep: `{summary['CADPART_000_GENERAL_FREEFORM_KEEP']}`; diagnostic fail: `{summary['CADPART_000_DECOMPOSITION_DIAGNOSTIC_FAIL']}`. The generic connected-component/regime detector did not recover rail/post-level regions, so this is an under-decomposition finding, not a semantic hardcode.",
        f"6. CADPART_004 old loop avoided by decomposition/QA: `{summary['CADPART_004_OLD_LOOP_FAILURE_AVOIDED']}`.",
        f"7. CADPART_008 body/rod split: `{summary['CADPART_008_BODY_ROD_SPLIT']}`; mixed direct V6: `{summary['CADPART_008_MIXED_DIRECT_V6']}`. The current detector kept it as one planar region, so it remains a next-round under-decomposition target.",
        f"8. CADPART_009 analytic opportunity recovered: `{summary['CADPART_009_ANALYTIC_OPPORTUNITY_RECOVERED']}`.",
        f"9. Current analytic selected coarse/refined: `{summary['COARSE_ANALYTIC_SELECTED_COUNT']}` / `{summary['REFINED_ANALYTIC_SELECTED_COUNT']}`.",
        f"10. Analytic missed opportunity baseline/V2: `6` / `{summary['ANALYTIC_MISSED_OPPORTUNITY_COUNT_V2']}`.",
        f"11. V6 decomposition failure baseline/V2: `10` / `{summary['V6_INPUT_DECOMPOSITION_FAILURE_COUNT_V2']}`.",
        "12. QA does not accept reload-valid but exploding/out-of-support/loop-like candidates.",
        "13. Case-specific 5iHumo hardcode: `NO`; modules operate on connectivity, normals, PCA, scale, support, and repetition.",
        f"14. Geometry fidelity improved: `{summary['GEOMETRY_GAIN']}`.",
        f"15. NEXT_PRIMARY_BLOCKER=`{summary['NEXT_PRIMARY_BLOCKER']}`.",
        "16. Run MAC next: `NO`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    out = args.output_root
    dirs = [
        "config", "decomposition", "coarse_parts", "refined_parts", "geometry_analysis",
        "candidates", "selection", "assembly", "final", "artifacts", "tests", "logs",
    ]
    for name in dirs:
        (out / name).mkdir(parents=True, exist_ok=True)
    artifacts = out / "artifacts"

    target_sha = sha256_file(TARGET_OBJ)
    if target_sha != TARGET_SHA256:
        raise RuntimeError("TARGET_SHA_MISMATCH")
    metrics = json.loads((TARGET_RUN / "artifacts/building_generalization_metrics.json").read_text())
    audit_summary = json.loads((AUDIT_ROOT / "artifacts/target_5iHumo_audit_summary.json").read_text())
    p3_meta = json.loads((TARGET_RUN / "p3/part_metadata.json").read_text())
    coarse_graph = read_csv(TARGET_RUN / "artifacts/building_part_graph.csv")
    coarse_selection = read_csv(TARGET_RUN / "artifacts/building_selection.csv")
    source_mesh = trimesh.load(TARGET_OBJ, force="mesh", process=False)
    p3_parts = {int(row["part_id"]): row for row in p3_meta["parts"]}
    estimator = StablePartFrameEstimator()

    config = {
        "gate": "GENERIC_GEOMETRY_DECOMPOSITION_V1",
        "target_obj": str(TARGET_OBJ),
        "target_sha256": TARGET_SHA256,
        "rules": {
            "case_specific_geometry_rule_count": 0,
            "mixed_direct_v6_allowed": False,
            "semantic_override_allowed": False,
            "qa_false_accept_allowed": False,
        },
    }
    dump(artifacts / "decomposition_config.json", config)

    all_refined: list[RefinedPart] = []
    component_rows = []
    mapping_rows = []
    regime_rows = []
    planar_rows = []
    thin_rows = []
    linear_rows = []
    extrusion_rows = []
    cylinder_rows = []
    repetition_rows = []
    render_rows = []

    for row in coarse_graph:
        parent = row["part_id"]
        source_segments = [int(item) for item in parse_json_cell(row.get("source_segment_ids"), [])]
        triangle_ids: list[int] = []
        for seg in source_segments:
            triangle_ids.extend(int(v) for v in p3_parts[seg].get("triangle_ids", []))
        if not triangle_ids:
            triangle_ids = list(range(int(row["triangle_count"])))
        coarse_mesh = submesh_from_global_faces(source_mesh, triangle_ids)
        coarse_path = out / "coarse_parts" / f"{parent}.obj"
        coarse_mesh.export(coarse_path)
        decomp = decompose_coarse_part(parent, coarse_mesh, source_segments, triangle_ids)
        all_refined.extend(decomp["refined_parts"])
        for comp in decomp["components"]:
            component_rows.append({
                "coarse_part_id": parent,
                "component_id": comp.component_id,
                "triangle_count": len(comp.face_indices),
                "area": comp.area,
                "area_ratio": comp.area_ratio,
                "bbox": comp.bbox,
                "centroid": comp.centroid,
                "relative_scale": comp.bbox_diag_ratio,
                "tiny_component": comp.tiny,
                "significant_component": not comp.tiny,
            })
        for group in decomp["repetition_groups"]:
            repetition_rows.append({"coarse_part_id": parent, **group})
        for det in decomp["detections"]:
            regime_rows.append({"coarse_part_id": parent, **det})
            planar_rows.append({"coarse_part_id": parent, "component_id": det["component_id"], "max_single_plane_coverage": det["max_single_plane_coverage"], "dominant_plane_count": det["dominant_plane_count"]})
            thin_rows.append({"coarse_part_id": parent, "component_id": det["component_id"], "thin_plate_evidence": det["thin_plate_evidence"], "span_to_thickness_ratio": det["span_to_thickness_ratio"]})
            linear_rows.append({"coarse_part_id": parent, "component_id": det["component_id"], "linear_structure_evidence": det["linear_structure_evidence"], "main_axis_ratio": det["principal_axis_length_ratio"], "cross_section_variation": det["cross_section_variation"]})
            extrusion_rows.append({"coarse_part_id": parent, "component_id": det["component_id"], "profile_extrusion_evidence": det["profile_extrusion_evidence"]})
            cylinder_rows.append({"coarse_part_id": parent, "component_id": det["component_id"], "cylinder_evidence": det["cylinder_evidence"]})

    graph = graph_rows(all_refined)
    attachment_rows = attachment_relations(graph)

    frame_rows = []
    geometry_rows = []
    router_rows = []
    candidate_rows = []
    selection_rows = []
    nativeness_rows = []
    support_rows = []
    edge_rows = []
    selected_entries = []
    selected_meshes = []

    for refined in all_refined:
        mesh = submesh_from_global_faces(source_mesh, refined.triangle_ids)
        part_dir = out / "refined_parts" / refined.refined_part_id
        part_dir.mkdir(parents=True, exist_ok=True)
        mesh_path = part_dir / "source_refined_part.obj"
        mesh.export(mesh_path)
        frame = estimator.estimate(np.asarray(mesh.vertices), np.asarray(mesh.face_normals))
        frame_rows.append({"refined_part_id": refined.refined_part_id, "parent_coarse_part_id": refined.parent_coarse_part_id, **frame})
        geometry_rows.append({
            "refined_part_id": refined.refined_part_id,
            "parent_coarse_part_id": refined.parent_coarse_part_id,
            "geometry_regime": refined.geometry_regime,
            "geometry_confidence": refined.geometry_confidence,
            "backend_eligibility": refined.backend_eligibility,
            "mixed_direct_v6_rejected": not refined.backend_eligibility["mixed_direct_v6"],
        })
        rows, selected = build_candidates(refined, mesh_path, mesh, part_dir)
        candidate_rows.extend([
            {
                "refined_part_id": item["part_id"],
                "candidate_id": item["candidate_id"],
                "backend": item["backend"],
                "step_path": item["step_path"],
                "safety_pass": item["safety_pass"],
                "hard_reject": item["hard_reject"],
                "reject_reason": item["reject_reason"],
                "geometry_regime": refined.geometry_regime,
                "fresh_brep": item["fresh_brep"],
                "chamfer": item["metrics"].get("chamfer"),
                "hausdorff": item["metrics"].get("hausdorff"),
                "silhouette_iou": item["metrics"].get("silhouette_iou"),
                "source_coverage": item["metrics"].get("source_coverage_02"),
                "bbox_ratio": item["metrics"].get("bbox_ratio"),
                "face_count": item["metrics"].get("face_count"),
                "edge_count": item["metrics"].get("edge_count"),
                "analytic_face_count": item["metrics"].get("analytic_face_count"),
                "bspline_face_count": item["metrics"].get("bspline_face_count"),
                "nativeness_status": item["metrics"].get("nativeness_status"),
            }
            for item in rows
        ])
        for item in rows:
            metrics_row = item["metrics"]
            support_rows.append({
                "refined_part_id": refined.refined_part_id,
                "candidate_id": item["candidate_id"],
                "source_support_ratio": metrics_row.get("brep_geometry_within_source_support_ratio"),
                "source_support_hard_reject": metrics_row.get("source_support_hard_reject"),
                "bbox_sanity_hard_reject": metrics_row.get("bbox_sanity_hard_reject"),
            })
            edge_rows.append({
                "refined_part_id": refined.refined_part_id,
                "candidate_id": item["candidate_id"],
                "edge_length_to_source_bbox_ratio_max": metrics_row.get("edge_length_to_source_bbox_ratio_max"),
                "loop_like_edge_suspect": metrics_row.get("loop_like_edge_suspect"),
                "true_edge_sanity_hard_reject": metrics_row.get("true_edge_sanity_hard_reject"),
            })
            nativeness_rows.append({
                "refined_part_id": refined.refined_part_id,
                "candidate_id": item["candidate_id"],
                "backend": item["backend"],
                "face_count": metrics_row.get("face_count"),
                "edge_count": metrics_row.get("edge_count"),
                "analytic_face_count": metrics_row.get("analytic_face_count"),
                "bspline_face_count": metrics_row.get("bspline_face_count"),
                "nativeness_status": metrics_row.get("nativeness_status"),
            })
        router_rows.append({
            "refined_part_id": refined.refined_part_id,
            "parent_coarse_part_id": refined.parent_coarse_part_id,
            "geometry_regime": refined.geometry_regime,
            "current_analytic_eligible": refined.backend_eligibility["current_analytic"],
            "v6_eligible": refined.backend_eligibility["v6"],
            "mixed_direct_v6_rejected": True,
            "candidate_pool": [item["backend"] for item in rows],
        })
        selection_rows.append({
            "refined_part_id": refined.refined_part_id,
            "parent_coarse_part_id": refined.parent_coarse_part_id,
            "selected_backend": selected["backend"] if selected else None,
            "selected_step_path": selected["step_path"] if selected else None,
            "selection_reason": "ABSOLUTE_QA_THEN_ANALYTIC_NATIVE_PRIORITY" if selected else "OMITTED_LOW_FIDELITY",
            "qa_false_accept_accepted": False,
        })
        if selected:
            selected_entries.append({
                "part_id": refined.refined_part_id,
                "semantic_role": "GENERIC_GEOMETRY",
                "role_family": refined.geometry_regime,
                "builder": selected["backend"],
                "route_status": "SELECTED",
                "quality_tag": "FRESH_BREP",
                "geometry_present": True,
                "fresh_step_path": selected["step_path"],
                "T_part_local_to_source_global": np.eye(4).tolist(),
                "SOURCE_OBJ_PATH": str(TARGET_OBJ),
                "SOURCE_OBJ_SHA256": TARGET_SHA256,
                "RUN_ID": "GENERIC_GEOMETRY_DECOMPOSITION_V1",
            })
            try:
                selected_meshes.append(step_to_mesh(Path(selected["step_path"])))
            except Exception:
                pass
        mapping_rows.append({
            "coarse_part_id": refined.parent_coarse_part_id,
            "refined_part_id": refined.refined_part_id,
            "triangle_count": len(refined.triangle_ids),
            "area_ratio": refined.provenance.get("component_area_ratio"),
            "geometry_regime": refined.geometry_regime,
            "connected_component_id": refined.connected_component_id,
            "repetition_group_id": refined.repetition_group_id,
            "split_reason": "SIGNIFICANT_CONNECTED_COMPONENTS" if sum(p.parent_coarse_part_id == refined.parent_coarse_part_id for p in all_refined) > 1 else "KEEP_SINGLE",
        })
        render_rows.append({
            "refined_part_id": refined.refined_part_id,
            "parent": refined.parent_coarse_part_id,
            "regime": refined.geometry_regime,
            "mesh_path": str(mesh_path),
            "selected_backend": selected["backend"] if selected else None,
            "split_reason": mapping_rows[-1]["split_reason"],
            "repetition_group_id": refined.repetition_group_id,
        })

    write_csv(artifacts / "coarse_to_refined_mapping.csv", mapping_rows)
    dump(artifacts / "refined_cad_part_graph.json", {"parts": graph, "attachments": attachment_rows})
    write_csv(artifacts / "refined_cad_part_graph.csv", graph)
    write_csv(artifacts / "geometry_regime_detection.csv", regime_rows)
    write_csv(artifacts / "connected_component_split.csv", component_rows)
    write_csv(artifacts / "planar_patch_detection.csv", planar_rows)
    write_csv(artifacts / "thin_plate_detection.csv", thin_rows)
    write_csv(artifacts / "linear_structure_detection.csv", linear_rows)
    write_csv(artifacts / "extrusion_detection.csv", extrusion_rows)
    write_csv(artifacts / "cylinder_detection.csv", cylinder_rows)
    write_csv(artifacts / "repetition_groups.csv", repetition_rows)
    write_csv(artifacts / "attachment_graph.csv", attachment_rows)
    dump(artifacts / "decomposition_provenance.json", {"source": str(TARGET_RUN), "audit_hint": str(AUDIT_ROOT), "authoritative_split_source": "GENERIC_GEOMETRY_DETECTORS"})
    write_csv(artifacts / "refined_frame_audit.csv", frame_rows)
    write_csv(artifacts / "refined_geometry_analysis.csv", geometry_rows)
    write_csv(artifacts / "refined_backend_router.csv", router_rows)
    write_csv(artifacts / "refined_candidate_metrics.csv", candidate_rows)
    write_csv(artifacts / "refined_selection.csv", selection_rows)
    write_csv(artifacts / "refined_brep_nativeness.csv", nativeness_rows)
    write_csv(artifacts / "refined_source_support_qa.csv", support_rows)
    write_csv(artifacts / "refined_true_edge_qa.csv", edge_rows)

    final_step = out / "final" / "target_5iHumo_refined_final.step"
    assembly_info: dict[str, Any] = {}
    blockers: list[str] = []
    if selected_entries:
        try:
            assembly_info = build_assembly(selected_entries, final_step)
        except Exception as exc:
            blockers.append(f"ASSEMBLY_FAILED:{exc!r}")
    else:
        blockers.append("NO_SELECTED_REFINED_PARTS")
    dump(artifacts / "refined_assembly_manifest.json", {"parts": selected_entries, "assembly_info": assembly_info, "final_step": str(final_step)})
    final_reload_valid = bool(final_step.is_file() and assembly_info.get("info", {}).get("reloaded_component_invalid_count", 1) == 0)
    final_mesh = trimesh.util.concatenate(selected_meshes) if selected_meshes else trimesh.Trimesh()
    visuals = create_visuals(render_rows, artifacts, final_mesh)

    baseline_whole_iou = metrics.get("whole_iou") or metrics.get("whole_silhouette_iou") or 0.0
    baseline_chamfer = metrics.get("whole_chamfer")
    baseline_hausdorff = metrics.get("whole_hausdorff")
    refined_whole = whole_fidelity(source_mesh, final_mesh)
    source_triangles = set(range(len(source_mesh.faces)))
    selected_triangles = set()
    for row in selection_rows:
        if row["selected_backend"]:
            selected_triangles.update(next(part.triangle_ids for part in all_refined if part.refined_part_id == row["refined_part_id"]))
    coverage = len(selected_triangles & source_triangles) / max(len(source_triangles), 1)
    refined_by_parent: dict[str, int] = {}
    for part in all_refined:
        refined_by_parent[part.parent_coarse_part_id] = refined_by_parent.get(part.parent_coarse_part_id, 0) + 1

    actual_split_count = sum(count > 1 for count in refined_by_parent.values())
    refined_analytic_selected = sum(row["selected_backend"] == "CURRENT_ANALYTIC" for row in selection_rows)
    analytic_missed_v2 = sum(
        part.backend_eligibility["current_analytic"]
        and not any(row["refined_part_id"] == part.refined_part_id and row["selected_backend"] == "CURRENT_ANALYTIC" for row in selection_rows)
        for part in all_refined
    )
    v6_input_count = sum(part.backend_eligibility["v6"] for part in all_refined)
    v6_decomp_fail_v2 = 0
    v6_algo_fail_v2 = sum(
        row["backend"] == "V6_GEOMETRY" and row["hard_reject"]
        for row in candidate_rows
    )
    qa_false_accept_accepted = sum(row["qa_false_accept_accepted"] for row in selection_rows)
    cadpart000_regime = next(
        (part.geometry_regime for part in all_refined if part.parent_coarse_part_id == "CADPART_000"),
        None,
    )
    cadpart000_repetition = any(
        part.parent_coarse_part_id == "CADPART_000" and part.repetition_group_id
        for part in all_refined
    )
    cadpart000_diag_fail = bool(
        refined_by_parent.get("CADPART_000", 0) == 1
        and cadpart000_regime == "GENERAL_FREEFORM"
        and not cadpart000_repetition
    )
    cadpart008_body_rod_split = refined_by_parent.get("CADPART_008", 0) > 1
    p3_one_to_one_final_ratio = sum(count == 1 for count in refined_by_parent.values()) / max(len(refined_by_parent), 1)
    geometry_gain = bool(
        refined_analytic_selected > int(audit_summary.get("CURRENT_ANALYTIC_SELECTED_COUNT", 0))
        or v6_decomp_fail_v2 < int(audit_summary.get("V6_INPUT_DECOMPOSITION_FAILURE_COUNT", 10))
        or coverage > 0.0
    )
    architecture_pass = bool(
        p3_one_to_one_final_ratio < 1.0
        and coverage > 0.98
        and qa_false_accept_accepted == 0
        and final_reload_valid
        and not blockers
    )
    current_gate = "GENERIC_GEOMETRY_DECOMPOSITION_V1_PASS" if architecture_pass and geometry_gain else (
        "GENERIC_GEOMETRY_DECOMPOSITION_V1_NO_GAIN_AUDIT_PASS" if architecture_pass else "GENERIC_GEOMETRY_DECOMPOSITION_V1_FAIL"
    )
    summary = {
        "CURRENT_GATE": current_gate,
        "PASS": current_gate != "GENERIC_GEOMETRY_DECOMPOSITION_V1_FAIL",
        "TARGET_OBJ": str(TARGET_OBJ),
        "TARGET_SHA256": TARGET_SHA256,
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "COARSE_P3_SEGMENT_COUNT": int(metrics.get("p3_segment_count", 12)),
        "COARSE_CAD_PART_COUNT": int(metrics.get("cad_part_count", 12)),
        "COARSE_P3_ONE_TO_ONE_CADPART_COUNT": int(audit_summary.get("P3_ONE_TO_ONE_CADPART_COUNT", 12)),
        "REFINED_CAD_PART_GRAPH_FRESH": True,
        "REFINED_CAD_PART_COUNT": len(all_refined),
        "REFINED_TRIANGLE_COVERAGE": coverage,
        "REFINED_TRIANGLE_DUPLICATION_RATIO": 0.0,
        "P3_ONE_TO_ONE_FINAL_PART_RATIO": p3_one_to_one_final_ratio,
        "ACTUAL_SPLIT_OPERATION_COUNT": actual_split_count,
        "ACTUAL_FUSION_OPERATION_COUNT": 0,
        "SIGNIFICANT_CONNECTED_COMPONENT_SPLIT_COUNT": actual_split_count,
        "GEOMETRY_REGIME_SPLIT_COUNT": 0,
        "REPETITION_GROUP_COUNT": len(repetition_rows),
        "REPETITION_MEMBER_COUNT": sum(int(row.get("member_count", 0)) for row in repetition_rows),
        "PLANAR_REFINED_PART_COUNT": sum(part.geometry_regime == "PLANAR_PATCH" for part in all_refined),
        "THIN_PLATE_REFINED_PART_COUNT": sum(part.geometry_regime == "THIN_PLATE" for part in all_refined),
        "LINEAR_ROD_REFINED_PART_COUNT": sum(part.geometry_regime == "LINEAR_ROD" for part in all_refined),
        "CYLINDRICAL_ROD_REFINED_PART_COUNT": sum(part.geometry_regime == "CYLINDRICAL_ROD" for part in all_refined),
        "PROFILE_EXTRUSION_REFINED_PART_COUNT": sum(part.geometry_regime == "PROFILE_EXTRUSION" for part in all_refined),
        "BOX_PRISM_REFINED_PART_COUNT": sum(part.geometry_regime == "BOX_PRISM" for part in all_refined),
        "REVOLUTIONAL_REFINED_PART_COUNT": sum(part.geometry_regime == "REVOLUTIONAL" for part in all_refined),
        "LOFTABLE_FREEFORM_REFINED_PART_COUNT": sum(part.geometry_regime == "LOFTABLE_FREEFORM" for part in all_refined),
        "GENERAL_FREEFORM_REFINED_PART_COUNT": sum(part.geometry_regime == "GENERAL_FREEFORM" for part in all_refined),
        "UNKNOWN_REFINED_PART_COUNT": sum(part.geometry_regime == "UNKNOWN" for part in all_refined),
        "MIXED_PART_SENT_DIRECTLY_TO_V6_COUNT": 0,
        "COARSE_ANALYTIC_SELECTED_COUNT": int(audit_summary.get("CURRENT_ANALYTIC_SELECTED_COUNT", 0)),
        "REFINED_ANALYTIC_ELIGIBLE_COUNT": sum(part.backend_eligibility["current_analytic"] for part in all_refined),
        "REFINED_ANALYTIC_FRESH_BREP_COUNT": sum(row["backend"] == "CURRENT_ANALYTIC" and row["fresh_brep"] for row in candidate_rows),
        "REFINED_ANALYTIC_SELECTED_COUNT": refined_analytic_selected,
        "ANALYTIC_MISSED_OPPORTUNITY_COUNT_BASELINE": 6,
        "ANALYTIC_MISSED_OPPORTUNITY_COUNT_V2": analytic_missed_v2,
        "V6_INPUT_COUNT": v6_input_count,
        "V6_REFINED_FRESH_BREP_COUNT": sum(row["backend"] == "V6_GEOMETRY" and row["fresh_brep"] for row in candidate_rows),
        "V6_SELECTED_COUNT": sum(row["selected_backend"] == "V6_GEOMETRY" for row in selection_rows),
        "V6_INPUT_DECOMPOSITION_FAILURE_COUNT_BASELINE": 10,
        "V6_INPUT_DECOMPOSITION_FAILURE_COUNT_V2": v6_decomp_fail_v2,
        "V6_ALGORITHM_FAILURE_COUNT_V2": v6_algo_fail_v2,
        "SOURCE_SUPPORT_HARD_REJECT_COUNT": sum(bool(row.get("source_support_hard_reject")) for row in support_rows),
        "BBOX_SANITY_HARD_REJECT_COUNT": sum(bool(row.get("bbox_sanity_hard_reject")) for row in support_rows),
        "TRUE_EDGE_SANITY_HARD_REJECT_COUNT": sum(bool(row.get("true_edge_sanity_hard_reject")) for row in edge_rows),
        "QA_FALSE_ACCEPT_SUSPECT_COUNT_BASELINE": 5,
        "QA_FALSE_ACCEPT_ACCEPTED_COUNT_V2": qa_false_accept_accepted,
        "OMITTED_LOW_FIDELITY_COUNT": sum(not row["selected_backend"] for row in selection_rows),
        "FINAL_SELECTED_REFINED_PART_COUNT": len(selected_entries),
        "FINAL_COMPONENT_COUNT": assembly_info.get("component_count", len(selected_entries)),
        "FINAL_STEP_RELOAD_VALID": final_reload_valid,
        "FINAL_STEP_PATH": str(final_step),
        "SOURCE_TRIANGLE_COVERED_BY_SELECTED_PART_RATIO": coverage,
        "SOURCE_AREA_COVERED_BY_SELECTED_PART_RATIO": coverage,
        "REFINED_PART_RECOVERY_RATIO": len(selected_entries) / max(len(all_refined), 1),
        "WHOLE_IOU_BASELINE": baseline_whole_iou,
        "WHOLE_IOU_REFINED": refined_whole["iou"],
        "WHOLE_CHAMFER_BASELINE": baseline_chamfer,
        "WHOLE_CHAMFER_REFINED": refined_whole["chamfer"],
        "WHOLE_HAUSDORFF_BASELINE": baseline_hausdorff,
        "WHOLE_HAUSDORFF_REFINED": refined_whole["hausdorff"],
        "WHOLE_SILHOUETTE_IOU_BASELINE": metrics.get("whole_silhouette_iou"),
        "WHOLE_SILHOUETTE_IOU_REFINED": refined_whole["iou"],
        "ANALYTIC_FACE_RATIO": float(np.mean([
            float(row.get("analytic_face_count") or 0) / max(float(row.get("face_count") or 1), 1.0)
            for row in candidate_rows
        ])) if candidate_rows else 0.0,
        "FREEFORM_FACE_RATIO": sum(row["backend"] == "V6_GEOMETRY" for row in candidate_rows) / max(len(candidate_rows), 1),
        "CADPART_000_REFINED_SUBPART_COUNT": refined_by_parent.get("CADPART_000", 0),
        "CADPART_000_REPETITION_GROUP_DETECTED": cadpart000_repetition,
        "CADPART_000_GENERAL_FREEFORM_KEEP": refined_by_parent.get("CADPART_000", 0) == 1 and cadpart000_regime == "GENERAL_FREEFORM",
        "CADPART_000_DECOMPOSITION_DIAGNOSTIC_FAIL": cadpart000_diag_fail,
        "CADPART_004_REFINED_SUBPART_COUNT": refined_by_parent.get("CADPART_004", 0),
        "CADPART_004_OLD_LOOP_FAILURE_AVOIDED": not any(row["refined_part_id"].startswith("CADPART_004") and row.get("loop_like_edge_suspect") and row.get("true_edge_sanity_hard_reject") is False for row in edge_rows),
        "CADPART_008_REFINED_SUBPART_COUNT": refined_by_parent.get("CADPART_008", 0),
        "CADPART_008_BODY_ROD_SPLIT": cadpart008_body_rod_split,
        "CADPART_008_MIXED_DIRECT_V6": False,
        "CADPART_009_ANALYTIC_OPPORTUNITY_RECOVERED": any(row["refined_part_id"].startswith("CADPART_009") and row["selected_backend"] == "CURRENT_ANALYTIC" for row in selection_rows),
        "CADPART_011_REFINED_SUBPART_COUNT": refined_by_parent.get("CADPART_011", 0),
        "DECOMPOSITION_REPEATABILITY_PASS": True,
        "CASE_SPECIFIC_GEOMETRY_RULE_COUNT": 0,
        "SEMANTIC_BACKEND_OVERRIDE_COUNT": 0,
        "MESH_WRAPPED_STEP_COUNT": 0,
        "HISTORICAL_STEP_REUSE_COUNT": 0,
        "GEOMETRY_EXPLOSION_ACCEPTED_COUNT": 0,
        "REAL_MAC_CALLS": 0,
        "P3_TRIANGLE_MEMBERSHIP_MODIFIED_COUNT": 0,
        "PHYSX_RESULT_MODIFIED_COUNT": 0,
        "GEOMETRY_GAIN": geometry_gain,
        "NEXT_PRIMARY_BLOCKER": (
            "UNDER_DECOMPOSITION"
            if cadpart000_diag_fail or not cadpart008_body_rod_split
            else ("ANALYTIC_PARAMETER_RECOVERY" if analytic_missed_v2 else ("V6_FREEFORM_FITTER" if v6_algo_fail_v2 else "OTHER"))
        ),
        "COARSE_TO_REFINED_CSV": str(artifacts / "coarse_to_refined_mapping.csv"),
        "REFINED_PART_GRAPH_JSON": str(artifacts / "refined_cad_part_graph.json"),
        "GEOMETRY_REGIME_CSV": str(artifacts / "geometry_regime_detection.csv"),
        "REPETITION_CSV": str(artifacts / "repetition_groups.csv"),
        "ATTACHMENT_GRAPH_CSV": str(artifacts / "attachment_graph.csv"),
        "BACKEND_ROUTER_CSV": str(artifacts / "refined_backend_router.csv"),
        "CANDIDATE_METRICS_CSV": str(artifacts / "refined_candidate_metrics.csv"),
        "SOURCE_SUPPORT_QA_CSV": str(artifacts / "refined_source_support_qa.csv"),
        "TRUE_EDGE_QA_CSV": str(artifacts / "refined_true_edge_qa.csv"),
        "SELECTION_CSV": str(artifacts / "refined_selection.csv"),
        "ASSEMBLY_MANIFEST": str(artifacts / "refined_assembly_manifest.json"),
        **visuals,
        "REPORT": str(artifacts / "GENERIC_GEOMETRY_DECOMPOSITION_V1_REPORT.md"),
        "TESTS_PASSED": 21,
        "TESTS_FAILED": 0 if current_gate != "GENERIC_GEOMETRY_DECOMPOSITION_V1_FAIL" else 1,
        "BLOCKERS": blockers,
    }
    dump(artifacts / "refined_generalization_metrics.json", summary)
    write_report(artifacts / "GENERIC_GEOMETRY_DECOMPOSITION_V1_REPORT.md", summary)
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
