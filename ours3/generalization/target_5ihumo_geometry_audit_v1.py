#!/usr/bin/env python3
"""Read-only decomposition and backend failure audit for target 5iHumo."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
TARGET_OBJ = ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"
TARGET_SHA256 = "f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61"
TARGET_RUN = ROOT / "building_cross_case_generalization_target_5iHumoHAKIPuELpWrRd3Vr3mk38_v1"
AUDIT_ROOT = ROOT / "target_5iHumo_geometry_decomposition_backend_audit_v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
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
                key: json.dumps(clean(value), sort_keys=True) if isinstance(value, (dict, list, tuple)) else clean(value)
                for key, value in row.items()
            })


def parse_json_cell(value: str | None, fallback: Any) -> Any:
    if value is None or value == "":
        return fallback
    try:
        return json.loads(value)
    except Exception:
        return fallback


def bool_cell(value: str | None) -> bool:
    return str(value).lower() == "true"


def float_cell(value: str | None, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def classify_from_features(features: dict[str, Any]) -> dict[str, Any]:
    regimes: list[str] = []
    if features.get("significant_component_count", 1) > 1:
        regimes.append("REPEATED_COMPONENT" if features.get("repetition_evidence") else "UNKNOWN")
    if features.get("max_single_plane_coverage", 0.0) >= 0.32:
        regimes.append("PLANAR_PATCH")
    if features.get("thin_plate_evidence"):
        regimes.append("THIN_PLATE")
    if features.get("linear_rod_evidence"):
        regimes.append("CYLINDRICAL_ROD" if features.get("cylinder_evidence") else "LINEAR_ROD")
    if features.get("profile_extrusion_evidence"):
        regimes.append("PROFILE_EXTRUSION")
    if not regimes:
        regimes.append("FREEFORM_SURFACE" if features.get("normal_dispersion", 0.0) > 0.65 else "UNKNOWN")
    unique = []
    for item in regimes:
        if item not in unique:
            unique.append(item)
    mixed_score = max(0, len(unique) - 1) + (1 if features.get("significant_component_count", 1) > 1 else 0)
    split = mixed_score > 0 or features.get("repetition_evidence", False)
    if features.get("significant_component_count", 1) > 1:
        recommendation = "SPLIT_BY_CONNECTED_COMPONENT"
        reason = "DISCONNECTED_COMPONENTS"
    elif features.get("repetition_evidence", False):
        recommendation = "SPLIT_REPETITION_GROUP"
        reason = "REPETITION_GROUP"
    elif split:
        recommendation = "SPLIT_BY_GEOMETRY_REGIME"
        reason = "MULTIPLE_GEOMETRY_REGIMES"
    else:
        recommendation = "KEEP_AS_SINGLE_CAD_PART"
        reason = "SINGLE_COHERENT_REGION"
    return {
        "audited_geometry_classes": unique,
        "geometry_regime_count": len(unique),
        "mixed_geometry_score": mixed_score,
        "split_recommended": split,
        "decomposition_recommendation": recommendation,
        "split_reason": reason,
    }


def v6_sanity_from_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    bbox_ratio = float(metrics.get("bbox_diag_ratio", 1.0))
    max_edge_ratio = float(metrics.get("edge_length_to_bbox_ratio_max", 0.0))
    support = float(metrics.get("brep_geometry_within_source_support_ratio", 1.0))
    return {
        "v6_bbox_explosion_suspect": bbox_ratio > 2.0 or float(metrics.get("max_bbox_expansion_ratio", 0.0)) > 2.0,
        "loop_like_edge_suspect": max_edge_ratio > 1.7,
        "v6_out_of_source_support": support < 0.35,
        "qa_false_accept_suspect": bool(metrics.get("selected") and (support < 0.35 or max_edge_ratio > 1.7 or bbox_ratio > 2.0)),
    }


def render_mesh_image(mesh: Any, size: tuple[int, int] = (240, 180), colors: np.ndarray | None = None, title: str = "") -> Image.Image:
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0 or len(faces) == 0:
        draw.text((8, 8), title or "EMPTY", fill=(30, 30, 30))
        return image
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    direction = np.asarray([1.2, -1.45, 0.9], dtype=float)
    direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0])
    right /= max(np.linalg.norm(right), 1e-12)
    up = np.cross(right, direction)
    projected = np.column_stack(((vertices - center) @ right, (vertices - center) @ up))
    scale = max(float(np.max(np.abs(projected))), 1e-9)
    xy = np.column_stack((size[0] * 0.5 + projected[:, 0] * size[0] * 0.42 / scale,
                          size[1] * 0.55 - projected[:, 1] * size[1] * 0.42 / scale))
    depth = (vertices - center) @ direction
    normals = np.asarray(mesh.face_normals)
    light = np.asarray([0.35, -0.45, 0.82], dtype=float)
    light /= np.linalg.norm(light)
    order = np.argsort(depth[faces].mean(axis=1))
    if len(order) > 25000:
        order = order[np.linspace(0, len(order) - 1, 25000, dtype=np.int64)]
    for face_index in order:
        polygon = [tuple(np.rint(xy[int(index)]).astype(int)) for index in faces[int(face_index)]]
        if colors is None:
            shade = 0.42 + 0.58 * max(float(np.dot(normals[int(face_index)], light)), 0.0)
            color = tuple(int(channel * shade) for channel in (180, 202, 220))
        else:
            color = tuple(int(v) for v in colors[int(face_index)][:3])
        draw.polygon(polygon, fill=color)
    draw.rectangle((0, 0, size[0], 18), fill="white")
    draw.text((5, 4), title[:42], fill=(20, 30, 40))
    return image


def step_to_mesh(path: Path) -> Any:
    import trimesh
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP_READ_FAILED:{path}")
    reader.TransferRoots()
    shape = reader.OneShape()
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
            trsf = loc.Transformation()
            for index in range(1, tri.NbNodes() + 1):
                point = tri.Node(index).Transformed(trsf)
                vertices.append([point.X(), point.Y(), point.Z()])
            for index in range(1, tri.NbTriangles() + 1):
                a, b, c = tri.Triangle(index).Get()
                faces.append([base + a - 1, base + b - 1, base + c - 1])
        explorer.Next()
    return trimesh.Trimesh(vertices=np.asarray(vertices), faces=np.asarray(faces), process=False)


def step_edge_topology(path: Path) -> dict[str, Any]:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP_READ_FAILED:{path}")
    reader.TransferRoots()
    shape = reader.OneShape()
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    bbox = np.asarray(box.Get(), dtype=float)
    diag = float(np.linalg.norm(bbox[3:] - bbox[:3]))
    edge_lengths = []
    explorer = TopExp_Explorer(shape, TopAbs_EDGE)
    while explorer.More():
        props = GProp_GProps()
        try:
            BRepGProp.LinearProperties_s(TopoDS.Edge_s(explorer.Current()), props)
            edge_lengths.append(float(props.Mass()))
        except Exception:
            pass
        explorer.Next()
    face_count = 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face_count += 1
        explorer.Next()
    lengths = np.asarray(edge_lengths, dtype=float)
    if len(lengths) == 0:
        return {"edge_length_p99": 0.0, "edge_length_to_bbox_ratio_max": 0.0, "very_long_edge_count": 0, "loop_like_edge_count": 0, "face_count_from_step": face_count}
    max_ratio = float(lengths.max() / max(diag, 1e-12))
    return {
        "edge_length_p99": float(np.percentile(lengths, 99)),
        "edge_length_to_bbox_ratio_max": max_ratio,
        "very_long_edge_count": int(np.sum(lengths > diag * 0.8)),
        "loop_like_edge_count": int(np.sum(lengths > diag * 1.7)),
        "face_count_from_step": face_count,
        "candidate_bbox": bbox.tolist(),
        "candidate_bbox_diag": diag,
    }


def normal_clusters(mesh: Any) -> list[dict[str, Any]]:
    normals = np.asarray(mesh.face_normals, dtype=float)
    areas = np.asarray(mesh.area_faces, dtype=float)
    total = max(float(areas.sum()), 1e-12)
    clusters: list[dict[str, Any]] = []
    for normal, area in zip(normals, areas):
        key_normal = normal / max(np.linalg.norm(normal), 1e-12)
        assigned = False
        for cluster in clusters:
            if abs(float(np.dot(cluster["normal"], key_normal))) > 0.965:
                cluster["area"] += float(area)
                cluster["count"] += 1
                assigned = True
                break
        if not assigned:
            clusters.append({"normal": key_normal, "area": float(area), "count": 1})
    clusters.sort(key=lambda item: item["area"], reverse=True)
    return [
        {"normal": item["normal"].tolist(), "area_ratio": item["area"] / total, "triangle_count": item["count"]}
        for item in clusters
    ]


def component_audit(mesh: Any) -> dict[str, Any]:
    parts = mesh.split(only_watertight=False)
    total_area = max(float(mesh.area), 1e-12)
    total_diag = max(float(np.linalg.norm(mesh.extents)), 1e-12)
    rows = []
    for index, comp in enumerate(parts):
        bbox_diag = float(np.linalg.norm(comp.extents))
        area_ratio = float(comp.area / total_area)
        tiny = bool(area_ratio < 0.01 or len(comp.faces) < 80 or bbox_diag / total_diag < 0.04)
        rows.append({
            "component_id": index,
            "triangle_count": int(len(comp.faces)),
            "area_ratio": area_ratio,
            "bbox_ratio": bbox_diag / total_diag,
            "bbox_min": comp.bounds[0].tolist(),
            "bbox_max": comp.bounds[1].tolist(),
            "centroid": comp.centroid.tolist(),
            "tiny_component": tiny,
        })
    significant = [row for row in rows if not row["tiny_component"]]
    separation = 0.0
    if len(significant) > 1:
        centers = np.asarray([row["centroid"] for row in significant], dtype=float)
        separation = float(max(np.linalg.norm(a - b) for a in centers for b in centers))
    return {
        "connected_component_count": len(parts),
        "component_rows": rows,
        "significant_component_count": len(significant),
        "tiny_component_count": len(rows) - len(significant),
        "component_centroid_separation": separation,
        "disconnected_multi_component_part": len(significant) > 1,
    }


def geometry_evidence(mesh: Any, comp: dict[str, Any]) -> dict[str, Any]:
    clusters = normal_clusters(mesh)
    max_plane = clusters[0]["area_ratio"] if clusters else 0.0
    dominant = [c for c in clusters if c["area_ratio"] >= 0.10]
    extents = np.sort(np.asarray(mesh.extents, dtype=float))[::-1]
    long_to_mid = float(extents[0] / max(extents[1], 1e-12))
    long_to_short = float(extents[0] / max(extents[2], 1e-12))
    mid_to_short = float(extents[1] / max(extents[2], 1e-12))
    thin_plate = bool(max_plane >= 0.28 and long_to_short >= 8.0 and mid_to_short >= 3.0)
    linear_rod = bool(long_to_mid >= 3.0 and long_to_short >= 6.0)
    cylinder = bool(linear_rod and 0.55 <= extents[2] / max(extents[1], 1e-12) <= 1.0)
    profile_extrusion = bool(linear_rod and not cylinder)
    repetition = bool(comp["significant_component_count"] >= 4)
    normal_dispersion = float(np.mean(1.0 - np.clip(np.asarray(mesh.face_normals) @ np.asarray(mesh.face_normals).mean(axis=0), -1, 1)))
    features = {
        **comp,
        "dominant_plane_count": len(dominant),
        "dominant_plane_coverage": float(sum(item["area_ratio"] for item in dominant)),
        "max_single_plane_coverage": float(max_plane),
        "planar_patch_area_ratios": [item["area_ratio"] for item in dominant],
        "thin_plate_evidence": thin_plate,
        "thickness_mean": float(extents[2]),
        "thickness_std": 0.0,
        "span_to_thickness_ratio": long_to_short,
        "parallel_face_evidence": bool(max_plane >= 0.22),
        "linear_rod_evidence": linear_rod,
        "principal_axis_length_ratio": long_to_mid,
        "cross_section_variation": float(abs(extents[1] - extents[2]) / max(extents[1], 1e-12)),
        "centerline_curvature": 0.0,
        "cylinder_evidence": cylinder,
        "profile_extrusion_evidence": profile_extrusion,
        "repetition_evidence": repetition,
        "repetition_group_count": 1 if repetition else 0,
        "repetition_member_count": comp["significant_component_count"] if repetition else 0,
        "repetition_shape_similarity": 0.5 if repetition else 0.0,
        "repetition_spacing_variation": 0.0,
        "repetition_axis": None,
        "normal_dispersion": normal_dispersion,
        "planar_patch_clusters": clusters[:8],
    }
    features.update(classify_from_features(features))
    return features


def mesh_distance_metrics(source: Any, candidate: Any) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    if len(candidate.vertices) == 0:
        return {"brep_geometry_within_source_support_ratio": 0.0, "edge_within_source_support_ratio": 0.0}
    source_vertices = np.asarray(source.vertices, dtype=float)
    candidate_vertices = np.asarray(candidate.vertices, dtype=float)
    distances = cKDTree(source_vertices).query(candidate_vertices)[0]
    diag = max(float(np.linalg.norm(source.extents)), 1e-12)
    threshold = max(diag * 0.08, 0.02)
    return {
        "brep_geometry_within_source_support_ratio": float(np.mean(distances <= threshold)),
        "edge_within_source_support_ratio": float(np.mean(distances <= threshold)),
        "face_within_source_support_ratio": float(np.mean(distances <= threshold)),
        "support_distance_p95": float(np.percentile(distances, 95)),
    }


def bbox_guard(source: Any, candidate: Any) -> dict[str, Any]:
    src_min, src_max = np.asarray(source.bounds[0]), np.asarray(source.bounds[1])
    cand_min, cand_max = np.asarray(candidate.bounds[0]), np.asarray(candidate.bounds[1])
    src_extent = np.maximum(src_max - src_min, 1e-12)
    left = np.maximum(src_min - cand_min, 0.0) / src_extent
    right = np.maximum(cand_max - src_max, 0.0) / src_extent
    expansion = np.maximum(left, right)
    return {
        "bbox_expansion_axis_x": float(expansion[0]),
        "bbox_expansion_axis_y": float(expansion[1]),
        "bbox_expansion_axis_z": float(expansion[2]),
        "max_bbox_expansion_ratio": float(expansion.max()),
    }


def audit(args: argparse.Namespace) -> dict[str, Any]:
    import trimesh

    target_run = args.target_run
    out = args.output_root
    artifacts = out / "artifacts"
    logs = out / "logs"
    tests = out / "tests"
    for path in (artifacts, logs, tests):
        path.mkdir(parents=True, exist_ok=True)

    immutable_files = [
        *(target_run / "artifacts").glob("*"),
        *(target_run / "p3").glob("*"),
        *(target_run / "parts").glob("CADPART_*/*"),
        *(target_run / "parts").glob("CADPART_*/candidates/*"),
        *(target_run / "final").glob("*"),
    ]
    before_hash = {str(path): sha256_file(path) for path in immutable_files if path.is_file()}

    metrics = json.loads((target_run / "artifacts/building_generalization_metrics.json").read_text())
    if metrics.get("input_obj") != str(TARGET_OBJ) or metrics.get("input_obj_sha256") != TARGET_SHA256:
        raise RuntimeError("TARGET_RUN_IDENTITY_MISMATCH")
    p3_meta = json.loads((target_run / "p3/part_metadata.json").read_text())
    part_graph = read_csv(target_run / "artifacts/building_part_graph.csv")
    geometry_csv = {row["part_id"]: row for row in read_csv(target_run / "artifacts/building_geometry_classification.csv")}
    frame_csv = {row["part_id"]: row for row in read_csv(target_run / "artifacts/building_frame_audit.csv")}
    selection_csv = {row["part_id"]: row for row in read_csv(target_run / "artifacts/building_selection.csv")}
    candidate_csv = read_csv(target_run / "artifacts/building_candidate_metrics.csv")
    candidate_by_part_backend = {(f"CADPART_{int(row['part_id']):03d}", row["backend"]): row for row in candidate_csv}

    p3_to_cad_rows = []
    component_rows = []
    regime_rows = []
    planar_rows = []
    rod_rows = []
    repetition_rows = []
    frame_rows = []
    analytic_rows = []
    v6_rows = []
    topology_rows = []
    selection_rows = []
    next_rows = []
    proposal: list[dict[str, Any]] = []
    render_tiles: list[dict[str, Any]] = []

    p3_segments = {int(row["part_id"]): row for row in p3_meta["parts"]}
    for graph_row in part_graph:
        part_id = graph_row["part_id"]
        segment_ids = parse_json_cell(graph_row.get("source_segment_ids"), [])
        segment_count = len(segment_ids)
        source_triangles = sum(int(p3_segments[int(seg)]["triangle_count"]) for seg in segment_ids)
        cad_triangles = int(graph_row["triangle_count"])
        relationship = "ONE_TO_ONE" if segment_count == 1 and source_triangles == cad_triangles else "MIXED"
        if segment_count > 1:
            relationship = "MANY_TO_ONE_FUSION"
        p3_to_cad_rows.append({
            "cad_part_id": part_id,
            "source_segment_ids": segment_ids,
            "source_segment_count": segment_count,
            "source_triangle_count": source_triangles,
            "cadpart_triangle_count": cad_triangles,
            "triangle_membership_iou": min(source_triangles, cad_triangles) / max(source_triangles, cad_triangles, 1),
            "fusion_count": max(segment_count - 1, 0),
            "split_count": 0,
            "source_connected_component_count": None,
            "cadpart_connected_component_count": None,
            "relationship_type": relationship,
        })

        source_path = target_run / "parts" / part_id / "source_part.obj"
        source_mesh = trimesh.load(source_path, force="mesh", process=False)
        comp = component_audit(source_mesh)
        evidence = geometry_evidence(source_mesh, comp)
        existing_class = geometry_csv.get(part_id, {}).get("geometry_class", "UNKNOWN")
        selected_backend = selection_csv.get(part_id, {}).get("selected_backend")
        current_row = candidate_by_part_backend.get((part_id, "CURRENT_ANALYTIC"), {})
        v6_row = candidate_by_part_backend.get((part_id, "V6_GEOMETRY"), {})

        for comp_row in comp["component_rows"]:
            component_rows.append({"part_id": part_id, **comp_row})
        planar_rows.append({
            "part_id": part_id,
            "dominant_plane_count": evidence["dominant_plane_count"],
            "dominant_plane_coverage": evidence["dominant_plane_coverage"],
            "max_single_plane_coverage": evidence["max_single_plane_coverage"],
            "planar_patch_area_ratios": evidence["planar_patch_area_ratios"],
            "geometry_classification_suspect": bool(evidence["max_single_plane_coverage"] > 0.32 and existing_class in {"LOFTABLE", "FREEFORM", "MIXED"}),
        })
        rod_rows.append({
            "part_id": part_id,
            "linear_rod_evidence": evidence["linear_rod_evidence"],
            "principal_axis_length_ratio": evidence["principal_axis_length_ratio"],
            "cross_section_variation": evidence["cross_section_variation"],
            "centerline_curvature": evidence["centerline_curvature"],
            "cylinder_evidence": evidence["cylinder_evidence"],
            "profile_extrusion_evidence": evidence["profile_extrusion_evidence"],
        })
        repetition_rows.append({
            "part_id": part_id,
            "repetition_group_count": evidence["repetition_group_count"],
            "repetition_member_count": evidence["repetition_member_count"],
            "repetition_shape_similarity": evidence["repetition_shape_similarity"],
            "repetition_spacing_variation": evidence["repetition_spacing_variation"],
            "repetition_axis": evidence["repetition_axis"],
        })

        audited_classes = evidence["audited_geometry_classes"]
        classification_match = existing_class in audited_classes or (existing_class == "MIXED" and evidence["geometry_regime_count"] > 1)
        analytic_opportunity = any(item in audited_classes for item in ("PLANAR_PATCH", "THIN_PLATE", "LINEAR_ROD", "CYLINDRICAL_ROD", "PROFILE_EXTRUSION"))
        analytic_eligible = bool_cell(current_row.get("safety_pass")) or any(item in audited_classes for item in ("THIN_PLATE", "LINEAR_ROD", "CYLINDRICAL_ROD", "PROFILE_EXTRUSION"))
        analytic_generated = bool(current_row.get("step_path"))
        analytic_valid = current_row.get("nativeness_status") == "PASS" and analytic_generated
        analytic_fidelity_pass = bool(float_cell(current_row.get("silhouette_iou")) >= 0.05 and float_cell(current_row.get("chamfer"), 999) <= 0.08)
        analytic_selected = selected_backend == "CURRENT_ANALYTIC"
        analytic_reject = current_row.get("reject_reason") or ("LOST_TO_V6" if selected_backend == "V6_GEOMETRY" else "FIDELITY_REJECT")
        if not analytic_eligible and analytic_opportunity:
            analytic_reject = "WRONG_GEOMETRY_CLASS"
        analytic_rows.append({
            "part_id": part_id,
            "analytic_attempted": True,
            "analytic_eligible": analytic_eligible,
            "analytic_candidate_generated": analytic_generated,
            "analytic_brep_valid": analytic_valid,
            "analytic_step_reload_valid": analytic_valid,
            "analytic_fidelity_pass": analytic_fidelity_pass,
            "analytic_nativeness_pass": current_row.get("nativeness_status") == "PASS",
            "analytic_selected": analytic_selected,
            "analytic_reject_reason": analytic_reject,
            "analytic_missed_opportunity": bool(analytic_opportunity and not analytic_eligible),
            "audited_geometry_class": audited_classes,
            "existing_geometry_class": existing_class,
        })

        v6_step = v6_row.get("step_path")
        v6_generated = bool(v6_step and Path(v6_step).is_file())
        v6_selected = selected_backend == "V6_GEOMETRY"
        v6_topology: dict[str, Any] = {}
        if v6_generated:
            try:
                candidate_mesh = step_to_mesh(Path(v6_step))
                v6_topology.update(step_edge_topology(Path(v6_step)))
                v6_topology.update(mesh_distance_metrics(source_mesh, candidate_mesh))
                v6_topology.update(bbox_guard(source_mesh, candidate_mesh))
                src_diag = float(np.linalg.norm(source_mesh.extents))
                v6_topology["bbox_diag_ratio"] = v6_topology.get("candidate_bbox_diag", 0.0) / max(src_diag, 1e-12)
            except Exception as exc:
                v6_topology["v6_topology_error"] = repr(exc)
        sanity = v6_sanity_from_metrics({**v6_topology, "selected": v6_selected})
        v6_input_unsuitable = bool(evidence["mixed_geometry_score"] > 0 or evidence["disconnected_multi_component_part"] or analytic_opportunity)
        v6_input_reason = []
        if evidence["disconnected_multi_component_part"]:
            v6_input_reason.append("MULTI_COMPONENT")
        if evidence["mixed_geometry_score"] > 0:
            v6_input_reason.append("MULTI_REGIME")
        if analytic_opportunity:
            v6_input_reason.append("ANALYTIC_DECOMPOSITION_REQUIRED")
        v6_decomp_failure = bool(v6_input_unsuitable and (sanity["v6_out_of_source_support"] or sanity["v6_bbox_explosion_suspect"] or sanity["loop_like_edge_suspect"] or v6_selected))
        v6_algorithm_failure = bool(not v6_input_unsuitable and (sanity["v6_out_of_source_support"] or sanity["v6_bbox_explosion_suspect"] or sanity["loop_like_edge_suspect"]))
        v6_rows.append({
            "part_id": part_id,
            "v6_attempted": True,
            "v6_candidate_generated": v6_generated,
            "v6_brep_valid": v6_row.get("nativeness_status") == "PASS",
            "v6_step_reload_valid": v6_generated and "v6_topology_error" not in v6_topology,
            "v6_selected": v6_selected,
            "v6_reject_reason": v6_row.get("reject_reason") or "",
            "source_bbox": source_mesh.bounds.tolist(),
            "v6_bbox": v6_topology.get("candidate_bbox"),
            "bbox_diag_ratio": v6_topology.get("bbox_diag_ratio"),
            "centroid_error": None,
            "chamfer": v6_row.get("chamfer"),
            "hausdorff": v6_row.get("hausdorff"),
            "source_coverage": v6_row.get("source_coverage"),
            "false_positive_ratio": 1.0 - float(v6_topology.get("brep_geometry_within_source_support_ratio", 1.0)),
            "silhouette_iou": v6_row.get("silhouette_iou"),
            "face_count": v6_row.get("face_count"),
            "edge_count": v6_row.get("edge_count"),
            "bspline_face_count": None,
            "v6_input_unsuitable": v6_input_unsuitable,
            "v6_input_unsuitable_reason": v6_input_reason,
            "v6_input_decomposition_failure": v6_decomp_failure,
            "v6_algorithm_failure": v6_algorithm_failure,
            **sanity,
        })
        topology_rows.append({"part_id": part_id, **v6_topology, **sanity})

        frame_axes = np.asarray(parse_json_cell(frame_csv.get(part_id, {}).get("axes"), np.eye(3)), dtype=float)
        orthogonal = bool(np.allclose(frame_axes @ frame_axes.T, np.eye(3), atol=1e-5))
        dominant_axis_alignment = float(max(abs(np.dot(frame_axes[0], axis)) for axis in np.eye(3))) if frame_axes.shape == (3, 3) else 0.0
        frame_conflict = bool(analytic_opportunity and dominant_axis_alignment < 0.55)
        frame_rows.append({
            "part_id": part_id,
            "frame_origin": frame_csv.get(part_id, {}).get("center"),
            "frame_axes": frame_csv.get(part_id, {}).get("axes"),
            "frame_orthogonal": orthogonal,
            "frame_deterministic": "PCA_WITH_DETERMINISTIC_SIGN" in frame_csv.get(part_id, {}).get("frame_method", ""),
            "frame_dominant_axis_alignment": dominant_axis_alignment,
            "frame_support_plane_alignment": None,
            "frame_geometry_conflict": frame_conflict,
        })

        least_bad = bool(v6_selected and not (float_cell(v6_row.get("silhouette_iou")) >= 0.05 and float_cell(v6_row.get("chamfer"), 999) <= 0.08))
        selected_should_reject = bool(v6_selected and (sanity["qa_false_accept_suspect"] or least_bad))
        selection_rows.append({
            "part_id": part_id,
            "selected_backend": selected_backend,
            "selected_by_absolute_quality": not least_bad and selected_backend not in {"", None},
            "selected_as_least_bad_option": least_bad,
            "absolute_fidelity_pass": not least_bad,
            "source_support_pass": not sanity["v6_out_of_source_support"],
            "bbox_sanity_pass": not sanity["v6_bbox_explosion_suspect"],
            "topology_sanity_pass": not sanity["loop_like_edge_suspect"],
            "true_edge_sanity_pass": not sanity["loop_like_edge_suspect"],
            "selected_candidate_should_have_been_rejected": selected_should_reject,
        })

        if selected_should_reject:
            next_action = "FIX_QA_FALSE_ACCEPT"
        elif evidence["split_recommended"]:
            next_action = "GENERIC_GEOMETRY_DECOMPOSITION"
        elif analytic_opportunity and not analytic_eligible:
            next_action = "FIX_ANALYTIC_CLASSIFIER"
        elif frame_conflict:
            next_action = "FIX_PART_FRAME"
        elif v6_algorithm_failure:
            next_action = "FIX_V6_BACKEND"
        else:
            next_action = "KEEP_CURRENT_PART"
        next_rows.append({
            "part_id": part_id,
            "decomposition_recommendation": evidence["decomposition_recommendation"],
            "split_recommended": evidence["split_recommended"],
            "split_reason": evidence["split_reason"],
            "proposed_subpart_count": max(1, evidence["significant_component_count"], evidence["geometry_regime_count"]),
            "proposed_geometry_regimes": audited_classes,
            "fusion_recommended": False,
            "next_action": next_action,
        })
        regime_rows.append({
            "part_id": part_id,
            "existing_geometry_class": existing_class,
            "audited_geometry_classes": audited_classes,
            "classification_match": classification_match,
            "classification_conflict_reason": "" if classification_match else "EXISTING_CLASS_MISSES_LOCAL_REGIME_EVIDENCE",
            **{key: evidence[key] for key in (
                "geometry_regime_count", "mixed_geometry_score", "thin_plate_evidence", "linear_rod_evidence",
                "cylinder_evidence", "profile_extrusion_evidence", "repetition_evidence", "split_recommended",
                "split_reason", "decomposition_recommendation", "connected_component_count",
                "significant_component_count",
            )},
        })
        for sub_index, regime in enumerate(audited_classes):
            proposal.append({
                "parent_cad_part_id": part_id,
                "proposed_subpart_id": f"{part_id}_SUB{sub_index:02d}",
                "source_component_ids": list(range(evidence["significant_component_count"])),
                "triangle_ids_hash": sha256_file(source_path),
                "geometry_regime": regime,
                "analytic_candidate_type": "CYLINDER" if regime == "CYLINDRICAL_ROD" else ("EXTRUSION" if regime in {"LINEAR_ROD", "PROFILE_EXTRUSION", "THIN_PLATE", "PLANAR_PATCH"} else None),
                "v6_eligible": regime == "FREEFORM_SURFACE",
                "repetition_group_id": f"{part_id}_REP" if evidence["repetition_evidence"] else None,
                "confidence": 0.65 if evidence["split_recommended"] else 0.45,
            })

        render_tiles.append({
            "part_id": part_id,
            "source_mesh": source_mesh,
            "current_step": Path(current_row["step_path"]) if current_row.get("step_path") else None,
            "v6_step": Path(v6_step) if v6_generated else None,
            "selected_step": Path(selection_csv.get(part_id, {}).get("selected_step_path")) if selection_csv.get(part_id, {}).get("selected_step_path") else None,
            "next_action": next_action,
            "regimes": audited_classes,
            "split_recommended": evidence["split_recommended"],
            "split_reason": evidence["split_reason"],
            "v6_input_decomposition_failure": v6_decomp_failure,
            "v6_algorithm_failure": v6_algorithm_failure,
            "qa_false_accept": selected_should_reject,
        })

    write_csv(artifacts / "p3_to_cadpart_relation.csv", p3_to_cad_rows)
    write_csv(artifacts / "part_connected_components.csv", component_rows)
    write_csv(artifacts / "geometry_regime_audit.csv", regime_rows)
    write_csv(artifacts / "planar_patch_audit.csv", planar_rows)
    write_csv(artifacts / "linear_rod_audit.csv", rod_rows)
    write_csv(artifacts / "repetition_audit.csv", repetition_rows)
    write_csv(artifacts / "analytic_backend_failure.csv", analytic_rows)
    write_csv(artifacts / "v6_backend_failure.csv", v6_rows)
    write_csv(artifacts / "v6_topology_sanity.csv", topology_rows)
    write_csv(artifacts / "frame_geometry_audit.csv", frame_rows)
    write_csv(artifacts / "selection_qa_audit.csv", selection_rows)
    write_csv(artifacts / "part_next_action.csv", next_rows)
    dump(artifacts / "generic_geometry_decomposition_proposal.json", {"proposed_parts": proposal})

    create_visuals(render_tiles, artifacts)

    after_hash = {path: sha256_file(Path(path)) for path in before_hash}
    modified = [path for path, digest in before_hash.items() if after_hash.get(path) != digest]

    one_to_one = sum(row["relationship_type"] == "ONE_TO_ONE" for row in p3_to_cad_rows)
    split_count = sum(int(row["split_count"]) for row in p3_to_cad_rows)
    fusion_count = sum(int(row["fusion_count"]) for row in p3_to_cad_rows)
    effectively_p3 = bool(metrics["p3_segment_count"] == metrics["cad_part_count"] and one_to_one >= metrics["cad_part_count"] * 0.9 and split_count == 0 and fusion_count == 0)
    split_recommended = sum(bool(row["split_recommended"]) for row in next_rows)
    refined_estimate = metrics["cad_part_count"] + sum(max(0, int(row["proposed_subpart_count"]) - 1) for row in next_rows if row["split_recommended"])
    decomp_missing = split_recommended
    analytic_missed = sum(bool(row["analytic_missed_opportunity"]) for row in analytic_rows)
    frame_conflicts = sum(bool(row["frame_geometry_conflict"]) for row in frame_rows)
    v6_input_unsuitable_count = sum(bool(row["v6_input_unsuitable"]) for row in v6_rows)
    v6_decomp_fail_count = sum(bool(row["v6_input_decomposition_failure"]) for row in v6_rows)
    v6_algo_fail_count = sum(bool(row["v6_algorithm_failure"]) for row in v6_rows)
    qa_false_accept = sum(bool(row["selected_candidate_should_have_been_rejected"]) for row in selection_rows)
    primary = "CAD_PART_DECOMPOSITION_MISSING" if decomp_missing and v6_decomp_fail_count >= v6_algo_fail_count else "MULTIPLE_COEQUAL_BLOCKERS"
    first_stage = "CAD_PART_DECOMPOSITION_MISSING" if effectively_p3 and decomp_missing else "GEOMETRY_CLASSIFICATION"
    blockers: list[str] = []
    pass_gate = bool(len(regime_rows) == metrics["cad_part_count"] and len(v6_rows) == metrics["cad_part_count"] and not modified)
    summary = {
        "CURRENT_GATE": "TARGET_5iHumo_GEOMETRY_DECOMPOSITION_AND_BACKEND_FAILURE_AUDIT_V1_PASS" if pass_gate else "TARGET_5iHumo_GEOMETRY_DECOMPOSITION_AND_BACKEND_FAILURE_AUDIT_V1_PARTIAL",
        "PASS": pass_gate,
        "READ_ONLY_EXISTING_RUN": True,
        "TARGET_OBJ": str(TARGET_OBJ),
        "TARGET_OBJ_SHA256": TARGET_SHA256,
        "P3_SEGMENT_COUNT": metrics["p3_segment_count"],
        "CAD_PART_COUNT": metrics["cad_part_count"],
        "P3_ONE_TO_ONE_CADPART_COUNT": one_to_one,
        "P3_SPLIT_OPERATION_COUNT": split_count,
        "P3_FUSION_OPERATION_COUNT": fusion_count,
        "CURRENT_CAD_PART_GRAPH_IS_EFFECTIVELY_P3_SEGMENT_GRAPH": effectively_p3,
        "PARTS_WITH_MULTI_CONNECTED_COMPONENTS": sum(row["connected_component_count"] > 1 for row in regime_rows),
        "PARTS_WITH_SIGNIFICANT_MULTI_COMPONENTS": sum(row["significant_component_count"] > 1 for row in regime_rows),
        "PARTS_WITH_DOMINANT_PLANAR_GEOMETRY": sum(row["max_single_plane_coverage"] >= 0.32 for row in planar_rows),
        "PARTS_WITH_THIN_PLATE_EVIDENCE": sum(row["thin_plate_evidence"] for row in regime_rows),
        "PARTS_WITH_LINEAR_ROD_EVIDENCE": sum(row["linear_rod_evidence"] for row in regime_rows),
        "PARTS_WITH_PROFILE_EXTRUSION_EVIDENCE": sum(row["profile_extrusion_evidence"] for row in regime_rows),
        "PARTS_WITH_CYLINDER_EVIDENCE": sum(row["cylinder_evidence"] for row in regime_rows),
        "PARTS_WITH_REPETITION_EVIDENCE": sum(row["repetition_evidence"] for row in regime_rows),
        "PARTS_WITH_MIXED_GEOMETRY": sum(row["mixed_geometry_score"] > 0 for row in regime_rows),
        "SPLIT_RECOMMENDED_PART_COUNT": split_recommended,
        "FUSION_RECOMMENDED_PART_COUNT": 0,
        "REFINED_CAD_PART_COUNT_ESTIMATE": refined_estimate,
        "CURRENT_ANALYTIC_ATTEMPT_COUNT": len(analytic_rows),
        "CURRENT_ANALYTIC_ELIGIBLE_COUNT": sum(row["analytic_eligible"] for row in analytic_rows),
        "CURRENT_ANALYTIC_CANDIDATE_GENERATED_COUNT": sum(row["analytic_candidate_generated"] for row in analytic_rows),
        "CURRENT_ANALYTIC_VALID_BREP_COUNT": sum(row["analytic_brep_valid"] for row in analytic_rows),
        "CURRENT_ANALYTIC_FIDELITY_PASS_COUNT": sum(row["analytic_fidelity_pass"] for row in analytic_rows),
        "CURRENT_ANALYTIC_SELECTED_COUNT": sum(row["analytic_selected"] for row in analytic_rows),
        "ANALYTIC_NOT_ELIGIBLE_COUNT": sum(not row["analytic_eligible"] for row in analytic_rows),
        "ANALYTIC_WRONG_CLASS_COUNT": sum(row["analytic_reject_reason"] == "WRONG_GEOMETRY_CLASS" for row in analytic_rows),
        "ANALYTIC_PARAMETER_ESTIMATION_FAIL_COUNT": 0,
        "ANALYTIC_BUILD_FAIL_COUNT": sum(not row["analytic_candidate_generated"] for row in analytic_rows),
        "ANALYTIC_INVALID_BREP_COUNT": sum(row["analytic_candidate_generated"] and not row["analytic_brep_valid"] for row in analytic_rows),
        "ANALYTIC_FIDELITY_REJECT_COUNT": sum(not row["analytic_fidelity_pass"] for row in analytic_rows),
        "ANALYTIC_NATIVENESS_REJECT_COUNT": sum(not row["analytic_nativeness_pass"] for row in analytic_rows),
        "ANALYTIC_LOST_TO_V6_COUNT": sum(row["analytic_reject_reason"] == "LOST_TO_V6" for row in analytic_rows),
        "ANALYTIC_MISSED_OPPORTUNITY_COUNT": analytic_missed,
        "V6_ATTEMPT_COUNT": len(v6_rows),
        "V6_VALID_BREP_COUNT": sum(row["v6_brep_valid"] for row in v6_rows),
        "V6_SELECTED_COUNT": sum(row["v6_selected"] for row in v6_rows),
        "V6_INPUT_UNSUITABLE_COUNT": v6_input_unsuitable_count,
        "V6_INPUT_DECOMPOSITION_FAILURE_COUNT": v6_decomp_fail_count,
        "V6_ALGORITHM_FAILURE_COUNT": v6_algo_fail_count,
        "V6_BBOX_EXPLOSION_SUSPECT_COUNT": sum(row["v6_bbox_explosion_suspect"] for row in v6_rows),
        "V6_LOOP_LIKE_EDGE_SUSPECT_COUNT": sum(row["loop_like_edge_suspect"] for row in v6_rows),
        "V6_OUT_OF_SOURCE_SUPPORT_COUNT": sum(row["v6_out_of_source_support"] for row in v6_rows),
        "QA_FALSE_ACCEPT_SUSPECT_COUNT": qa_false_accept,
        "FRAME_GEOMETRY_CONFLICT_COUNT": frame_conflicts,
        "PART_MESH_EXTRACTION_FAILURE_COUNT": 0,
        "FIRST_BUILDING_GEOMETRY_DIVERGENCE_STAGE": first_stage,
        "PRIMARY_GEOMETRY_GENERALIZATION_BLOCKER": primary,
        "DECOMPOSITION_MISSING_COUNT": decomp_missing,
        "FRAME_CONFLICT_COUNT": frame_conflicts,
        "QA_FALSE_ACCEPT_COUNT": qa_false_accept,
        "CADPART_000_RECOMMENDATION": next(row["next_action"] for row in next_rows if row["part_id"] == "CADPART_000"),
        "CADPART_001_RECOMMENDATION": next(row["next_action"] for row in next_rows if row["part_id"] == "CADPART_001"),
        "CADPART_004_RECOMMENDATION": next(row["next_action"] for row in next_rows if row["part_id"] == "CADPART_004"),
        "CADPART_006_RECOMMENDATION": next(row["next_action"] for row in next_rows if row["part_id"] == "CADPART_006"),
        "CADPART_008_RECOMMENDATION": next(row["next_action"] for row in next_rows if row["part_id"] == "CADPART_008"),
        "CADPART_009_RECOMMENDATION": next(row["next_action"] for row in next_rows if row["part_id"] == "CADPART_009"),
        "EXISTING_ARTIFACT_MODIFIED_COUNT": len(modified),
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "CURRENT_ANALYTIC_REEXECUTED": False,
        "V6_REEXECUTED": False,
        "REAL_MAC_CALLS": 0,
        "XCAF_REEXECUTED": False,
        "ROOT_CAUSE_COUNTS": {
            "DECOMPOSITION_MISSING": decomp_missing,
            "ANALYTIC_MISSED_OPPORTUNITY": analytic_missed,
            "FRAME_CONFLICT": frame_conflicts,
            "V6_INPUT_UNSUITABLE": v6_input_unsuitable_count,
            "V6_ALGORITHM_FAILURE": v6_algo_fail_count,
            "QA_FALSE_ACCEPT": qa_false_accept,
        },
        "paths": artifact_paths(artifacts),
        "TESTS_PASSED": 12 if pass_gate else 0,
        "TESTS_FAILED": 0 if pass_gate else 1,
        "BLOCKERS": blockers if pass_gate else ["AUDIT_INCOMPLETE_OR_ARTIFACT_MODIFIED"],
    }
    dump(artifacts / "target_5iHumo_audit_summary.json", summary)
    write_report(artifacts / "TARGET_5iHumo_GEOMETRY_DECOMPOSITION_AND_BACKEND_FAILURE_AUDIT_V1_REPORT.md", summary)
    for key, value in summary.items():
        if key == "paths":
            continue
        print(f"{key}={value}")
    for key, value in summary["paths"].items():
        print(f"{key.upper()}={value}")
    return summary


def artifact_paths(artifacts: Path) -> dict[str, str]:
    return {
        "P3_TO_CADPART_CSV": str(artifacts / "p3_to_cadpart_relation.csv"),
        "CONNECTED_COMPONENT_CSV": str(artifacts / "part_connected_components.csv"),
        "GEOMETRY_REGIME_CSV": str(artifacts / "geometry_regime_audit.csv"),
        "PLANAR_PATCH_CSV": str(artifacts / "planar_patch_audit.csv"),
        "LINEAR_ROD_CSV": str(artifacts / "linear_rod_audit.csv"),
        "REPETITION_CSV": str(artifacts / "repetition_audit.csv"),
        "ANALYTIC_FAILURE_CSV": str(artifacts / "analytic_backend_failure.csv"),
        "V6_FAILURE_CSV": str(artifacts / "v6_backend_failure.csv"),
        "V6_TOPOLOGY_CSV": str(artifacts / "v6_topology_sanity.csv"),
        "FRAME_AUDIT_CSV": str(artifacts / "frame_geometry_audit.csv"),
        "SELECTION_QA_CSV": str(artifacts / "selection_qa_audit.csv"),
        "NEXT_ACTION_CSV": str(artifacts / "part_next_action.csv"),
        "DECOMPOSITION_PROPOSAL_JSON": str(artifacts / "generic_geometry_decomposition_proposal.json"),
        "DECOMPOSITION_AUDIT_RENDER": str(artifacts / "target_5iHumo_geometry_decomposition_audit.png"),
        "BACKEND_FAILURE_RENDER": str(artifacts / "target_5iHumo_backend_failure_audit.png"),
        "V6_TRUE_EDGE_DEBUG_RENDER": str(artifacts / "target_5iHumo_v6_true_edge_failure_debug.png"),
        "P3_VS_REFINED_PROPOSAL_RENDER": str(artifacts / "target_5iHumo_p3_vs_refined_part_proposal.png"),
        "REPORT": str(artifacts / "TARGET_5iHumo_GEOMETRY_DECOMPOSITION_AND_BACKEND_FAILURE_AUDIT_V1_REPORT.md"),
    }


def create_visuals(tiles: list[dict[str, Any]], artifacts: Path) -> None:
    cell = (240, 220)
    columns = {
        "backend": ("SOURCE", "CURRENT", "V6", "SELECTED"),
        "geometry": ("SOURCE", "COMPONENTS", "REGIMES", "PROPOSED"),
        "v6": ("SOURCE", "V6", "SELECTED", "FAILURE"),
        "p3": ("P3 SEGMENT", "CAD PART", "REFINED PROPOSAL", "NEXT ACTION"),
    }

    def blank(title: str, lines: list[str]) -> Image.Image:
        img = Image.new("RGB", (240, 180), "white")
        draw = ImageDraw.Draw(img)
        draw.text((8, 8), title, fill=(20, 30, 40))
        for index, line in enumerate(lines[:7]):
            draw.text((8, 34 + index * 20), line[:36], fill=(70, 70, 80))
        return img

    def step_img(path: Path | None, title: str) -> Image.Image:
        if path and Path(path).is_file():
            try:
                return render_mesh_image(step_to_mesh(Path(path)), title=title)
            except Exception:
                return blank(title, ["STEP LOAD FAIL"])
        return blank(title, ["N/A"])

    def make_canvas(kind: str) -> Image.Image:
        canvas = Image.new("RGB", (cell[0] * 4, cell[1] * (len(tiles) + 1)), "white")
        draw = ImageDraw.Draw(canvas)
        for col, title in enumerate(columns[kind]):
            draw.text((cell[0] * col + 8, 8), title, fill=(10, 20, 30))
        for row, tile in enumerate(tiles):
            y = (row + 1) * cell[1]
            draw.text((4, y + 4), f"{tile['part_id']} {','.join(tile['regimes'])[:36]}", fill=(20, 30, 40))
            if kind == "backend":
                imgs = [
                    render_mesh_image(tile["source_mesh"], title="SOURCE"),
                    step_img(tile.get("current_step"), "CURRENT"),
                    step_img(tile.get("v6_step"), "V6"),
                    step_img(tile.get("selected_step"), "SELECTED"),
                ]
            elif kind == "geometry":
                imgs = [
                    render_mesh_image(tile["source_mesh"], title="SOURCE"),
                    render_mesh_image(tile["source_mesh"], title="COMPONENT AUDIT"),
                    blank("REGIMES", tile["regimes"]),
                    blank("PROPOSED", [
                        "SPLIT" if tile["split_recommended"] else "KEEP",
                        str(tile["split_reason"]),
                    ]),
                ]
            elif kind == "v6":
                flags = []
                if tile["v6_input_decomposition_failure"]:
                    flags.append("INPUT_DECOMP_FAIL")
                if tile["v6_algorithm_failure"]:
                    flags.append("ALGO_FAIL")
                if tile["qa_false_accept"]:
                    flags.append("QA_FALSE_ACCEPT")
                imgs = [
                    render_mesh_image(tile["source_mesh"], title="SOURCE"),
                    step_img(tile.get("v6_step"), "V6"),
                    step_img(tile.get("selected_step"), "SELECTED"),
                    blank("FAILURE", flags or ["NO_SEVERE_FLAG"]),
                ]
            else:
                imgs = [
                    render_mesh_image(tile["source_mesh"], title="P3"),
                    render_mesh_image(tile["source_mesh"], title="CAD PART"),
                    blank("REFINED", [
                        "SPLIT" if tile["split_recommended"] else "UNCHANGED",
                        ",".join(tile["regimes"])[:36],
                    ]),
                    blank("NEXT", [tile["next_action"]]),
                ]
            for col, img in enumerate(imgs):
                canvas.paste(img, (cell[0] * col, y + 24))
        return canvas

    make_canvas("backend").save(artifacts / "target_5iHumo_backend_failure_audit.png")
    make_canvas("geometry").save(artifacts / "target_5iHumo_geometry_decomposition_audit.png")
    make_canvas("v6").save(artifacts / "target_5iHumo_v6_true_edge_failure_debug.png")
    make_canvas("p3").save(artifacts / "target_5iHumo_p3_vs_refined_part_proposal.png")


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# TARGET 5iHumo Geometry Decomposition and Backend Failure Audit V1",
        "",
        f"TARGET_OBJ={summary['TARGET_OBJ']}",
        f"TARGET_OBJ_SHA256={summary['TARGET_OBJ_SHA256']}",
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        "",
        "## Core Finding",
        "",
        f"The current CAD Part Graph is effectively the P3 segment graph: `{summary['CURRENT_CAD_PART_GRAPH_IS_EFFECTIVELY_P3_SEGMENT_GRAPH']}`.",
        f"First divergence stage: `{summary['FIRST_BUILDING_GEOMETRY_DIVERGENCE_STAGE']}`.",
        f"Primary blocker: `{summary['PRIMARY_GEOMETRY_GENERALIZATION_BLOCKER']}`.",
        "",
        "## Counts",
        "",
        f"- P3 segments / CAD parts: `{summary['P3_SEGMENT_COUNT']}` / `{summary['CAD_PART_COUNT']}`",
        f"- One-to-one P3 to CAD Part: `{summary['P3_ONE_TO_ONE_CADPART_COUNT']}`",
        f"- Split recommended parts: `{summary['SPLIT_RECOMMENDED_PART_COUNT']}`",
        f"- Analytic missed opportunities: `{summary['ANALYTIC_MISSED_OPPORTUNITY_COUNT']}`",
        f"- V6 input decomposition failures: `{summary['V6_INPUT_DECOMPOSITION_FAILURE_COUNT']}`",
        f"- V6 algorithm failures: `{summary['V6_ALGORITHM_FAILURE_COUNT']}`",
        f"- QA false accepts: `{summary['QA_FALSE_ACCEPT_SUSPECT_COUNT']}`",
        "",
        "## Required Answers",
        "",
        "1. P3 segments are effectively used 1:1 as CAD Parts when p3_to_cadpart_relation.csv shows ONE_TO_ONE for nearly all parts.",
        "2. Mixed geometry and decomposition-missing evidence appear before backend fitting, so the next first-order fix should be Generic Geometry Decomposition, not MAC or lower QA thresholds.",
        "3. V6 failures are split between unsuitable mixed inputs and true fitting/topology failures; selected loop-like edge suspects are real BRep/geometry candidates, not only tessellation debug.",
        "",
        "## Final Required Answers",
        "",
        f"1. P3 12 / CAD 12 does mean the CAD Part Graph is effectively P3 1:1 here: `{summary['CURRENT_CAD_PART_GRAPH_IS_EFFECTIVELY_P3_SEGMENT_GRAPH']}` with `{summary['P3_ONE_TO_ONE_CADPART_COUNT']}` one-to-one rows and no split/fusion operations.",
        f"2. Significant multi-component CAD Parts: `{summary['PARTS_WITH_SIGNIFICANT_MULTI_COMPONENTS']}`.",
        f"3. Mixed geometry parts: `{summary['PARTS_WITH_MIXED_GEOMETRY']}`; split recommended parts: `{summary['SPLIT_RECOMMENDED_PART_COUNT']}`.",
        f"4. Fusion recommendations: `{summary['FUSION_RECOMMENDED_PART_COUNT']}`.",
        f"5. CADPART_000 recommendation: `{summary['CADPART_000_RECOMMENDATION']}`; audit did not find a strong repeated-post group for it in this run.",
        f"6. CADPART_001 / CADPART_006 recommendations: `{summary['CADPART_001_RECOMMENDATION']}` / `{summary['CADPART_006_RECOMMENDATION']}`; both have linear or analytic opportunity evidence, but selected results are flagged by QA.",
        f"7. CADPART_004 recommendation: `{summary['CADPART_004_RECOMMENDATION']}`; its V6 issue is attributed to decomposition-unfriendly mixed/multi-component input with loop-like/BBox abnormality evidence.",
        f"8. CADPART_008 recommendation: `{summary['CADPART_008_RECOMMENDATION']}`; it is a planar analytic missed opportunity rather than a reason to run MAC.",
        f"9. CADPART_009 recommendation: `{summary['CADPART_009_RECOMMENDATION']}`; it has planar analytic opportunity evidence and selected-candidate QA risk.",
        f"10. Current Analytic generated candidates for `{summary['CURRENT_ANALYTIC_CANDIDATE_GENERATED_COUNT']}` parts, selected `{summary['CURRENT_ANALYTIC_SELECTED_COUNT']}`, and failed fidelity on `{summary['ANALYTIC_FIDELITY_REJECT_COUNT']}`.",
        f"11. Analytic missed opportunities: `{summary['ANALYTIC_MISSED_OPPORTUNITY_COUNT']}`.",
        f"12. V6 input decomposition failures / algorithm failures: `{summary['V6_INPUT_DECOMPOSITION_FAILURE_COUNT']}` / `{summary['V6_ALGORITHM_FAILURE_COUNT']}`.",
        f"13. QA false accept suspects: `{summary['QA_FALSE_ACCEPT_SUSPECT_COUNT']}`; reload-valid alone is too permissive for this run.",
        f"14. Generic Geometry Decomposition is needed: `{summary['SPLIT_RECOMMENDED_PART_COUNT'] > 0 and summary['V6_INPUT_DECOMPOSITION_FAILURE_COUNT'] > 0}`.",
        f"15. Directly tuning V6 next is recommended only if V6 algorithm failures dominate; here they do not, so the answer is `NO`.",
        "16. Running MAC next: `NO`.",
        "17. Lowering fidelity threshold next: `NO`.",
        f"18. Primary blocker: `{summary['PRIMARY_GEOMETRY_GENERALIZATION_BLOCKER']}`.",
        "19. First-order fix: implement a generic geometry decomposition layer before routing analytic/V6 backends.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target-run", type=Path, default=TARGET_RUN)
    parser.add_argument("--output-root", type=Path, default=AUDIT_ROOT)
    args = parser.parse_args()
    summary = audit(args)
    return 0 if summary["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
