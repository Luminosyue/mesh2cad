from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "mac_residual_feature_repair_v1" / "front_dorsal_focus_audit_v1"
GRAPH = ROOT / "case09_full_pipeline_fresh_e2e_v1" / "02_cad_part_graph" / "cad_part_graph.json"
MANIFEST = ROOT / "mac_residual_feature_repair_v1" / "final" / "CASE09_mac_residual_feature_repaired_manifest.json"


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(path, force="mesh", process=False)


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    return vector / max(norm, 1e-12)


def propeller_audit(prop: trimesh.Trimesh, fuselage: trimesh.Trimesh) -> dict[str, object]:
    components = sorted(prop.split(only_watertight=False), key=lambda item: -item.area)
    vertices = np.asarray(prop.vertices, dtype=float)
    values, vectors = np.linalg.eigh(np.cov(vertices - vertices.mean(axis=0), rowvar=False))
    axis = normalize(vectors[:, int(np.argmin(values))])
    centers = [np.asarray(part.centroid, dtype=float) for part in components]
    hub_center = np.mean(centers, axis=0)
    blade_rows: list[dict[str, object]] = []
    root_points: list[np.ndarray] = []
    for index, part in enumerate(components):
        points = np.asarray(part.vertices, dtype=float)
        offsets = points - hub_center
        axial = np.outer(offsets @ axis, axis)
        radial = np.linalg.norm(offsets - axial, axis=1)
        root = points[int(np.argmin(radial))]
        tip = points[int(np.argmax(radial))]
        root_points.append(root)
        blade_rows.append(
            {
                "component": index,
                "vertex_count": int(len(points)),
                "face_count": int(len(part.faces)),
                "bounds": part.bounds.tolist(),
                "watertight": bool(part.is_watertight),
                "root_nearest_to_hub": root.tolist(),
                "tip_farthest_from_hub": tip.tolist(),
                "root_radial_distance": float(np.min(radial)),
                "tip_radial_distance": float(np.max(radial)),
                "component_centroid": part.centroid.tolist(),
            }
        )

    fuselage_vertices = np.asarray(fuselage.vertices, dtype=float)
    fuselage_tree = cKDTree(fuselage_vertices)
    root_distances = fuselage_tree.query(np.asarray(root_points))[0]
    local_mask = np.linalg.norm(fuselage_vertices - hub_center, axis=1) <= 0.12
    local = fuselage_vertices[local_mask]
    if len(local):
        local_axis = (local - hub_center) @ axis
        local_radial = np.linalg.norm((local - hub_center) - np.outer(local_axis, axis), axis=1)
        local_summary = {
            "vertex_count": int(len(local)),
            "bounds": local.min(axis=0).tolist(),
            "max_radial_extent": float(local_radial.max()),
            "median_radial_extent": float(np.median(local_radial)),
            "axis_extent": [float(local_axis.min()), float(local_axis.max())],
        }
    else:
        local_summary = {
            "vertex_count": 0,
            "bounds": None,
            "max_radial_extent": None,
            "median_radial_extent": None,
            "axis_extent": None,
        }
    return {
        "schema": "FRONT_DORSAL_FOCUS_AUDIT_V1_PROPELLER",
        "component_count": len(components),
        "component_watertight": [bool(part.is_watertight) for part in components],
        "rotation_axis": axis.tolist(),
        "hub_center_inferred_from_blade_centroids": hub_center.tolist(),
        "blade_measurements": blade_rows,
        "blade_root_to_fuselage_surface_distance": root_distances.tolist(),
        "fuselage_local_parent_surface": local_summary,
        "hub_component_observed": False,
        "parent_surface_observed": bool(len(local) > 0 and np.min(root_distances) <= 0.01),
        "safe_standalone_hub_recovery": False,
        "decision": "PARENT_SURFACE_OBSERVED_BUT_HUB_NOT_INDEPENDENTLY_SEGMENTED",
    }


def dorsal_audit(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, object]:
    source_points = np.asarray(source.vertices, dtype=float)
    candidate_points = np.asarray(candidate.vertices, dtype=float)
    distances = cKDTree(candidate_points).query(source_points)[0]
    result: dict[str, object] = {
        "schema": "FRONT_DORSAL_FOCUS_AUDIT_V1_DORSAL",
        "source_bounds": source.bounds.tolist(),
        "candidate_bounds": candidate.bounds.tolist(),
        "source_vertex_count": int(len(source.vertices)),
        "candidate_vertex_count": int(len(candidate.vertices)),
        "distance_quantiles": {
            str(q): float(np.quantile(distances, q))
            for q in (0.5, 0.75, 0.9, 0.95, 0.99, 1.0)
        },
    }
    for quantile in (0.90, 0.95, 0.98):
        selected = distances >= np.quantile(distances, quantile)
        points = source_points[selected]
        result[f"residual_q{int(quantile * 100)}"] = {
            "vertex_count": int(len(points)),
            "bounds": points.min(axis=0).tolist() if len(points) else None,
            "centroid": points.mean(axis=0).tolist() if len(points) else None,
        }
    result["decision"] = "LOCAL_DORSAL_RESIDUAL_REMAINS"
    return result


def camera_basis(azimuth_deg: float = 40.0, elevation_deg: float = 25.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
    forward = normalize(np.array([math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)]))
    right = normalize(np.cross(forward, np.array([0.0, 0.0, 1.0])))
    up = normalize(np.cross(right, forward))
    return right, up, forward


def project(vertices: np.ndarray, center: np.ndarray, scale: float, size: int) -> np.ndarray:
    right, up, forward = camera_basis()
    relative = vertices - center
    x = relative @ right
    y = relative @ up
    depth = relative @ forward
    perspective = 1.0 / np.maximum(1.0 + depth / max(scale * 2.5, 1e-9), 0.25)
    px = size * 0.5 + x / max(scale, 1e-9) * size * 0.78 * perspective
    py = size * 0.5 - y / max(scale, 1e-9) * size * 0.78 * perspective
    return np.column_stack((px, py))


def render_mesh(mesh: trimesh.Trimesh, output: Path, title: str, *, heat: np.ndarray | None = None, crop_bounds: np.ndarray | None = None) -> None:
    if crop_bounds is None:
        crop_bounds = mesh.bounds
    center = (crop_bounds[0] + crop_bounds[1]) * 0.5
    scale = float(np.linalg.norm(crop_bounds[1] - crop_bounds[0]))
    size = 900
    image = Image.new("RGB", (size, size + 42), "white")
    draw = ImageDraw.Draw(image)
    projected = project(np.asarray(mesh.vertices), center, max(scale, 1e-9), size)
    face_depth = np.asarray(mesh.triangles_center) @ camera_basis()[2]
    order = np.argsort(face_depth)
    normals = np.asarray(mesh.face_normals)
    light = normalize(np.array([0.35, -0.45, 0.82]))
    if heat is not None:
        heat = np.asarray(heat)
        hmin, hmax = float(heat.min()), float(heat.max())
    for face_index in order:
        face = np.asarray(mesh.faces[face_index], dtype=int)
        shade = 0.43 + 0.57 * max(float(np.dot(normals[face_index], light)), 0.0)
        if heat is None:
            base = np.array([184.0, 201.0, 221.0])
        else:
            value = float(np.clip((heat[face_index] - hmin) / max(hmax - hmin, 1e-12), 0.0, 1.0))
            base = np.array([255.0 * value, 120.0 * (1.0 - value), 70.0])
        color = tuple(int(np.clip(channel * shade, 0, 255)) for channel in base)
        polygon = [tuple(int(round(value)) for value in projected[index]) for index in face]
        draw.polygon(polygon, fill=color)
    draw.rectangle((0, size, size, size + 42), fill="white")
    draw.text((14, size + 12), title, fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def contact(images: list[Path], output: Path, labels: list[str]) -> None:
    canvas = Image.new("RGB", (900 * len(images), 942), "white")
    for index, image_path in enumerate(images):
        image = Image.open(image_path).convert("RGB")
        canvas.paste(image, (index * 900, 0))
    draw = ImageDraw.Draw(canvas)
    for index, label in enumerate(labels):
        draw.text((index * 900 + 16, 910), label, fill="black")
    canvas.save(output)


def main() -> None:
    sys.path.insert(0, str(ROOT))
    from remote_gate10.gate10_runner import shape_mesh

    graph = json.loads(GRAPH.read_text())
    paths = {node["semantic_role"]: Path(node["source_part_mesh"]) for node in graph["nodes"]}
    manifest = json.loads(MANIFEST.read_text())
    dorsal_step = Path(next(item["selected_step_path"] for item in manifest["components"] if item["semantic_role"] == "DORSAL_FEATURES"))
    fuselage_step = Path(next(item["selected_step_path"] for item in manifest["components"] if item["semantic_role"] == "FUSELAGE"))
    prop = load_mesh(paths["PROPELLER_PATTERN"])
    fuselage = load_mesh(paths["FUSELAGE"])
    dorsal_source = load_mesh(paths["DORSAL_FEATURES"])
    dorsal_candidate = shape_mesh(dorsal_step)
    fuselage_candidate = shape_mesh(fuselage_step)

    prop_result = propeller_audit(prop, fuselage)
    dorsal_result = dorsal_audit(dorsal_source, dorsal_candidate)
    result = {
        "schema": "FRONT_DORSAL_FOCUS_AUDIT_V1",
        "CURRENT_GATE": "FRONT_DORSAL_FOCUS_AUDIT_V1",
        "PROP_PARENT_AUDIT": prop_result,
        "DORSAL_AUDIT": dorsal_result,
        "FROZEN_BASE_READ_ONLY": True,
        "BLADE_ONLY_RECOVERY_AUTHORIZED": False,
        "HUB_SOURCE_RECOVERY_AUTHORIZED": False,
        "DORSAL_BASE_MODIFIED": False,
    }
    dump(OUT / "artifacts/front_dorsal_focus_audit.json", result)
    dump(OUT / "artifacts/propeller_parent_audit.json", prop_result)
    dump(OUT / "artifacts/dorsal_local_audit.json", dorsal_result)

    prop_bounds = np.array([[-0.40, -1.00, -0.10], [0.04, -0.83, 0.13]], dtype=float)
    render_mesh(prop, OUT / "artifacts/propeller_source_closeup.png", "PROPELLER SOURCE PART", crop_bounds=prop_bounds)
    combined = trimesh.util.concatenate([prop, fuselage_candidate])
    render_mesh(combined, OUT / "artifacts/propeller_parent_overlay.png", "PROPELLER + FUSELAGE PARENT", crop_bounds=prop_bounds)

    dorsal_bounds = np.array([[-0.11, -0.80, 0.03], [0.12, 0.12, 0.22]], dtype=float)
    distances = cKDTree(np.asarray(dorsal_candidate.vertices)).query(np.asarray(dorsal_source.vertices))[0]
    face_heat = distances[np.asarray(dorsal_source.faces)].mean(axis=1)
    render_mesh(dorsal_source, OUT / "artifacts/dorsal_source_closeup.png", "DORSAL SOURCE PART", crop_bounds=dorsal_bounds)
    render_mesh(dorsal_candidate, OUT / "artifacts/dorsal_candidate_closeup.png", "DORSAL CURRENT CANDIDATE", crop_bounds=dorsal_bounds)
    render_mesh(dorsal_source, OUT / "artifacts/dorsal_residual_heatmap.png", "DORSAL SOURCE RESIDUAL HEATMAP", heat=face_heat, crop_bounds=dorsal_bounds)
    contact(
        [
            OUT / "artifacts/dorsal_source_closeup.png",
            OUT / "artifacts/dorsal_candidate_closeup.png",
            OUT / "artifacts/dorsal_residual_heatmap.png",
        ],
        OUT / "artifacts/dorsal_focus_comparison.png",
        ["SOURCE", "CURRENT", "RESIDUAL"],
    )
    report = [
        "# FRONT_DORSAL_FOCUS_AUDIT_V1",
        "",
        "The audit is read-only over the frozen Base BRep and current source Part Meshes.",
        "",
        f"- Propeller components: {prop_result['component_count']}",
        f"- Parent surface observed at blade roots: {prop_result['parent_surface_observed']}",
        f"- Independent hub component observed: {prop_result['hub_component_observed']}",
        f"- Safe standalone hub recovery: {prop_result['safe_standalone_hub_recovery']}",
        f"- Dorsal decision: {dorsal_result['decision']}",
        "",
        "No Propeller or Dorsal geometry was selected or modified by this audit.",
    ]
    (OUT / "artifacts/FRONT_DORSAL_FOCUS_AUDIT_V1_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
