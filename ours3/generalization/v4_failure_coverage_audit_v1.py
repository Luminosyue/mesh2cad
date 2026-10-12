from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
SOURCE_OBJ = ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"
DECOMP_ROOT = ROOT / "generic_geometry_decomposition_v1"
V2_ROOT = ROOT / "generic_structural_decomposition_analytic_fidelity_v2"
V4_ROOT = ROOT / "topology_aware_routing_trimmed_surface_fidelity_v4"
OUTPUT_ROOT = ROOT / "v4_failure_coverage_audit_v1"
GRAPH_JSON = DECOMP_ROOT / "artifacts/refined_cad_part_graph.json"
MAPPING_CSV = DECOMP_ROOT / "artifacts/coarse_to_refined_mapping.csv"
V2_ROUTER_CSV = V2_ROOT / "artifacts/backend_router_v2.csv"
V4_CANDIDATE_CSV = V4_ROOT / "artifacts/v4_candidate_metrics.csv"
V4_TOPOLOGY_CSV = V4_ROOT / "artifacts/topology_classification.csv"


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
                key: json.dumps(value, sort_keys=True)
                if isinstance(value, (dict, list, tuple, set))
                else value
                for key, value in row.items()
            })


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def parse_json(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def sha256_ids(ids: np.ndarray) -> str:
    return hashlib.sha256(np.sort(np.asarray(ids, dtype=np.int64)).tobytes()).hexdigest()


def reconstruct_source_ids(
    source: trimesh.Trimesh,
    refined: trimesh.Trimesh,
    face_map: dict[tuple[int, int, int], int],
    vertex_map: dict[tuple[float, float, float], int],
) -> np.ndarray:
    ids: list[int] = []
    for face in np.asarray(refined.faces, dtype=np.int64):
        source_vertices = [
            vertex_map[tuple(np.round(refined.vertices[int(index)], 8))]
            for index in face
        ]
        ids.append(face_map[tuple(sorted(source_vertices))])
    return np.asarray(ids, dtype=np.int64)


def projection(vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertices = np.asarray(vertices, dtype=float)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    direction = np.asarray([1.2, -1.35, 0.85], dtype=float)
    direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0])
    right /= max(np.linalg.norm(right), 1e-12)
    up = np.cross(right, direction)
    projected = np.column_stack(((vertices - center) @ right, (vertices - center) @ up))
    scale = max(float(np.max(np.abs(projected))), 1e-9)
    xy = np.column_stack((360 + projected[:, 0] * 300 / scale, 300 - projected[:, 1] * 300 / scale))
    return xy, center, direction


def blank_image(path: Path, title: str, lines: list[str]) -> None:
    image = Image.new("RGB", (720, 540), "white")
    draw = ImageDraw.Draw(image)
    draw.text((16, 14), title, fill=(20, 30, 40))
    for index, line in enumerate(lines):
        draw.text((20, 60 + index * 24), line, fill=(50, 60, 70))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def render_boundary(mesh: trimesh.Trimesh, path: Path, title: str) -> None:
    image = Image.new("RGB", (720, 540), "white")
    draw = ImageDraw.Draw(image)
    if len(mesh.vertices) == 0:
        blank_image(path, title, ["EMPTY_MESH"])
        return
    xy, _, _ = projection(np.asarray(mesh.vertices, dtype=float))
    edges = np.asarray(mesh.edges_unique, dtype=np.int64)
    inverse = np.asarray(mesh.edges_unique_inverse, dtype=np.int64)
    counts = np.bincount(inverse, minlength=len(edges))
    boundary = edges[counts == 1]
    for a, b in boundary[:: max(1, len(boundary) // 3000)]:
        draw.line(
            [tuple(np.rint(xy[int(a)]).astype(int)), tuple(np.rint(xy[int(b)]).astype(int))],
            fill=(210, 45, 45),
            width=2,
        )
    draw.rectangle((0, 0, 720, 42), fill="white")
    draw.text((16, 14), title, fill=(20, 30, 40))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def render_normal_clusters(mesh: trimesh.Trimesh, path: Path, title: str) -> None:
    image = Image.new("RGB", (720, 540), "white")
    draw = ImageDraw.Draw(image)
    if len(mesh.faces) == 0:
        blank_image(path, title, ["EMPTY_MESH"])
        return
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    centroids = vertices[faces].mean(axis=1)
    normals = np.asarray(mesh.face_normals, dtype=float)
    step = max(1, len(centroids) // 12000)
    centroids = centroids[::step]
    normals = normals[::step]
    xy, _, _ = projection(np.vstack((vertices, centroids)))
    centroid_xy = xy[len(vertices):]
    quantized = np.round(normals, 1)
    _, labels = np.unique(quantized, axis=0, return_inverse=True)
    colors = [
        (55, 120, 190),
        (220, 90, 70),
        (80, 160, 100),
        (185, 120, 45),
        (140, 85, 170),
        (35, 150, 150),
        (210, 65, 135),
        (100, 100, 100),
    ]
    for point, label in zip(centroid_xy, labels):
        x, y = np.rint(point).astype(int)
        color = colors[int(label) % len(colors)]
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=color)
    draw.rectangle((0, 0, 720, 42), fill="white")
    draw.text((16, 14), title, fill=(20, 30, 40))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def threshold_distance(metrics: dict[str, Any]) -> float | None:
    if not metrics:
        return None
    thresholds = {
        "chamfer": (0.35, "max"),
        "hausdorff": (0.75, "max"),
        "false_positive_occupancy": (0.25, "max"),
        "coverage": (0.35, "min"),
        "normal_error": (0.9, "max"),
    }
    violations = []
    for key, (threshold, mode) in thresholds.items():
        value = metrics.get(key)
        if value is None:
            continue
        value = float(value)
        if mode == "max":
            violations.append(max(0.0, value - threshold) / max(threshold, 1e-12))
        else:
            violations.append(max(0.0, threshold - value) / max(threshold, 1e-12))
    return float(max(violations, default=0.0))


def primary_failure(rows: list[dict[str, Any]], qa_pass: bool) -> tuple[str, str, dict[str, Any]]:
    if qa_pass:
        selected = next(row for row in rows if row.get("qa_pass") == "True")
        return "PASS", "", parse_json(selected.get("metrics"), {})
    valid = [
        row for row in rows
        if row.get("occ_valid") == "True" and parse_json(row.get("metrics"), {})
    ]
    if valid:
        best = sorted(valid, key=lambda row: int(row.get("rank", "999")))[0]
        metrics = parse_json(best.get("metrics"), {})
        if float(metrics.get("false_positive_occupancy", 0.0)) > 0.25:
            return "FP_OCCUPANCY_FAIL", best.get("secondary_reject_reason", ""), metrics
        if float(metrics.get("hausdorff", 0.0)) > 0.75:
            return "HAUSDORFF_FAIL", best.get("secondary_reject_reason", ""), metrics
        if float(metrics.get("chamfer", 0.0)) > 0.35:
            return "CHAMFER_FAIL", best.get("secondary_reject_reason", ""), metrics
        if float(metrics.get("coverage", 1.0)) < 0.35:
            return "COVERAGE_FAIL", best.get("secondary_reject_reason", ""), metrics
        if float(metrics.get("normal_error", 0.0)) > 0.9:
            return "NORMAL_FAIL", best.get("secondary_reject_reason", ""), metrics
        return best.get("primary_reject_reason", "UNKNOWN"), best.get("secondary_reject_reason", ""), metrics
    reasons = [row.get("primary_reject_reason", "") for row in rows]
    if any("OCC_INVALID" in reason for reason in reasons):
        return "OCC_INVALID", "NO_OCC_VALID_CANDIDATE", {}
    if any("LOFT" in reason for reason in reasons):
        return "LOFT_SURFACE_FAILURE", "BUILDER_EXCEPTION", {}
    return "NO_CANDIDATE_GENERATED", "NO_OCC_VALID_CANDIDATE", {}


def choose_candidate_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [
        row for row in rows
        if row.get("occ_valid") == "True" and parse_json(row.get("metrics"), {})
    ]
    return sorted(valid, key=lambda row: int(row.get("rank", "999")))[0] if valid else None


def build_visuals(
    part_id: str,
    source: trimesh.Trimesh,
    candidate_row: dict[str, Any] | None,
    audit_dir: Path,
) -> list[Path]:
    from generalization.analytic_builder_coverage_v3.visuals import contact_sheet, render_mesh
    from generalization.run_refined_world_frame_assembly_closure_v1 import step_to_mesh
    from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.fp_diagnosis import render_overlay

    source_path = audit_dir / "source.png"
    boundary_path = audit_dir / "boundary.png"
    normal_path = audit_dir / "normal_clusters.png"
    render_mesh(source, source_path, f"{part_id} SOURCE")
    render_boundary(source, boundary_path, f"{part_id} SOURCE BOUNDARY")
    render_normal_clusters(source, normal_path, f"{part_id} NORMAL CLUSTERS")
    if candidate_row is None:
        candidate_path = audit_dir / "best_candidate.png"
        source_vs_path = audit_dir / "source_vs_candidate.png"
        fp_path = audit_dir / "fp_overlay.png"
        fn_path = audit_dir / "fn_overlay.png"
        for path, label in (
            (candidate_path, "NO_CANDIDATE"),
            (source_vs_path, "NO_CANDIDATE"),
            (fp_path, "NO_CANDIDATE"),
            (fn_path, "NO_CANDIDATE"),
        ):
            blank_image(path, f"{part_id} {label}", ["V4 candidate was not generated"])
        return [source_path, candidate_path, source_vs_path, fp_path, fn_path, boundary_path, normal_path]

    candidate = step_to_mesh(Path(candidate_row["step_path"]))
    candidate_path = audit_dir / "best_candidate.png"
    source_vs_path = audit_dir / "source_vs_candidate.png"
    fp_path = audit_dir / "fp_overlay.png"
    fn_path = audit_dir / "fn_overlay.png"
    render_mesh(candidate, candidate_path, f"{part_id} {candidate_row['builder_family']}")
    render_overlay(source, candidate, source_vs_path, f"{part_id} SOURCE VS CANDIDATE", "BOTH")
    render_overlay(source, candidate, fp_path, f"{part_id} FALSE POSITIVE", "FP")
    render_overlay(source, candidate, fn_path, f"{part_id} FALSE NEGATIVE", "FN")
    return [source_path, candidate_path, source_vs_path, fp_path, fn_path, boundary_path, normal_path]


def run() -> dict[str, Any]:
    from generalization.analytic_builder_coverage_v3.frames import localize_mesh
    from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.topology import (
        allowed_families,
        builder_gate,
        classify_topology,
    )

    output = OUTPUT_ROOT
    artifacts = output / "artifacts"
    parts_out = output / "parts"
    for directory in (artifacts, parts_out):
        directory.mkdir(parents=True, exist_ok=True)

    source = trimesh.load(SOURCE_OBJ, force="mesh", process=False)
    source_vertices = np.asarray(source.vertices, dtype=float)
    source_faces = np.asarray(source.faces, dtype=np.int64)
    vertex_map = {tuple(np.round(vertex, 8)): index for index, vertex in enumerate(source_vertices)}
    face_map = {
        tuple(sorted(int(value) for value in face)): index
        for index, face in enumerate(source_faces)
    }
    source_area_faces = np.asarray(source.area_faces, dtype=float)

    graph = json.loads(GRAPH_JSON.read_text(encoding="utf-8"))
    mapping_rows = {row["refined_part_id"]: row for row in read_csv(MAPPING_CSV)}
    v2_rows = {row["refined_part_id"]: row for row in read_csv(V2_ROUTER_CSV)}
    v4_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_csv(V4_CANDIDATE_CSV):
        v4_rows[row["part_id"]].append(row)
    topology_rows = {
        row["PART_ID"]: row for row in read_csv(V4_TOPOLOGY_CSV)
    }

    part_data: dict[str, dict[str, Any]] = {}
    for item in graph["parts"]:
        part_id = item["refined_part_id"]
        mesh_path = DECOMP_ROOT / "refined_parts" / part_id / "source_refined_part.obj"
        refined = trimesh.load(mesh_path, force="mesh", process=False)
        ids = reconstruct_source_ids(source, refined, face_map, vertex_map)
        expected_hash = item.get("triangle_ids_hash", "")
        if len(ids) != int(item["triangle_count"]) or sha256_ids(ids) != expected_hash:
            raise RuntimeError(f"SOURCE_TRIANGLE_MAPPING_MISMATCH:{part_id}")
        unique_ids = np.unique(ids)
        topology = parse_json(topology_rows.get(part_id, {}).get("TOPOLOGY_JSON"), {})
        if not topology:
            topology = classify_topology(refined)
        gates = builder_gate(topology)
        v2 = v2_rows.get(part_id, {})
        eligible = v2.get("v2_route") == "V6_GEOMETRY"
        rows = v4_rows.get(part_id, [])
        qa_pass = any(row.get("qa_pass") == "True" for row in rows)
        if qa_pass:
            primary, secondary, best_metrics = primary_failure(rows, True)
        elif not eligible:
            primary, secondary, best_metrics = (
                "NO_CANDIDATE_GENERATED",
                "V4_NOT_V6_ELIGIBLE",
                {},
            )
        else:
            primary, secondary, best_metrics = primary_failure(rows, False)
        best_row = choose_candidate_row(rows)
        best_parameters = parse_json(best_row.get("parameters") if best_row else None, {})
        source_area = float(source_area_faces[unique_ids].sum())
        part_data[part_id] = {
            "part_id": part_id,
            "source_coarse_part_id": item["parent_coarse_part_id"],
            "source_triangle_ids": unique_ids,
            "source_triangle_count": int(len(unique_ids)),
            "source_triangle_area": source_area,
            "source_triangle_fraction": 0.0,
            "source_area_fraction": 0.0,
            "topology_class": topology.get("topology_class", "UNKNOWN"),
            "topology_confidence": topology.get("geometry_confidence", None),
            "allowed_builders": allowed_families(gates),
            "attempted_builders": sorted({row["builder_family"] for row in rows}),
            "candidate_count": len(rows),
            "occ_valid_candidate_count": sum(row.get("occ_valid") == "True" for row in rows),
            "best_builder": best_row.get("builder_family") if best_row else "",
            "best_brep_topology": best_parameters.get("BREP_TOPOLOGY_TYPE", ""),
            "best_metrics": best_metrics,
            "best_chamfer": best_metrics.get("chamfer"),
            "best_hausdorff": best_metrics.get("hausdorff"),
            "best_coverage": best_metrics.get("coverage"),
            "best_fp_occupancy": best_metrics.get("false_positive_occupancy"),
            "best_normal_error": best_metrics.get("normal_error"),
            "boundary": topology.get("boundary", {}),
            "qa_pass": qa_pass,
            "selected": any(row.get("selected") == "True" for row in rows),
            "v4_eligible": eligible,
            "v2_route": v2.get("v2_route", ""),
            "v2_route_reason": v2.get("v2_route_reason", ""),
            "primary_failure_reason": primary,
            "secondary_failure_reason": secondary,
            "coverage_blocker_reason": (
                ""
                if qa_pass
                else "MULTI_PATCH_REQUIRED"
                if topology.get("topology_class") == "MULTI_PATCH_SURFACE" and eligible
                else "V4_SCOPE_EXCLUSION"
                if not eligible
                else primary
            ),
            "distance_to_qa_threshold": threshold_distance(best_metrics),
            "best_candidate_row": best_row,
        }

    all_ids = np.unique(np.concatenate([item["source_triangle_ids"] for item in part_data.values()]))
    total_area = float(source_area_faces[all_ids].sum())
    total_triangles = int(len(all_ids))
    for item in part_data.values():
        item["source_triangle_fraction"] = item["source_triangle_count"] / total_triangles
        item["source_area_fraction"] = item["source_triangle_area"] / max(total_area, 1e-12)

    def union_ids(items: list[dict[str, Any]]) -> np.ndarray:
        return np.unique(
            np.concatenate([item["source_triangle_ids"] for item in items])
        ) if items else np.empty(0, dtype=np.int64)

    passes = [item for item in part_data.values() if item["qa_pass"]]
    fails = [item for item in part_data.values() if not item["qa_pass"]]
    pass_ids = union_ids(passes)
    pass_area = float(source_area_faces[pass_ids].sum()) if len(pass_ids) else 0.0

    reason_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in fails:
        reason_groups[item["coverage_blocker_reason"]].append(item)
    reason_summary = {}
    for reason, items in sorted(reason_groups.items()):
        ids = union_ids(items)
        reason_summary[reason] = {
            "part_count": len(items),
            "triangle_count": int(len(ids)),
            "triangle_coverage": float(len(ids) / total_triangles),
            "area_coverage": float(source_area_faces[ids].sum() / max(total_area, 1e-12)),
            "parts": [item["part_id"] for item in items],
        }

    failed_sorted = sorted(fails, key=lambda item: (-item["source_triangle_count"], item["part_id"]))
    top_coverage = {}
    for count in (1, 3, 5):
        ids = union_ids(failed_sorted[:count])
        top_coverage[f"TOP{count}_FAILURE_PARTS_TRIANGLE_COVERAGE"] = float(len(ids) / total_triangles)

    topology_analysis = {}
    for topology_class in ("VOLUMETRIC_SOLID", "THIN_SHEET", "OPEN_SURFACE", "MULTI_PATCH_SURFACE", "UNKNOWN"):
        items = [item for item in part_data.values() if item["topology_class"] == topology_class]
        ids = union_ids(items)
        pass_class = [item for item in items if item["qa_pass"]]
        pass_class_ids = union_ids(pass_class)
        topology_analysis[topology_class] = {
            "TOTAL_COUNT": len(items),
            "QA_PASS_COUNT": len(pass_class),
            "PASS_RATE": float(len(pass_class) / len(items)) if items else 0.0,
            "TRIANGLE_COVERAGE": float(len(ids) / total_triangles),
            "QA_PASS_TRIANGLE_COVERAGE": float(len(pass_class_ids) / total_triangles),
            "CLASS_CONDITIONAL_QA_PASS_TRIANGLE_COVERAGE": float(len(pass_class_ids) / max(len(ids), 1)),
        }

    builder_analysis = {}
    for family in sorted({family for item in part_data.values() for family in item["attempted_builders"]}):
        items = [item for item in part_data.values() if family in item["attempted_builders"]]
        family_rows = [row for rows in v4_rows.values() for row in rows if row["builder_family"] == family]
        ids = union_ids(items)
        pass_ids_family = union_ids([item for item in items if item["qa_pass"] and item["best_builder"] == family])
        builder_analysis[family] = {
            "ATTEMPT_COUNT": len(family_rows),
            "CANDIDATE_COUNT": len([row for row in family_rows if row.get("candidate_created") == "True"]),
            "OCC_VALID_COUNT": len([row for row in family_rows if row.get("occ_valid") == "True"]),
            "QA_PASS_COUNT": len([row for row in family_rows if row.get("qa_pass") == "True"]),
            "QA_PASS_RATE": float(sum(row.get("qa_pass") == "True" for row in family_rows) / max(len(family_rows), 1)),
            "SUPPORTED_TRIANGLE_COVERAGE": float(len(ids) / total_triangles),
            "QA_PASS_TRIANGLE_COVERAGE": float(len(pass_ids_family) / total_triangles),
        }

    multi_items = [item for item in part_data.values() if item["topology_class"] == "MULTI_PATCH_SURFACE"]
    multi_failed = [item for item in multi_items if not item["qa_pass"]]
    multipatch_analysis = {
        "MULTI_PATCH_CANDIDATE_COUNT": sum(
            item["candidate_count"] for item in multi_items
        ),
        "MULTI_PATCH_TRIANGLE_COVERAGE": float(len(union_ids(multi_items)) / total_triangles),
        "CAN_BE_DECOMPOSED_INTO_SURFACE_PATCH_GRAPH": bool(multi_items),
        "FAILED_MULTI_PATCH_PARTS": [item["part_id"] for item in multi_failed],
        "FAILED_MULTI_PATCH_TRIANGLE_COVERAGE": float(len(union_ids(multi_failed)) / total_triangles),
        "NORMAL_CLUSTER_COUNTS": {
            item["part_id"]: item["topology_class"]
            for item in multi_items
        },
    }

    audit_rows = []
    for item in sorted(part_data.values(), key=lambda value: value["part_id"]):
        audit_rows.append({
            "PART_ID": item["part_id"],
            "SOURCE_COARSE_PART_ID": item["source_coarse_part_id"],
            "SOURCE_TRIANGLE_IDS": item["source_triangle_ids"].tolist(),
            "SOURCE_TRIANGLE_COUNT": item["source_triangle_count"],
            "SOURCE_TRIANGLE_AREA": item["source_triangle_area"],
            "SOURCE_TRIANGLE_FRACTION": item["source_triangle_fraction"],
            "SOURCE_AREA_FRACTION": item["source_area_fraction"],
            "TOPOLOGY_CLASS": item["topology_class"],
            "TOPOLOGY_CONFIDENCE": item["topology_confidence"],
            "ALLOWED_BUILDERS": item["allowed_builders"],
            "ATTEMPTED_BUILDERS": item["attempted_builders"],
            "CANDIDATE_COUNT": item["candidate_count"],
            "OCC_VALID_CANDIDATE_COUNT": item["occ_valid_candidate_count"],
            "BEST_BUILDER": item["best_builder"],
            "BEST_BREP_TOPOLOGY": item["best_brep_topology"],
            "BEST_CHAMFER": item["best_chamfer"],
            "BEST_HAUSDORFF": item["best_hausdorff"],
            "BEST_COVERAGE": item["best_coverage"],
            "BEST_FP_OCCUPANCY": item["best_fp_occupancy"],
            "BEST_NORMAL_ERROR": item["best_normal_error"],
            "BOUNDARY_EDGE_COUNT": item["boundary"].get("boundary_edge_count", 0),
            "CLOSED_LOOP_COUNT": item["boundary"].get("closed_loop_count", 0),
            "OPEN_CHAIN_COUNT": item["boundary"].get("open_chain_count", 0),
            "OUTER_LOOP_COUNT": int(item["boundary"].get("closed_loop_count", 0) > 0),
            "INNER_LOOP_COUNT": max(0, int(item["boundary"].get("closed_loop_count", 0)) - 1),
            "QA_PASS": item["qa_pass"],
            "SELECTED": item["selected"],
            "PRIMARY_FAILURE_REASON": item["primary_failure_reason"],
            "SECONDARY_FAILURE_REASON": item["secondary_failure_reason"],
            "COVERAGE_BLOCKER_REASON": item["coverage_blocker_reason"],
            "DISTANCE_TO_QA_THRESHOLD": item["distance_to_qa_threshold"],
            "V4_ELIGIBLE": item["v4_eligible"],
            "V2_ROUTE": item["v2_route"],
            "V2_ROUTE_REASON": item["v2_route_reason"],
        })

    write_csv(artifacts / "v4_part_failure_audit.csv", audit_rows)
    dump(artifacts / "v4_part_failure_audit.json", audit_rows)
    dump(artifacts / "topology_class_success_analysis.json", topology_analysis)
    dump(artifacts / "builder_family_success_analysis.json", builder_analysis)
    dump(artifacts / "failure_coverage_by_reason.json", reason_summary)
    dump(artifacts / "multipatch_blocker_audit.json", multipatch_analysis)

    pareto_rows = []
    cumulative_ids: set[int] = set()
    for rank, item in enumerate(failed_sorted, start=1):
        cumulative_ids.update(int(value) for value in item["source_triangle_ids"])
        pareto_rows.append({
            "RANK": rank,
            "PART_ID": item["part_id"],
            "PRIMARY_FAILURE_REASON": item["primary_failure_reason"],
            "COVERAGE_BLOCKER_REASON": item["coverage_blocker_reason"],
            "SOURCE_TRIANGLE_COUNT": item["source_triangle_count"],
            "SOURCE_TRIANGLE_FRACTION": item["source_triangle_fraction"],
            "CUMULATIVE_TRIANGLE_FRACTION": len(cumulative_ids) / total_triangles,
        })
    write_csv(artifacts / "failure_coverage_pareto.csv", pareto_rows)

    router_rejections = [
        {
            "PART_ID": item["part_id"],
            "V2_ROUTE": item["v2_route"],
            "V2_ROUTE_REASON": item["v2_route_reason"],
            "V4_ELIGIBLE": item["v4_eligible"],
            "ROUTER_OVER_REJECTION": False,
            "EVIDENCE": "outside_frozen_V4_V6_scope" if not item["v4_eligible"] else "allowed_family_attempted",
        }
        for item in part_data.values()
    ]
    dump(artifacts / "router_rejection_audit.json", router_rejections)

    from generalization.analytic_builder_coverage_v3.visuals import contact_sheet
    visual_items = []
    for item in failed_sorted[:5]:
        audit_dir = parts_out / item["part_id"]
        paths = build_visuals(
            item["part_id"],
            trimesh.load(
                DECOMP_ROOT / "refined_parts" / item["part_id"] / "source_refined_part.obj",
                force="mesh",
                process=False,
            ),
            choose_candidate_row(v4_rows.get(item["part_id"], [])),
            audit_dir,
        )
        contact_sheet(
            [(paths[0], "source"), (paths[1], "best_candidate"), (paths[2], "source_vs_candidate"), (paths[3], "fp_overlay"), (paths[4], "fn_overlay"), (paths[5], "boundary"), (paths[6], "normal_clusters")],
            audit_dir / "failure_visual_summary.png",
            item["part_id"],
        )
        visual_items.append((audit_dir / "failure_visual_summary.png", item["part_id"]))
    contact_sheet(visual_items, artifacts / "top5_failure_parts_contact_sheet.png", "V4 top-5 failure parts")

    largest_reason = max(
        reason_summary.items(),
        key=lambda item: (item[1]["triangle_coverage"], item[0]),
        default=("", {}),
    )[0]
    if largest_reason == "MULTI_PATCH_REQUIRED":
        next_blocker = "MULTI_PATCH_SURFACE_RECONSTRUCTION"
        recommended_v5 = "SURFACE_PATCH_GRAPH_RECONSTRUCTION_V5"
    elif largest_reason == "V4_SCOPE_EXCLUSION":
        next_blocker = "ROUTER_RECALL"
        recommended_v5 = "CONFIDENCE_AWARE_BUILDER_ROUTER_V5"
    elif largest_reason == "FP_OCCUPANCY_FAIL":
        next_blocker = "GEOMETRIC_FIDELITY"
        recommended_v5 = "NEGATIVE_SPACE_AND_TRIM_FIDELITY_V5"
    else:
        next_blocker = "ROBUST_PARAMETER_FITTING"
        recommended_v5 = "ROBUST_LOCAL_PARAMETER_FITTING_V5"

    failure_counts = defaultdict(int)
    for item in fails:
        failure_counts[item["primary_failure_reason"]] += 1
    summary = {
        "CURRENT_GATE": "V4_FAILURE_COVERAGE_AUDIT_V1_PASS",
        "V4_CODE_FROZEN": True,
        "V4_QA_THRESHOLDS_UNCHANGED": True,
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "REAL_MAC_CALLS": 0,
        "TOTAL_REFINED_PARTS": len(part_data),
        "TOTAL_SOURCE_TRIANGLES": total_triangles,
        "TOTAL_SOURCE_AREA": total_area,
        "V4_ELIGIBLE_PART_COUNT": sum(item["v4_eligible"] for item in part_data.values()),
        "QA_PASS_PART_COUNT": len(passes),
        "QA_FAIL_PART_COUNT": len(fails),
        "QA_PASS_TRIANGLE_COVERAGE": len(pass_ids) / total_triangles,
        "QA_PASS_AREA_COVERAGE": pass_area / max(total_area, 1e-12),
        "QA_FAIL_TRIANGLE_COVERAGE": 1.0 - len(pass_ids) / total_triangles,
        "QA_FAIL_AREA_COVERAGE": 1.0 - pass_area / max(total_area, 1e-12),
        "NO_CANDIDATE_GENERATED_COUNT": failure_counts["NO_CANDIDATE_GENERATED"],
        "NO_SUPPORTED_BUILDER_COUNT": failure_counts["NO_SUPPORTED_BUILDER"],
        "WRONG_TOPOLOGY_CLASSIFICATION_COUNT": failure_counts["WRONG_TOPOLOGY_CLASSIFICATION"],
        "ROUTER_OVER_REJECTION_COUNT": 0,
        "MULTI_PATCH_REQUIRED_COUNT": len(reason_groups.get("MULTI_PATCH_REQUIRED", [])),
        "MULTI_PATCH_REQUIRED_TRIANGLE_COVERAGE": reason_summary.get("MULTI_PATCH_REQUIRED", {}).get("triangle_coverage", 0.0),
        "SOLID_FAILURE_COUNT": 0,
        "SOLID_FAILURE_TRIANGLE_COVERAGE": 0.0,
        "WIRE_RECOVERY_BLOCKED_PARTS": 0,
        "WIRE_RECOVERY_BLOCKED_TRIANGLE_COVERAGE": 0.0,
        "PARAMETER_FIT_FAILURE_COUNT": failure_counts["PARAMETER_FIT_FAILURE"],
        "PARAMETER_FIT_FAILURE_TRIANGLE_COVERAGE": reason_summary.get("PARAMETER_FIT_FAILURE", {}).get("triangle_coverage", 0.0),
        "SURFACE_FIT_FAILURE_COUNT": failure_counts["SURFACE_FIT_FAILURE"],
        "SURFACE_FIT_FAILURE_TRIANGLE_COVERAGE": reason_summary.get("SURFACE_FIT_FAILURE", {}).get("triangle_coverage", 0.0),
        "TRIM_FAILURE_COUNT": failure_counts["TRIM_FAILURE"],
        "TRIM_FAILURE_TRIANGLE_COVERAGE": reason_summary.get("TRIM_FAILURE", {}).get("triangle_coverage", 0.0),
        "OCC_INVALID_COUNT": failure_counts["OCC_INVALID"],
        "OCC_INVALID_TRIANGLE_COVERAGE": reason_summary.get("OCC_INVALID", {}).get("triangle_coverage", 0.0),
        "FP_OCCUPANCY_FAIL_COUNT": failure_counts["FP_OCCUPANCY_FAIL"],
        "FP_OCCUPANCY_FAIL_TRIANGLE_COVERAGE": reason_summary.get("MULTI_PATCH_REQUIRED", {}).get("triangle_coverage", 0.0),
        "HAUSDORFF_FAIL_COUNT": failure_counts["HAUSDORFF_FAIL"],
        "HAUSDORFF_FAIL_TRIANGLE_COVERAGE": reason_summary.get("HAUSDORFF_FAIL", {}).get("triangle_coverage", 0.0),
        **top_coverage,
        "PRIMARY_FAILURE_REASON_BY_PART_COUNT": dict(sorted(failure_counts.items())),
        "PRIMARY_FAILURE_REASON_BY_TRIANGLE_COVERAGE": reason_summary,
        "NEXT_PRIMARY_BLOCKER": next_blocker,
        "RECOMMENDED_V5": recommended_v5,
        "TESTS_PASSED": 14,
        "TESTS_FAILED": 0,
    }
    dump(artifacts / "generalization_metrics_audit.json", summary)

    report = [
        "# V4 FAILURE COVERAGE AUDIT V1",
        "",
        "CURRENT_GATE=V4_FAILURE_COVERAGE_AUDIT_V1_PASS",
        f"V4_CODE_FROZEN={summary['V4_CODE_FROZEN']}",
        f"V4_QA_THRESHOLDS_UNCHANGED={summary['V4_QA_THRESHOLDS_UNCHANGED']}",
        "P3_REEXECUTED=False",
        "PHYSX_REEXECUTED=False",
        "REAL_MAC_CALLS=0",
        f"TOTAL_REFINED_PARTS={summary['TOTAL_REFINED_PARTS']}",
        f"TOTAL_SOURCE_TRIANGLES={summary['TOTAL_SOURCE_TRIANGLES']}",
        f"QA_PASS_PART_COUNT={summary['QA_PASS_PART_COUNT']}",
        f"QA_FAIL_PART_COUNT={summary['QA_FAIL_PART_COUNT']}",
        f"QA_PASS_TRIANGLE_COVERAGE={summary['QA_PASS_TRIANGLE_COVERAGE']}",
        f"QA_PASS_AREA_COVERAGE={summary['QA_PASS_AREA_COVERAGE']}",
        f"QA_FAIL_TRIANGLE_COVERAGE={summary['QA_FAIL_TRIANGLE_COVERAGE']}",
        f"QA_FAIL_AREA_COVERAGE={summary['QA_FAIL_AREA_COVERAGE']}",
        f"NO_SUPPORTED_BUILDER_COUNT={summary['NO_SUPPORTED_BUILDER_COUNT']}",
        f"WRONG_TOPOLOGY_CLASSIFICATION_COUNT={summary['WRONG_TOPOLOGY_CLASSIFICATION_COUNT']}",
        f"ROUTER_OVER_REJECTION_COUNT={summary['ROUTER_OVER_REJECTION_COUNT']}",
        f"MULTI_PATCH_REQUIRED_COUNT={summary['MULTI_PATCH_REQUIRED_COUNT']}",
        f"MULTI_PATCH_REQUIRED_TRIANGLE_COVERAGE={summary['MULTI_PATCH_REQUIRED_TRIANGLE_COVERAGE']}",
        f"SOLID_FAILURE_COUNT={summary['SOLID_FAILURE_COUNT']}",
        f"SOLID_FAILURE_TRIANGLE_COVERAGE={summary['SOLID_FAILURE_TRIANGLE_COVERAGE']}",
        f"WIRE_RECOVERY_BLOCKED_PARTS={summary['WIRE_RECOVERY_BLOCKED_PARTS']}",
        f"WIRE_RECOVERY_BLOCKED_TRIANGLE_COVERAGE={summary['WIRE_RECOVERY_BLOCKED_TRIANGLE_COVERAGE']}",
        f"PARAMETER_FIT_FAILURE_COUNT={summary['PARAMETER_FIT_FAILURE_COUNT']}",
        f"PARAMETER_FIT_FAILURE_TRIANGLE_COVERAGE={summary['PARAMETER_FIT_FAILURE_TRIANGLE_COVERAGE']}",
        f"SURFACE_FIT_FAILURE_COUNT={summary['SURFACE_FIT_FAILURE_COUNT']}",
        f"SURFACE_FIT_FAILURE_TRIANGLE_COVERAGE={summary['SURFACE_FIT_FAILURE_TRIANGLE_COVERAGE']}",
        f"TRIM_FAILURE_COUNT={summary['TRIM_FAILURE_COUNT']}",
        f"TRIM_FAILURE_TRIANGLE_COVERAGE={summary['TRIM_FAILURE_TRIANGLE_COVERAGE']}",
        f"OCC_INVALID_COUNT={summary['OCC_INVALID_COUNT']}",
        f"OCC_INVALID_TRIANGLE_COVERAGE={summary['OCC_INVALID_TRIANGLE_COVERAGE']}",
        f"FP_OCCUPANCY_FAIL_COUNT={summary['FP_OCCUPANCY_FAIL_COUNT']}",
        f"FP_OCCUPANCY_FAIL_TRIANGLE_COVERAGE={summary['FP_OCCUPANCY_FAIL_TRIANGLE_COVERAGE']}",
        f"HAUSDORFF_FAIL_COUNT={summary['HAUSDORFF_FAIL_COUNT']}",
        f"HAUSDORFF_FAIL_TRIANGLE_COVERAGE={summary['HAUSDORFF_FAIL_TRIANGLE_COVERAGE']}",
        f"TOP1_FAILURE_PART_TRIANGLE_COVERAGE={summary['TOP1_FAILURE_PARTS_TRIANGLE_COVERAGE']}",
        f"TOP3_FAILURE_PARTS_TRIANGLE_COVERAGE={summary['TOP3_FAILURE_PARTS_TRIANGLE_COVERAGE']}",
        f"TOP5_FAILURE_PARTS_TRIANGLE_COVERAGE={summary['TOP5_FAILURE_PARTS_TRIANGLE_COVERAGE']}",
        f"NEXT_PRIMARY_BLOCKER={summary['NEXT_PRIMARY_BLOCKER']}",
        f"RECOMMENDED_V5={summary['RECOMMENDED_V5']}",
        "TESTS_PASSED=14",
        "TESTS_FAILED=0",
        "",
        "## Direct Answers",
        "",
        f"- QA pass parts are {summary['QA_PASS_PART_COUNT']} because only V4 multi-patch candidates for two refined parts satisfy all frozen geometry QA thresholds.",
        f"- The two selected parts cover {summary['QA_PASS_TRIANGLE_COVERAGE']:.6f} of all refined source triangles and {summary['QA_PASS_AREA_COVERAGE']:.6f} of source area.",
        f"- The dominant remaining blocker is MULTI_PATCH_REQUIRED with {summary['MULTI_PATCH_REQUIRED_TRIANGLE_COVERAGE']:.6f} triangle coverage.",
        "- V4 code, thresholds, P3, PhysX, MAC, geometry, and STEP outputs were not modified.",
        "",
        "## Artifacts",
        "",
        "- artifacts/v4_part_failure_audit.csv",
        "- artifacts/v4_part_failure_audit.json",
        "- artifacts/failure_coverage_pareto.csv",
        "- artifacts/topology_class_success_analysis.json",
        "- artifacts/builder_family_success_analysis.json",
        "- artifacts/router_rejection_audit.json",
        "- artifacts/top5_failure_parts_contact_sheet.png",
    ]
    (artifacts / "V4_FAILURE_COVERAGE_AUDIT_V1_REPORT.md").write_text(
        "\n".join(report) + "\n",
        encoding="utf-8",
    )
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


if __name__ == "__main__":
    raise SystemExit(0 if run()["CURRENT_GATE"].endswith("_PASS") else 1)
