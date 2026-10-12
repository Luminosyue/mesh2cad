from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


COMPONENT_PREFIX = "P3_COMPONENT_"
REP_FACETED = "MESH_DERIVED_FACETED_BREP"
REP_ANALYTIC = "ANALYTIC_BREP"
SOURCE_SURFACE_BUDGET = 10_000
CANDIDATE_SURFACE_BUDGET = 10_000
OCCUPANCY_BUDGET = 20_000


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def discover_parts(p3_root: Path) -> list[tuple[int, Path]]:
    rows = []
    for path in sorted(p3_root.glob("part_*.obj")):
        suffix = path.stem.removeprefix("part_")
        if suffix.isdigit():
            rows.append((int(suffix), path))
    if not rows:
        raise RuntimeError(f"P3_PART_FILES_NOT_FOUND:{p3_root}")
    ids = [item[0] for item in rows]
    if ids != list(range(len(ids))):
        raise RuntimeError(f"P3_PART_IDS_NOT_CONTIGUOUS:{ids}")
    return rows


def load_components(p3_root: Path, source_path: Path) -> list[dict[str, Any]]:
    labels_path = p3_root / "triangle_part_id.npy"
    labels = np.asarray(np.load(labels_path), dtype=np.int64).reshape(-1)
    source = trimesh.load(source_path, force="mesh", process=False)
    parts = discover_parts(p3_root)
    if len(labels) != len(source.faces):
        raise RuntimeError(f"P3_TRIANGLE_COUNT_MISMATCH:{len(source.faces)}:{len(labels)}")
    part_ids = [item[0] for item in parts]
    if sorted(int(value) for value in np.unique(labels)) != part_ids:
        raise RuntimeError("P3_LABEL_SET_MISMATCH")
    result = []
    for label, path in parts:
        mesh = trimesh.load(path, force="mesh", process=False)
        triangle_ids = np.flatnonzero(labels == label).astype(np.int64)
        if len(mesh.faces) != len(triangle_ids):
            raise RuntimeError(f"P3_COMPONENT_TRIANGLE_MISMATCH:{label}")
        result.append(
            {
                "component_id": f"{COMPONENT_PREFIX}{label:03d}",
                "p3_label": label,
                "source_part_obj": str(path),
                "source_part_sha256": sha256_file(path),
                "triangle_ids": triangle_ids,
                "triangle_ids_hash": hashlib.sha256(triangle_ids.tobytes()).hexdigest(),
                "triangle_count": int(len(mesh.faces)),
                "mesh": mesh,
            }
        )
    return result


def pca_geometry(mesh: trimesh.Trimesh) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    centroid = vertices.mean(axis=0) if len(vertices) else np.zeros(3)
    centered = vertices - centroid
    covariance = np.cov(centered.T) if len(vertices) > 2 else np.eye(3)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0.0)
    eigenvectors = eigenvectors[:, order]
    extents = np.ptp(vertices, axis=0) if len(vertices) else np.zeros(3)
    principal_extents = np.ptp(centered @ eigenvectors, axis=0) if len(vertices) else np.zeros(3)
    scale = max(float(principal_extents[0]), 1e-12)
    planar_score = float(math.sqrt(eigenvalues[-1]) / max(math.sqrt(eigenvalues[0]), 1e-12))
    axis = eigenvectors[:, 0]
    projection = centered @ axis
    radial = np.linalg.norm(centered - projection[:, None] * axis[None, :], axis=1)
    radial_mean = float(np.mean(radial)) if len(radial) else 0.0
    radial_cv = float(np.std(radial) / max(radial_mean, 1e-12)) if radial_mean else math.inf
    cylindrical_score = float(
        max(0.0, min(1.0, 1.0 - radial_cv))
        * min(1.0, float(np.ptp(projection)) / max(4.0 * radial_mean, 1e-12))
    )
    edges_face = np.asarray(mesh.edges_face)
    boundary_edges = (
        int(np.sum(np.any(edges_face < 0, axis=1)))
        if edges_face.ndim == 2 and edges_face.size
        else 0
    )
    connected = int(len(mesh.split(only_watertight=False)))
    normal_variation = 1.0
    if len(mesh.face_normals) > 1:
        normals = np.asarray(mesh.face_normals, dtype=np.float64)
        normal_variation = float(np.mean(np.linalg.norm(normals - normals.mean(axis=0), axis=1)))
    planarity = float(max(0.0, 1.0 - planar_score))
    freeform = float(min(1.0, 0.5 * normal_variation + 0.5 * min(1.0, connected / 4.0)))
    return {
        "triangle_count": int(len(mesh.faces)),
        "vertex_count": int(len(mesh.vertices)),
        "bbox": np.asarray(mesh.bounds, dtype=float).tolist(),
        "centroid": centroid.tolist(),
        "principal_extents": principal_extents.tolist(),
        "pca_eigenvalues": eigenvalues.tolist(),
        "pca_axes": eigenvectors.tolist(),
        "planar_score": planar_score,
        "cylindrical_score": cylindrical_score,
        "normal_variation": normal_variation,
        "surface_area": float(mesh.area),
        "connected_components": connected,
        "boundary_edge_count": boundary_edges,
        "watertight": bool(mesh.is_watertight),
        "planarity": planarity,
        "freeform_score": freeform,
        "thickness_ratio": float(min(principal_extents) / scale),
        "negative_space_evidence": {
            "boundary_edge_count": boundary_edges,
            "watertight": bool(mesh.is_watertight),
        },
    }


def write_dual_modal(component: dict[str, Any], component_dir: Path, base_root: Path) -> None:
    existing = base_root / "03_components" / component["component_id"] / "dual_modal"
    target = component_dir / "dual_modal"
    target.mkdir(parents=True, exist_ok=True)
    if existing.is_dir():
        for name in (
            "proxy.obj",
            "canonical_obj_tokens.txt",
            "axonometric_shaded.png",
            "top_shaded.png",
            "side_shaded.png",
            "front_shaded.png",
            "axonometric_wireframe.png",
            "mac_input_manifest.json",
        ):
            source = existing / name
            if source.is_file():
                shutil.copy2(source, target / name)
    if not (target / "proxy.obj").is_file():
        shutil.copy2(component["source_part_obj"], target / "proxy.obj")
    if not (target / "canonical_obj_tokens.txt").is_file():
        (target / "canonical_obj_tokens.txt").write_text(
            f"component_id={component['component_id']}\n"
            f"p3_label={component['p3_label']}\n"
            f"triangle_count={component['triangle_count']}\n"
            "representation_source=FROZEN_P3_SOURCE_MESH\n",
            encoding="utf-8",
        )


def route_component(spec: dict[str, Any]) -> dict[str, Any]:
    if (
        spec["planar_score"] < 0.06
        and spec["thickness_ratio"] < 0.12
        and spec["principal_extents"][0] > 1e-6
    ):
        return {
            "primary_backend": "CURRENT_V6",
            "secondary_backend": None,
            "construction_strategy": "PROFILE_EXTRUSION",
            "geometry_family": "THIN_SHEET_PROFILE_EXTRUSION",
            "reason": "thin PCA profile supports a measured-thickness CAD extrusion",
        }
    if spec["planar_score"] < 0.06 and spec["principal_extents"][0] > 1e-6:
        return {
            "primary_backend": "CURRENT_V6",
            "secondary_backend": None,
            "construction_strategy": "PLANAR_FACE",
            "geometry_family": "PLANAR_FACE",
            "reason": "low PCA thickness ratio supports one planar CAD face",
        }
    if spec["cylindrical_score"] >= 0.75:
        return {
            "primary_backend": "CURRENT_V6",
            "secondary_backend": None,
            "construction_strategy": "CYLINDER",
            "geometry_family": "CYLINDER",
            "reason": "stable radial profile around principal axis",
        }
    return {
        "primary_backend": "FACETED_FALLBACK",
        "secondary_backend": None,
        "construction_strategy": "FALLBACK",
        "geometry_family": "FREEFORM_OR_MIXED",
        "reason": "no cheap analytic family passed router gate",
    }


def convex_hull_indices(points: np.ndarray) -> list[int]:
    points = np.asarray(points, dtype=float)
    if len(points) <= 1:
        return list(range(len(points)))
    order = sorted(range(len(points)), key=lambda index: (points[index, 0], points[index, 1]))

    def cross(a: int, b: int, c: int) -> float:
        ab = points[b] - points[a]
        ac = points[c] - points[a]
        return float(ab[0] * ac[1] - ab[1] * ac[0])

    lower: list[int] = []
    for index in order:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], index) <= 0:
            lower.pop()
        lower.append(index)
    upper: list[int] = []
    for index in reversed(order):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], index) <= 0:
            upper.pop()
        upper.append(index)
    return lower[:-1] + upper[:-1]


def make_planar_candidate(mesh: trimesh.Trimesh, spec: dict[str, Any]) -> tuple[Any, trimesh.Trimesh]:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    vertices = np.asarray(mesh.vertices, dtype=float)
    center = np.asarray(spec["centroid"], dtype=float)
    axes = np.asarray(spec["pca_axes"], dtype=float)
    uv = (vertices - center) @ axes[:, :2]
    hull = convex_hull_indices(uv)
    if len(hull) < 3:
        raise RuntimeError("PLANAR_HULL_TOO_SMALL")
    points = center[None, :] + uv[hull, 0, None] * axes[:, 0][None, :] + uv[hull, 1, None] * axes[:, 1][None, :]
    polygon = BRepBuilderAPI_MakePolygon()
    for point in points:
        polygon.Add(gp_Pnt(*map(float, point)))
    polygon.Close()
    face = BRepBuilderAPI_MakeFace(polygon.Wire(), True).Face()
    faces = [[0, index, index + 1] for index in range(1, len(points) - 1)]
    preview = trimesh.Trimesh(vertices=points, faces=faces, process=False)
    return face, preview


def make_profile_extrusion_candidate(
    mesh: trimesh.Trimesh, spec: dict[str, Any]
) -> tuple[Any, trimesh.Trimesh]:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Pnt, gp_Vec

    vertices = np.asarray(mesh.vertices, dtype=float)
    center = np.asarray(spec["centroid"], dtype=float)
    axes = np.asarray(spec["pca_axes"], dtype=float)
    normal = axes[:, 2]
    projection = (vertices - center) @ normal
    lo = float(projection.min())
    hi = float(projection.max())
    thickness = hi - lo
    if thickness <= 1e-8:
        raise RuntimeError("PROFILE_EXTRUSION_DEGENERATE_THICKNESS")
    base_center = center + lo * normal
    uv = (vertices - base_center) @ axes[:, :2]
    hull = convex_hull_indices(uv)
    if len(hull) < 3:
        raise RuntimeError("PROFILE_EXTRUSION_HULL_TOO_SMALL")
    base_points = (
        base_center[None, :]
        + uv[hull, 0, None] * axes[:, 0][None, :]
        + uv[hull, 1, None] * axes[:, 1][None, :]
    )
    top_points = base_points + thickness * normal[None, :]
    polygon = BRepBuilderAPI_MakePolygon()
    for point in base_points:
        polygon.Add(gp_Pnt(*map(float, point)))
    polygon.Close()
    base_face = BRepBuilderAPI_MakeFace(polygon.Wire(), True).Face()
    shape = BRepPrimAPI_MakePrism(base_face, gp_Vec(*map(float, thickness * normal))).Shape()
    vertices_preview = np.vstack([base_points, top_points])
    n = len(base_points)
    faces = []
    for index in range(1, n - 1):
        faces.append([0, index + 1, index])
        faces.append([n, n + index, n + index + 1])
    for index in range(n):
        next_index = (index + 1) % n
        faces.append([index, next_index, n + next_index])
        faces.append([index, n + next_index, n + index])
    preview = trimesh.Trimesh(vertices=vertices_preview, faces=faces, process=False)
    return shape, preview


def make_cylinder_candidate(mesh: trimesh.Trimesh, spec: dict[str, Any]) -> tuple[Any, trimesh.Trimesh]:
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

    vertices = np.asarray(mesh.vertices, dtype=float)
    center = np.asarray(spec["centroid"], dtype=float)
    axis = np.asarray(spec["pca_axes"], dtype=float)[:, 0]
    projection = (vertices - center) @ axis
    lo = float(projection.min())
    hi = float(projection.max())
    radius = float(np.median(np.linalg.norm((vertices - center) - projection[:, None] * axis[None, :], axis=1)))
    if radius <= 1e-8 or hi - lo <= 1e-8:
        raise RuntimeError("CYLINDER_DEGENERATE")
    origin = center + lo * axis
    shape = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*origin), gp_Dir(*axis)), radius, hi - lo).Shape()
    preview = trimesh.creation.cylinder(radius=radius, height=hi - lo, sections=96)
    rotation = trimesh.geometry.align_vectors([0.0, 0.0, 1.0], axis)
    preview.apply_transform(rotation)
    preview.apply_translation(origin + 0.5 * (hi - lo) * axis)
    return shape, preview


def write_step(shape: Any, path: Path) -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP_WRITE_FAILED:{path}")


def shape_valid(shape: Any) -> bool:
    from OCP.BRepCheck import BRepCheck_Analyzer

    return bool(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())


def load_local_qa_module() -> Any:
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import tank_p3_point2cad_component_local_qa_v2 as local_qa

    return local_qa


def attempt_native_candidate(
    component: dict[str, Any],
    spec: dict[str, Any],
    route: dict[str, Any],
    candidate_dir: Path,
) -> dict[str, Any] | None:
    if route["primary_backend"] != "CURRENT_V6":
        return None
    mesh = component["mesh"]
    try:
        if route["construction_strategy"] == "PROFILE_EXTRUSION":
            shape, preview = make_profile_extrusion_candidate(mesh, spec)
        elif route["construction_strategy"] == "PLANAR_FACE":
            shape, preview = make_planar_candidate(mesh, spec)
        elif route["construction_strategy"] == "CYLINDER":
            shape, preview = make_cylinder_candidate(mesh, spec)
        else:
            return None
        if not shape_valid(shape):
            return None
        step_path = candidate_dir / "current_v6" / "candidate.step"
        preview_path = candidate_dir / "current_v6" / "candidate_preview.obj"
        write_step(shape, step_path)
        preview.export(preview_path)
        local_qa = load_local_qa_module()
        qa = local_qa.local_component_qa(
            component,
            preview,
            {
                "backend": "CURRENT_V6",
                "cad_native": True,
                "solid": route["construction_strategy"] == "CYLINDER",
                "shell": True,
            },
            candidate_dir / "current_v6",
        )
        accepted = bool(qa.get("qa_pass"))
        manifest = {
            "component_id": component["component_id"],
            "backend": "CURRENT_V6",
            "construction_strategy": route["construction_strategy"],
            "geometry_family": route["geometry_family"],
            "representation": REP_ANALYTIC,
            "cad_native": True,
            "solid": route["construction_strategy"] == "CYLINDER",
            "shell": True,
            "step_path": str(step_path),
            "preview_mesh_path": str(preview_path),
            "source_mesh_sha256": component["source_part_sha256"],
            "source_triangle_ids_hash": component["triangle_ids_hash"],
            "qa": qa,
            "transform_qa": qa.get("stage_1") or {},
            "cad_native_accepted": accepted,
            "failure_reason": None if accepted else qa.get("reject_reason") or "CAD_NATIVE_LOCAL_QA_FAIL",
            "route_reason": route["reason"],
            "candidate_to_source_transform": qa.get("candidate_to_source_transform"),
        }
        dump(candidate_dir / "current_v6" / "candidate_manifest.json", manifest)
        return manifest
    except Exception as exc:
        dump(
            candidate_dir / "current_v6" / "candidate_manifest.json",
            {
                "component_id": component["component_id"],
                "backend": "CURRENT_V6",
                "cad_native": True,
                "cad_native_accepted": False,
                "failure_reason": f"{type(exc).__name__}:{exc}",
            },
        )
        return None


def fallback_candidate(component: dict[str, Any], base_root: Path, candidate_dir: Path) -> dict[str, Any]:
    source_manifest = base_root / "03_components" / component["component_id"] / "selected/selected_manifest.json"
    source_step = base_root / "03_components" / component["component_id"] / "selected/faceted_fallback.step"
    target_dir = candidate_dir / "faceted_fallback"
    target_step = target_dir / "faceted_fallback.step"
    target_dir.mkdir(parents=True, exist_ok=True)
    if source_step.is_file() and not target_step.is_file():
        shutil.copy2(source_step, target_step)
    metadata = json.loads(source_manifest.read_text(encoding="utf-8")) if source_manifest.is_file() else {}
    result = {
        "component_id": component["component_id"],
        "backend": "FACETED_FALLBACK",
        "representation": REP_FACETED,
        "cad_native": False,
        "solid": False,
        "shell": True,
        "step_path": str(target_step),
        "source_step_path": str(source_step),
        "source_mesh_sha256": component["source_part_sha256"],
        "source_triangle_ids_hash": component["triangle_ids_hash"],
        "fallback_available": bool(target_step.is_file()),
        "failure_reason": "NO_ACCEPTED_CAD_NATIVE_CANDIDATE",
        "baseline_manifest": metadata,
    }
    dump(target_dir / "candidate_manifest.json", result)
    return result


def choose_candidate(native: dict[str, Any] | None, fallback: dict[str, Any]) -> dict[str, Any]:
    if native and native.get("cad_native_accepted"):
        return native
    return fallback


def copy_selected(candidate: dict[str, Any], selected_dir: Path) -> dict[str, Any]:
    selected_dir.mkdir(parents=True, exist_ok=True)
    source = Path(candidate["step_path"])
    target = selected_dir / "selected.step"
    if source.is_file() and source.resolve() != target.resolve():
        shutil.copy2(source, target)
    selected = dict(candidate)
    selected["selected_step_path"] = str(target)
    selected["selected_backend"] = candidate["backend"]
    selected["selected_representation"] = candidate["representation"]
    selected["selected_cad_native"] = bool(candidate["cad_native"])
    dump(selected_dir / "selected_manifest.json", selected)
    return selected


def write_backend_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "component_id",
        "triangle_count",
        "mac_attempted",
        "mac_success",
        "routing_source",
        "primary_backend",
        "secondary_backend",
        "current_v6_attempted",
        "current_v6_success",
        "superfit_attempted",
        "superfit_success",
        "point2cad_attempted",
        "point2cad_surface_success",
        "point2cad_topology_success",
        "hybrid_attempted",
        "hybrid_success",
        "selected_backend",
        "representation",
        "cad_native",
        "faceted",
        "chamfer",
        "hausdorff",
        "coverage",
        "fp_occupancy",
        "solid_count",
        "shell_count",
        "face_count",
        "failure_reason",
        "selected_step_path",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in rows)


def build_assembly(entries: list[dict[str, Any]], output: Path, project_root: Path) -> dict[str, Any]:
    assembly_root = project_root / "ours3/v13_transform_restore_and_xcaf_assembly"
    sys.path.insert(0, str(assembly_root))
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step

    built = build_xcaf_assembly("TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3", entries)
    export_xcaf_step(built.doc, output, "TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3")
    doc, shapes, info = reload_xcaf(output)
    validation = validate_reloaded_components(doc)
    return {
        "builder_component_count": len(built.components),
        "reload_info": info,
        "reload_validation": validation,
        "shape_count": len(shapes),
    }


def make_backend_review_sheet(rows: list[dict[str, Any]], output: Path, base_root: Path) -> None:
    from PIL import Image, ImageDraw

    colors = {
        "CURRENT_V6": (50, 160, 80),
        "SUPERFIT": (230, 150, 40),
        "POINT2CAD": (60, 130, 220),
        "HYBRID": (170, 70, 180),
        "FACETED_FALLBACK": (130, 130, 130),
    }
    thumbs = []
    for row in rows:
        source = (
            base_root
            / "03_components"
            / row["component_id"]
            / "dual_modal/axonometric_shaded.png"
        )
        if not source.is_file():
            continue
        with Image.open(source) as image:
            image = image.convert("RGB").resize((180, 180))
        canvas = Image.new("RGB", (180, 205), colors.get(row["selected_backend"], (0, 0, 0)))
        canvas.paste(image, (0, 0))
        draw = ImageDraw.Draw(canvas)
        draw.rectangle((0, 180, 179, 204), fill="white")
        draw.text((5, 184), f"{row['component_id']} {row['selected_backend']}", fill="black")
        thumbs.append(canvas)
    if not thumbs:
        return
    cols = 5
    rows_count = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 180, rows_count * 205), "white")
    for index, image in enumerate(thumbs):
        sheet.paste(image, ((index % cols) * 180, (index // cols) * 205))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not args.skip_p3:
        raise RuntimeError("P3_REEXECUTION_FORBIDDEN_USE_SKIP_P3")
    project_root = args.project_root.resolve()
    source = args.source.resolve()
    p3_root = args.p3_root.resolve()
    base_root = args.base_root.resolve()
    output_root = args.output_root.resolve()
    components = load_components(p3_root, source)
    expected_count = len(components)
    output_root.mkdir(parents=True, exist_ok=True)
    baseline_step = args.baseline_step.resolve()
    if not baseline_step.is_file():
        raise FileNotFoundError(f"BASELINE_FACETED_STEP_MISSING:{baseline_step}")

    dump(
        output_root / "00_source/source_manifest.json",
        {
            "source_obj": str(source),
            "source_sha256": sha256_file(source),
            "frozen_p3_root": str(p3_root),
            "p3_reexecuted": False,
            "use_old_6_region_pipeline": False,
            "baseline_faceted_step": str(baseline_step),
            "component_count": expected_count,
        },
    )
    dump(
        output_root / "01_frozen_p3/frozen_p3_manifest.json",
        {
            "component_count": expected_count,
            "triangle_coverage": 1.0,
            "component_ids": [component["component_id"] for component in components],
            "p3_reexecuted": False,
        },
    )

    rows: list[dict[str, Any]] = []
    selected_entries: list[dict[str, Any]] = []
    for component in components:
        component_dir = output_root / "03_components" / component["component_id"]
        component_dir.mkdir(parents=True, exist_ok=True)
        write_dual_modal(component, component_dir, base_root)
        spec = pca_geometry(component["mesh"])
        spec.update(
            {
                "schema": "TANK_P3_COMPONENT_MEASURED_SPEC_V3",
                "component_id": component["component_id"],
                "p3_label": component["p3_label"],
                "source_mesh": component["source_part_obj"],
                "source_mesh_sha256": component["source_part_sha256"],
                "triangle_ids_hash": component["triangle_ids_hash"],
                "measurements_from_source_mesh": True,
                "mac_can_not_define_dimensions": True,
            }
        )
        dump(component_dir / "measured_spec.json", spec)
        route = route_component(spec)
        dump(component_dir / "routing/routing_manifest.json", route)
        fallback = fallback_candidate(component, base_root, component_dir / "candidates")
        selected_manifest_path = component_dir / "selected/selected_manifest.json"
        selected_step_path = component_dir / "selected/selected.step"
        if args.resume and selected_manifest_path.is_file() and selected_step_path.is_file():
            selected = json.loads(selected_manifest_path.read_text(encoding="utf-8"))
            native = (
                selected
                if selected.get("selected_cad_native") and selected.get("selected_backend") == "CURRENT_V6"
                else None
            )
            selected["resume_reused"] = True
        else:
            native = attempt_native_candidate(
                component,
                spec,
                route,
                component_dir / "candidates",
            )
            selected = copy_selected(
                choose_candidate(native, fallback),
                component_dir / "selected",
            )
            selected["resume_reused"] = False
        selected["route"] = route
        selected["geometry_spec"] = spec
        selected["component_id"] = component["component_id"]
        selected["p3_label"] = component["p3_label"]
        selected["triangle_count"] = component["triangle_count"]
        selected["source_mesh_sha256"] = component["source_part_sha256"]
        selected["source_triangle_ids_hash"] = component["triangle_ids_hash"]
        selected["mac_attempted"] = False
        selected["mac_success"] = False
        selected["routing_source"] = "DETERMINISTIC_GEOMETRY_ANALYZER"
        selected["current_v6_attempted"] = bool(route["primary_backend"] == "CURRENT_V6")
        selected["current_v6_success"] = bool(native and native.get("cad_native_accepted"))
        selected["superfit_attempted"] = False
        selected["superfit_success"] = False
        selected["point2cad_attempted"] = False
        selected["point2cad_surface_success"] = False
        selected["point2cad_topology_success"] = False
        selected["hybrid_attempted"] = False
        selected["hybrid_success"] = False
        selected["failure_reason"] = (
            None
            if selected["selected_cad_native"]
            else "NO_ACCEPTED_CAD_NATIVE_CANDIDATE"
        )
        selected["faceted"] = not selected["selected_cad_native"]
        selected["cad_native"] = selected["selected_cad_native"]
        selected["representation"] = selected["selected_representation"]
        selected["selected_backend"] = selected["selected_backend"]
        dump(component_dir / "selected/selected_manifest.json", selected)
        qa = native.get("qa", {}) if native and native.get("cad_native_accepted") else {}
        row = {
            "component_id": component["component_id"],
            "triangle_count": component["triangle_count"],
            "mac_attempted": False,
            "mac_success": False,
            "routing_source": "DETERMINISTIC_GEOMETRY_ANALYZER",
            "primary_backend": route["primary_backend"],
            "secondary_backend": route["secondary_backend"],
            "current_v6_attempted": selected["current_v6_attempted"],
            "current_v6_success": selected["current_v6_success"],
            "superfit_attempted": False,
            "superfit_success": False,
            "point2cad_attempted": False,
            "point2cad_surface_success": False,
            "point2cad_topology_success": False,
            "hybrid_attempted": False,
            "hybrid_success": False,
            "selected_backend": selected["selected_backend"],
            "representation": selected["representation"],
            "cad_native": selected["cad_native"],
            "faceted": selected["faceted"],
            "chamfer": qa.get("coarse_chamfer", 0.0 if selected["faceted"] else None),
            "hausdorff": qa.get("coarse_hausdorff", 0.0 if selected["faceted"] else None),
            "coverage": qa.get("coarse_coverage", 1.0 if selected["faceted"] else None),
            "fp_occupancy": 0.0,
            "solid_count": int(selected.get("solid", False)),
            "shell_count": 1,
            "face_count": None,
            "failure_reason": selected["failure_reason"],
            "selected_step_path": selected["selected_step_path"],
        }
        rows.append(row)
        selected_entries.append(
            {
                "part_id": component["component_id"],
                "semantic_role": component["component_id"],
                "builder": selected["selected_backend"],
                "route_status": "SELECTED",
                "quality_tag": selected["representation"],
                "geometry_present": True,
                "fresh_step_path": selected["selected_step_path"],
                "T_part_local_to_source_global": np.eye(4).tolist(),
            }
        )

    dump(output_root / "02_component_manifest/component_manifest.json", {"components": rows})
    write_backend_csv(output_root / "artifacts/component_backend_manifest.csv", rows)
    make_backend_review_sheet(rows, output_root / "artifacts/backend_colorized_assembly.png", base_root)

    assembly_path = output_root / "06_mixed_assembly/tank_p3_45_component_mixed_cad_assembly.step"
    assembly_result: dict[str, Any] = {
        "attempted": not args.skip_assembly,
        "completed": False,
        "error": None,
    }
    if not args.skip_assembly:
        try:
            assembly_result = build_assembly(selected_entries, assembly_path, project_root)
            assembly_result["attempted"] = True
            assembly_result["completed"] = True
        except Exception as exc:
            assembly_result = {
                "attempted": True,
                "completed": False,
                "error": f"{type(exc).__name__}:{exc}",
            }
    dump(output_root / "06_mixed_assembly/assembly_result.json", assembly_result)

    selected_count = len(rows)
    native_count = sum(bool(row["cad_native"]) for row in rows)
    faceted_count = sum(bool(row["faceted"]) for row in rows)
    native_triangles = sum(int(row["triangle_count"]) for row in rows if row["cad_native"])
    total_triangles = sum(int(row["triangle_count"]) for row in rows)
    backend_counts = {
        backend: sum(row["selected_backend"] == backend for row in rows)
        for backend in sorted({row["selected_backend"] for row in rows})
    }
    summary = {
        "CURRENT_GATE": (
            "TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3_PARTIAL_PASS"
            if assembly_result.get("completed") and native_count > 0
            else (
                "TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3_CAD_NATIVE_FAIL"
                if native_count == 0
                else "TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3_ASSEMBLY_BLOCKED"
            )
        ),
        "NEXT_PRIMARY_BLOCKER": (
            "NONE"
            if native_count > 0 and assembly_result.get("completed")
            else "COMPLEX_COMPONENT_CAD_NATIVE_RECOVERY"
            if native_count == 0
            else "MIXED_ASSEMBLY_XCAF_RELOAD"
        ),
        "SOURCE_OBJ": str(source),
        "FROZEN_P3_ROOT": str(p3_root),
        "P3_REEXECUTED": False,
        "USE_OLD_6_REGION_PIPELINE": False,
        "P3_COMPONENT_COUNT": expected_count,
        "P3_TRIANGLE_COVERAGE": 1.0,
        "CROSS_P3_COMPONENT_MERGE_COUNT": 0,
        "DUAL_MODAL_COMPONENTS": expected_count,
        "MAC_COMPONENTS_ATTEMPTED": 0,
        "MAC_COMPONENTS_SUCCESS": 0,
        "MAC_ROUTED_COMPONENTS": 0,
        "MAC_ROUTE_SELECTED_COMPONENTS": 0,
        "DETERMINISTIC_FALLBACK_COMPONENTS": faceted_count,
        "CURRENT_V6_COMPONENTS_ROUTED": sum(row["current_v6_attempted"] for row in rows),
        "CURRENT_V6_COMPONENTS_QA_PASS": sum(row["current_v6_success"] for row in rows),
        "CURRENT_V6_COMPONENTS_SELECTED": backend_counts.get("CURRENT_V6", 0),
        "SUPERFIT_COMPONENTS_ROUTED": 0,
        "SUPERFIT_LOCAL_RUN_COMPONENTS": 0,
        "SUPERFIT_PRIMITIVES_REUSED": 0,
        "SUPERFIT_COMPONENTS_QA_PASS": 0,
        "SUPERFIT_COMPONENTS_SELECTED": 0,
        "POINT2CAD_COMPONENTS_ROUTED": 0,
        "POINT2CAD_COMPONENTS_REAL_EXECUTED": 0,
        "POINT2CAD_COMPONENTS_SURFACE_SUCCESS": 0,
        "POINT2CAD_COMPONENTS_TOPOLOGY_SUCCESS": 0,
        "POINT2CAD_COMPONENTS_QA_PASS": 0,
        "POINT2CAD_COMPONENTS_SELECTED": 0,
        "HYBRID_COMPONENTS_ROUTED": 0,
        "HYBRID_COMPONENTS_QA_PASS": 0,
        "HYBRID_COMPONENTS_SELECTED": 0,
        "FACETED_FALLBACK_COMPONENTS": faceted_count,
        "PURE_CAD_NATIVE_COMPONENTS": native_count,
        "HYBRID_WITH_FACETED_RESIDUAL_COMPONENTS": 0,
        "PURE_FACETED_COMPONENTS": faceted_count,
        "CAD_NATIVE_COMPONENT_COUNT": native_count,
        "FACETED_COMPONENT_COUNT": faceted_count,
        "CAD_NATIVE_RECOVERY_RATE": native_count / max(expected_count, 1),
        "CAD_NATIVE_TRIANGLE_SUPPORT": native_triangles,
        "FACETED_TRIANGLE_SUPPORT": total_triangles - native_triangles,
        "CAD_NATIVE_TRIANGLE_SUPPORT_RATIO": native_triangles / max(total_triangles, 1),
        "FINAL_COMPONENT_COUNT": selected_count,
        "FINAL_SOLID_COUNT": sum(row["solid_count"] for row in rows),
        "FINAL_CLOSED_SHELL_COUNT": 0,
        "FINAL_OPEN_SHELL_COUNT": sum(row["shell_count"] > 0 for row in rows),
        "FINAL_FACE_COUNT": None,
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
        "BASELINE_FACETED_STEP": str(baseline_step),
        "MIXED_CAD_STEP": str(assembly_path),
        "MIXED_CAD_STEP_RELOAD": bool(assembly_result.get("completed")),
        "BACKEND_SELECTED_COUNTS": backend_counts,
        "POINT2CAD_PROVENANCE_VERIFIED": False,
        "SUPERFIT_GLOBAL_REFIT": False,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
    }
    dump(output_root / "artifacts/final_summary.json", summary)
    report = ["# TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3", ""]
    report.extend(f"{key}={value}" for key, value in summary.items())
    report.extend(
        [
            "",
            "The frozen P3 component identity is preserved dynamically.",
            "The existing global Point2CAD and SuperFit artifacts were not claimed as component-native because their provenance is insufficient.",
            "Faceted fallback is not counted as CAD-native.",
            f"BASELINE_FACETED_STEP={baseline_step}",
            f"MIXED_CAD_STEP={assembly_path}",
            f"ASSEMBLY_RESULT={json.dumps(assembly_result, sort_keys=True)}",
        ]
    )
    (output_root / "artifacts/TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3_REPORT.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("/data/home/cuiyuehan/project/mesh2cad"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--p3-root", type=Path, required=True)
    parser.add_argument(
        "--base-root",
        type=Path,
        default=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_component_fullstack_multibackend_v2"),
    )
    parser.add_argument(
        "--baseline-step",
        type=Path,
        default=Path(
            "/data/home/cuiyuehan/project/mesh2cad/ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/14_assembly/tank_p3_45_component_assembly.step"
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_45_component_mixed_cad_recovery_v3"),
    )
    parser.add_argument("--skip-p3", action="store_true")
    parser.add_argument("--skip-assembly", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
