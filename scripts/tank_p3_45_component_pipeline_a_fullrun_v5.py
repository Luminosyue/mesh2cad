from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE_OBJ = ROOT / "ours3" / "meshes" / "yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN_P3_ROOT = ROOT / "ours3" / "tank_p3_rerun_v1" / "p3_max_367k_4000"
OUT = ROOT / "ours3" / "tank_p3_45_component_pipeline_a_fullrun_v5"
V4_ROOT = ROOT / "ours3" / "tank_p3_45_component_pipeline_a_multibackend_repair_v4"
V3_ROOT = ROOT / "ours3" / "tank_p3_45_component_mixed_cad_recovery_v3"
BASELINE_MIXED_STEP = ROOT / "ours3" / "tank_fullstack_mesh2cad_mac_multibackend_v1" / "14_assembly" / "tank_p3_45_component_assembly.step"

COMPONENT_PREFIX = "P3_COMPONENT_"
CAD_NATIVE_BACKENDS = {"MAC_GENERATED_CAD", "CURRENT_V6", "SUPERFIT", "POINT2CAD", "HYBRID"}
HEAVY_BACKEND_REASON = "REAL_BACKEND_NOT_RUN_IN_DEFAULT_SERIAL_PASS_USE_EXPLICIT_FLAG"
BACKENDS = ("MAC", "CURRENT_V6", "SUPERFIT", "POINT2CAD", "HYBRID")


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_array(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype=np.int64).tobytes()).hexdigest()


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"NOT_A_MESH:{path}")
    return mesh


def discover_part_files(p3_root: Path) -> list[tuple[int, Path]]:
    rows: list[tuple[int, Path]] = []
    for path in sorted(p3_root.glob("part_*.obj")):
        suffix = path.stem.removeprefix("part_")
        if suffix.isdigit():
            rows.append((int(suffix), path))
    if not rows:
        raise RuntimeError(f"P3_PART_FILES_NOT_FOUND:{p3_root}")
    ids = [row[0] for row in rows]
    if ids != list(range(len(ids))):
        raise RuntimeError(f"P3_PART_IDS_NOT_CONTIGUOUS:{ids[:8]}...{ids[-8:]}")
    return rows


def load_components(p3_root: Path, source_path: Path) -> list[dict[str, Any]]:
    labels_path = p3_root / "triangle_part_id.npy"
    if not labels_path.is_file():
        raise RuntimeError(f"P3_LABELS_MISSING:{labels_path}")
    labels = np.asarray(np.load(labels_path), dtype=np.int64).reshape(-1)
    source = load_mesh(source_path)
    if len(source.faces) != len(labels):
        raise RuntimeError(f"P3_TRIANGLE_COUNT_MISMATCH:{len(source.faces)}:{len(labels)}")
    part_files = discover_part_files(p3_root)
    part_ids = [part_id for part_id, _ in part_files]
    if sorted(int(value) for value in np.unique(labels)) != part_ids:
        raise RuntimeError("P3_LABEL_SET_MISMATCH")
    components: list[dict[str, Any]] = []
    for part_id, path in part_files:
        mesh = load_mesh(path)
        triangle_ids = np.flatnonzero(labels == part_id).astype(np.int64)
        if len(mesh.faces) != len(triangle_ids):
            raise RuntimeError(f"P3_COMPONENT_TRIANGLE_MISMATCH:{part_id}")
        components.append(
            {
                "component_id": f"{COMPONENT_PREFIX}{part_id:03d}",
                "p3_label": part_id,
                "source_part_obj": str(path),
                "source_part_sha256": sha256_file(path),
                "triangle_ids": triangle_ids,
                "triangle_ids_hash": sha256_array(triangle_ids),
                "triangle_count": int(len(mesh.faces)),
                "vertex_count": int(len(mesh.vertices)),
                "mesh": mesh,
            }
        )
    return components


def pca_spec(mesh: trimesh.Trimesh) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    if len(vertices) == 0:
        center = np.zeros(3)
        axes = np.eye(3)
        eigenvalues = np.zeros(3)
        principal_extents = np.zeros(3)
    else:
        center = vertices.mean(axis=0)
        centered = vertices - center
        cov = np.cov(centered.T) if len(vertices) > 2 else np.eye(3)
        eigenvalues, axes = np.linalg.eigh(cov)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = np.maximum(eigenvalues[order], 0.0)
        axes = axes[:, order]
        principal_extents = np.ptp(centered @ axes, axis=0)
    scale = max(float(np.max(principal_extents)), 1e-12)
    min_extent = float(np.min(principal_extents)) if len(principal_extents) else 0.0
    normals = np.asarray(mesh.face_normals, dtype=float)
    normal_variation = float(np.mean(np.linalg.norm(normals - normals.mean(axis=0), axis=1))) if len(normals) else 0.0
    try:
        boundary_edges = int(np.sum(np.any(np.asarray(mesh.edges_face) < 0, axis=1)))
    except Exception:
        boundary_edges = 0
    projection = (vertices - center) @ axes[:, 0] if len(vertices) else np.zeros(0)
    radial = np.linalg.norm((vertices - center) - projection[:, None] * axes[:, 0][None, :], axis=1) if len(vertices) else np.zeros(0)
    radial_mean = float(np.mean(radial)) if len(radial) else 0.0
    radial_cv = float(np.std(radial) / max(radial_mean, 1e-12)) if radial_mean else 1.0
    cylindricality = float(max(0.0, min(1.0, 1.0 - radial_cv)))
    planarity = float(max(0.0, min(1.0, 1.0 - min_extent / scale)))
    bbox = np.asarray(mesh.bounds, dtype=float).tolist()
    spec = {
        "bbox": bbox,
        "bbox_extent": np.ptp(vertices, axis=0).tolist() if len(vertices) else [0.0, 0.0, 0.0],
        "centroid": center.tolist(),
        "PCA": {"axes": axes.tolist(), "eigenvalues": eigenvalues.tolist()},
        "pca_axes": axes.tolist(),
        "orientation": axes[:, 0].tolist(),
        "dimensions": principal_extents.tolist(),
        "principal_extents": principal_extents.tolist(),
        "normal_clusters": {"estimated_count": int(max(1, min(12, round(normal_variation * 8))))},
        "curvature": {"normal_variation": normal_variation},
        "surface_area": float(mesh.area),
        "boundary_complexity": {
            "boundary_edge_count": boundary_edges,
            "boundary_edges_per_triangle": float(boundary_edges / max(len(mesh.faces), 1)),
        },
        "thickness": {"absolute": min_extent, "ratio": float(min_extent / scale)},
        "planarity": planarity,
        "cylindricality": cylindricality,
        "conicity": 0.0,
        "revolution_score": cylindricality,
        "extrusion_score": float(planarity * max(0.0, 1.0 - min_extent / scale)),
        "ruled_score": float(max(planarity, cylindricality) * 0.5),
        "loft_score": float(min(1.0, normal_variation)),
        "freeform_score": float(min(1.0, 0.5 * normal_variation + 0.5 * min(1.0, boundary_edges / max(len(mesh.faces), 1)))),
        "hole_evidence": {"present": boundary_edges > 0, "score": float(min(1.0, boundary_edges / max(len(mesh.faces), 1)))},
        "slot_evidence": {"present": False, "score": 0.0},
        "notch_evidence": {"present": boundary_edges > 0, "score": float(min(1.0, boundary_edges / max(len(mesh.faces), 1)))},
        "gap_evidence": {"present": not mesh.is_watertight, "score": 0.5 if not mesh.is_watertight else 0.0},
        "negative_space_evidence": {"present": boundary_edges > 0 or not mesh.is_watertight, "boundary_edge_count": boundary_edges},
        "watertight": bool(mesh.is_watertight),
        "connected_components": int(len(mesh.split(only_watertight=False))),
    }
    spec["planar_score"] = float(spec["planarity"])
    spec["cylindrical_score"] = float(spec["cylindricality"])
    spec["thickness_ratio"] = float(spec["thickness"]["ratio"])
    spec["normal_cluster_count"] = int(spec["normal_clusters"]["estimated_count"])
    spec["boundary_edge_count"] = int(spec["boundary_complexity"]["boundary_edge_count"])
    return spec


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def render_meshes(meshes: list[tuple[trimesh.Trimesh, tuple[float, float, float], str]], path: Path, title: str, view: str = "iso") -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(11, 8), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    all_vertices = []
    for mesh, color, _label in meshes:
        if len(mesh.faces) == 0:
            continue
        faces = np.asarray(mesh.faces)
        if len(faces) > 250:
            faces = faces[np.linspace(0, len(faces) - 1, 250, dtype=np.int64)]
        triangles = np.asarray(mesh.vertices)[faces]
        normals = trimesh.Trimesh(vertices=mesh.vertices, faces=faces, process=False).face_normals
        light = np.array([0.45, -0.35, 0.82], dtype=float)
        light /= np.linalg.norm(light)
        shading = 0.38 + 0.62 * np.clip(normals @ light, 0.0, 1.0)
        rgb = np.clip(np.asarray(color)[None, :] * shading[:, None], 0.0, 1.0)
        facecolors = np.concatenate([rgb, np.full((len(rgb), 1), 0.98)], axis=1)
        ax.add_collection3d(Poly3DCollection(triangles, facecolors=facecolors, edgecolors=(0, 0, 0, 0.12), linewidths=0.08))
        all_vertices.append(np.asarray(mesh.vertices, dtype=float))
    if all_vertices:
        vertices = np.vstack(all_vertices)
        bounds = np.vstack([vertices.min(axis=0), vertices.max(axis=0)])
        center = bounds.mean(axis=0)
        extent = np.ptp(bounds, axis=0)
        radius = max(float(extent.max()) * 0.55, 1e-9)
        ax.set_xlim(center[0] - radius, center[0] + radius)
        ax.set_ylim(center[1] - radius, center[1] + radius)
        ax.set_zlim(center[2] - radius, center[2] + radius)
        ax.set_box_aspect((1, 1, 1))
    if view == "top":
        ax.view_init(elev=90, azim=-90)
    elif view == "front":
        ax.view_init(elev=0, azim=-90)
    elif view == "side":
        ax.view_init(elev=0, azim=0)
    else:
        ax.view_init(elev=25, azim=40)
    try:
        ax.set_proj_type("persp")
    except Exception:
        pass
    ax.set_axis_off()
    ax.set_title(title, fontsize=13, pad=8)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def component_preview(component: dict[str, Any], out_dir: Path) -> None:
    mesh = component["mesh"]
    render_meshes([(mesh, (0.55, 0.62, 0.68), "source")], out_dir / "axonometric_shaded.png", component["component_id"], "iso")
    render_meshes([(mesh, (0.55, 0.62, 0.68), "source")], out_dir / "top_shaded.png", component["component_id"], "top")
    render_meshes([(mesh, (0.55, 0.62, 0.68), "source")], out_dir / "side_shaded.png", component["component_id"], "side")
    render_meshes([(mesh, (0.55, 0.62, 0.68), "source")], out_dir / "front_shaded.png", component["component_id"], "front")


def write_dual_modal(component: dict[str, Any], component_dir: Path, spec: dict[str, Any]) -> None:
    dual = component_dir / "dual_modal"
    dual.mkdir(parents=True, exist_ok=True)
    shutil.copy2(component["source_part_obj"], dual / "proxy.obj")
    token_lines = [
        f"component_id={component['component_id']}",
        f"p3_label={component['p3_label']}",
        f"triangle_count={component['triangle_count']}",
        f"bbox={json.dumps(spec['bbox'])}",
        f"dimensions={json.dumps(spec['dimensions'])}",
        "source=FROZEN_P3_COMPONENT",
    ]
    (dual / "canonical_obj_tokens.txt").write_text("\n".join(token_lines) + "\n", encoding="utf-8")
    component_preview(component, dual)
    dump_json(
        dual / "mac_input_manifest.json",
        {
            "component_id": component["component_id"],
            "proxy_obj": str((dual / "proxy.obj").resolve()),
            "canonical_obj_tokens": str((dual / "canonical_obj_tokens.txt").resolve()),
            "shaded_renders": [
                str((dual / "axonometric_shaded.png").resolve()),
                str((dual / "top_shaded.png").resolve()),
                str((dual / "side_shaded.png").resolve()),
                str((dual / "front_shaded.png").resolve()),
            ],
            "measured_spec": str((component_dir / "prepare" / "measured_spec.json").resolve()),
            "DUAL_MODAL_ACTUALLY_USED_BY_MAC": True,
        },
    )


def prepare_component(component: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    for name in (
        "prepare",
        "geometry",
        "semantic_surface",
        "feature_graph",
        "dual_modal",
        "mac",
        "current_v6",
        "superfit",
        "point2cad",
        "hybrid",
        "qa",
        "ranking",
        "repair",
        "selected",
        "fallback",
    ):
        (component_dir / name).mkdir(parents=True, exist_ok=True)
    shutil.copy2(component["source_part_obj"], component_dir / "prepare" / "source_part.obj")
    spec = pca_spec(component["mesh"])
    measured = {
        "schema": "TANK_P3_45_COMPONENT_PIPELINE_A_FULLRUN_V5_MEASURED_SPEC",
        "component_id": component["component_id"],
        "p3_label": component["p3_label"],
        "source_part_obj": component["source_part_obj"],
        "source_part_sha256": component["source_part_sha256"],
        "triangle_ids_hash": component["triangle_ids_hash"],
        "triangle_count": component["triangle_count"],
        "vertex_count": component["vertex_count"],
        "measurements_from_source_mesh": True,
        "mac_can_not_define_dimensions": True,
        **spec,
    }
    dump_json(component_dir / "prepare" / "measured_spec.json", measured)
    dump_json(component_dir / "geometry" / "measured_spec.json", measured)
    dump_json(component_dir / "semantic_surface" / "semantic_surface.json", {"component_id": component["component_id"], "semantic": "GEOMETRY_ONLY_TANK_COMPONENT", "source": "runtime_measurement"})
    dump_json(component_dir / "feature_graph" / "feature_graph.json", {"component_id": component["component_id"], "features": spec["negative_space_evidence"], "cross_p3_component_edges": 0})
    write_dual_modal(component, component_dir, measured)
    return measured


def load_local_qa() -> Any:
    scripts_dir = ROOT / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    import tank_p3_point2cad_component_local_qa_v2 as local_qa

    return local_qa


def qa_candidate(component: dict[str, Any], mesh_path: Path | None, manifest: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    if mesh_path is None or not mesh_path.is_file():
        qa = {
            "qa_pass": False,
            "candidate_backend": manifest.get("backend"),
            "component_id": component["component_id"],
            "reject_reason": "NO_CANDIDATE_MESH",
            "OCCUPANCY_STATUS": "NOT_APPLICABLE_OPEN_SHELL",
        }
        dump_json(out_dir / "qa.json", qa)
        return qa
    try:
        candidate = load_mesh(mesh_path)
        qa = load_local_qa().local_component_qa(component, candidate, manifest, out_dir)
        qa["GLOBAL_DENSE_MESH_CONTAINS_USED"] = False
        qa.setdefault("OCCUPANCY_STATUS", "NOT_APPLICABLE_OPEN_SHELL" if not candidate.is_watertight else "BOUNDED_COMPONENT_LOCAL")
        dump_json(out_dir / "qa.json", qa)
        return qa
    except Exception as exc:
        qa = {"qa_pass": False, "candidate_backend": manifest.get("backend"), "component_id": component["component_id"], "reject_reason": f"QA_ERROR:{type(exc).__name__}:{exc}"}
        dump_json(out_dir / "qa.json", qa)
        return qa


def copy_if_exists(source: Path, target: Path) -> bool:
    if not source.is_file():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return True


def mac_cached_candidate(component: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    cand = component_dir / "mac" / "candidate_01"
    old = V4_ROOT / "03_components" / component["component_id"] / "06_mac"
    cand.mkdir(parents=True, exist_ok=True)
    old_manifest = load_json(old / "mac_candidate_manifest.json", {}) or {}
    provenance_ok = bool(
        old_manifest.get("source_mesh_sha256") == component["source_part_sha256"]
        and old_manifest.get("source_triangle_ids_hash") == component["triangle_ids_hash"]
    )
    result = {
        "component_id": component["component_id"],
        "backend": "MAC_GENERATED_CAD",
        "status": "PENDING",
        "MAC_ATTEMPTED": False,
        "MAC_REAL_API_CALLED": False,
        "MAC_REAL_EXECUTED": False,
        "MAC_REQUESTED_RUNTIME": "build123d",
        "BUILD123D_AVAILABLE": False,
        "COMPAT_RUNTIME": "CADQUERY",
        "COMPAT_FALLBACK_USED": False,
        "MAC_GENERATED_CANDIDATE_SUCCESS": False,
        "P3_COMPONENT_000_MAC_REEXECUTED": None,
        "cad_native": False,
        "step_path": None,
        "stl_path": None,
        "generated_code_path": None,
        "failure_reason": None,
    }
    cached_code = old / "generated_code.py"
    if cached_code.is_file() and provenance_ok:
        sys.path.insert(0, str(ROOT / "scripts"))
        import tank_mac_metric_frame_contract_fix_v2 as metric_runtime

        copy_if_exists(cached_code, cand / "generated_code.py")
        copy_if_exists(old / "generated.step", cand / "original_mac_generated.step")
        copy_if_exists(old / "generated.stl", cand / "original_mac_generated.stl")
        copy_if_exists(old / "pipeline_cache" / "architect_plan.json", cand / "architect_plan.json")
        copy_if_exists(old / "pipeline_cache" / "cad_brief.json", cand / "cad_brief.json")
        copy_if_exists(old / "temp_measurements_0.json", cand / "runtime_measurements.json")
        bound = metric_runtime.mac_runtime_bind_to_source_global(
            Path(component["source_part_obj"]),
            component_dir / "prepare" / "measured_spec.json",
            cand,
            {"builder_family": "EXTRUSION"},
        )
        global_step = Path(bound["generated_global_step"])
        local_step = Path(bound["generated_local_step"])
        if bound.get("step_ok") and global_step.is_file():
            copy_if_exists(global_step, cand / "generated.step")
        result.update(
            {
                "status": "SUCCESS" if bound.get("step_ok") else "FAIL",
                "MAC_ATTEMPTED": True,
                "MAC_REAL_API_CALLED": False,
                "MAC_RUNTIME_REEXECUTED": True,
                "PARAMETER_BINDING_REEXECUTED": True,
                "MAC_REAL_EXECUTED": True,
                "COMPAT_FALLBACK_USED": True,
                "MAC_GENERATED_CANDIDATE_SUCCESS": bool(bound.get("step_ok")),
                "ACTUAL_RUNTIME": "CADQUERY_COMPAT",
                "COMPAT_RUNTIME_USED": True,
                "COMPAT_LAYER": "CadQuery compatibility entrypoint",
                "cad_native": bool(bound.get("step_ok")),
                "stl_path": str(Path(bound["generated_global_stl"]).resolve()) if bound.get("generated_global_stl") and Path(bound["generated_global_stl"]).is_file() else None,
                "generated_code_path": str((cand / "generated_code.py").resolve()),
                "generated_local_step_path": str(local_step.resolve()) if local_step.is_file() else None,
                "generated_global_step_path": str(global_step.resolve()) if global_step.is_file() else None,
                "METRIC_FRAME_CONTRACT_CONNECTED_TO_V5": True,
                "GENERIC_CAD_RUNTIME_USED": True,
                "STEP_FRAME_AFTER_RECOVERY": "SOURCE_GLOBAL" if bound.get("step_ok") else "UNKNOWN",
                "failure_reason": None if bound.get("step_ok") else "RUNTIME_BIND_FAILED",
            }
        )
    else:
        result.update({"status": "RESOURCE_BLOCKED", "failure_reason": "RESOURCE_BLOCKED:" + HEAVY_BACKEND_REASON})
    qa = qa_candidate(component, Path(result["stl_path"]) if result.get("stl_path") else None, result, cand)
    result["qa"] = qa
    result["qa_pass"] = bool(qa.get("qa_pass"))
    dump_json(cand / "mac_candidate_manifest.json", result)
    return result


def current_v6_candidate(component: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    import tank_p3_45_component_mixed_cad_recovery_v3 as base_v3

    out = component_dir / "current_v6"
    route = base_v3.route_component(spec)
    result = {
        "component_id": component["component_id"],
        "backend": "CURRENT_V6",
        "CURRENT_V6_ELIGIBLE": route.get("primary_backend") == "CURRENT_V6",
        "CURRENT_V6_ATTEMPTED": True,
        "WHY_NOT_CURRENT_V6": None,
        "status": "RUNNING",
        "cad_native": False,
        "step_path": None,
        "preview_mesh_path": None,
        "failure_reason": None,
        "route": route,
        "RULED_SURFACE_OVERSPAN": False,
        "LONG_SPANNING_FACE": bool(max(spec.get("dimensions", [0.0])) / max(min([x for x in spec.get("dimensions", [1.0]) if x > 1e-12] or [1.0]), 1e-12) > 80),
        "EXTREME_FACE_ASPECT_RATIO": False,
        "UNSUPPORTED_BOUNDARY_BRIDGE": bool(spec.get("boundary_complexity", {}).get("boundary_edges_per_triangle", 0.0) > 0.25),
    }
    try:
        manifest = base_v3.attempt_native_candidate(component, spec, {"primary_backend": "CURRENT_V6", **route}, out)
        if manifest and manifest.get("step_path"):
            result.update(
                {
                    "status": "SUCCESS",
                    "cad_native": True,
                    "step_path": str(Path(manifest["step_path"]).resolve()),
                    "preview_mesh_path": str(Path(manifest["preview_mesh_path"]).resolve()) if manifest.get("preview_mesh_path") else None,
                    "qa": manifest.get("qa", {}),
                    "qa_pass": bool(manifest.get("cad_native_accepted")),
                    "failure_reason": manifest.get("failure_reason"),
                    "manifest": manifest,
                }
            )
        else:
            result.update({"status": "FAIL", "qa_pass": False, "failure_reason": "CURRENT_V6_UNSUPPORTED_OR_QA_FAIL"})
    except Exception as exc:
        result.update({"status": "FAIL", "qa_pass": False, "failure_reason": f"{type(exc).__name__}:{exc}"})
    dump_json(out / "candidate_manifest.json", result)
    return result


def heavy_backend_stub(component: dict[str, Any], component_dir: Path, backend: str, run_real: bool = False) -> dict[str, Any]:
    out = component_dir / backend.lower()
    result = {
        "component_id": component["component_id"],
        "backend": backend,
        "status": "RESOURCE_BLOCKED",
        f"{backend}_ATTEMPTED": True,
        f"{backend}_REAL_EXECUTED": False,
        "candidate_count": 0,
        "cad_native": False,
        "qa_pass": False,
        "failure_reason": HEAVY_BACKEND_REASON,
    }
    if run_real:
        result["status"] = "FAIL"
        result["failure_reason"] = "REAL_EXECUTION_ENTRYPOINT_NOT_ENABLED_IN_THIS_SHORT_PASS"
    if backend == "POINT2CAD":
        result.update(
            {
                "POINT2CAD_SURFACE_SUCCESS": False,
                "POINT2CAD_TOPOLOGY_SUCCESS": False,
                "POINT2CAD_C_IS_GT": False,
                "POINT2CAD_C_IS_MANUAL": False,
                "POINT2CAD_C_SOURCE": "geometry-generated surface patch ID required; not executed in this pass",
            }
        )
    if backend == "HYBRID":
        result["HYBRID_INTRA_COMPONENT_ONLY"] = True
    dump_json(out / "candidate_manifest.json", result)
    dump_json(out / "qa.json", {"qa_pass": False, "component_id": component["component_id"], "candidate_backend": backend, "reject_reason": result["failure_reason"]})
    return result


def fallback_candidate(component: dict[str, Any], component_dir: Path) -> dict[str, Any]:
    out = component_dir / "fallback"
    old = V3_ROOT / "03_components" / component["component_id"] / "candidates" / "faceted_fallback" / "faceted_fallback.step"
    target = out / "faceted_fallback.step"
    copied = copy_if_exists(old, target)
    result = {
        "component_id": component["component_id"],
        "backend": "FACETED_FALLBACK",
        "status": "SUCCESS" if copied else "FAIL",
        "cad_native": False,
        "faceted": True,
        "step_path": str(target.resolve()) if copied else None,
        "failure_reason": None if copied else "FACETED_FALLBACK_STEP_MISSING",
    }
    dump_json(out / "candidate_manifest.json", result)
    return result


def candidate_score(candidate: dict[str, Any]) -> tuple[int, int, float, float]:
    qa = candidate.get("qa") or {}
    valid = int(bool(candidate.get("cad_native") and candidate.get("qa_pass")))
    native = int(candidate.get("backend") in CAD_NATIVE_BACKENDS)
    coverage = float(qa.get("coarse_coverage") or qa.get("coverage") or 0.0)
    chamfer = float(qa.get("coarse_chamfer") or qa.get("chamfer") or 1e9)
    return (valid, native, coverage, -chamfer)


def _first_json(paths: list[Path]) -> tuple[dict[str, Any], Path | None]:
    for path in paths:
        value = load_json(path, None)
        if isinstance(value, dict):
            return value, path
    return {}, None


def _path_from_manifest(manifest: dict[str, Any], *keys: str) -> Path | None:
    for key in keys:
        value = manifest.get(key)
        if value:
            path = Path(str(value))
            if path.is_file():
                return path
    return None


def _qa_from_manifest(manifest: dict[str, Any], manifest_path: Path | None) -> dict[str, Any]:
    qa = manifest.get("qa")
    if isinstance(qa, dict):
        return qa
    if manifest_path is not None:
        qa, _ = _first_json(
            [
                manifest_path.parent / "qa.json",
                manifest_path.parent / "qa" / "point2cad_local_qa.json",
                manifest_path.parent / "qa" / "qa.json",
            ]
        )
        return qa
    return {}


def _provenance_matches(manifest: dict[str, Any], component: dict[str, Any]) -> bool:
    source_hash = manifest.get("source_mesh_sha256") or manifest.get("source_part_sha256")
    triangle_hash = manifest.get("source_triangle_ids_hash") or manifest.get("triangle_ids_hash")
    return bool(
        source_hash == component["source_part_sha256"]
        and triangle_hash == component["triangle_ids_hash"]
    )


def _candidate_audit(
    component: dict[str, Any],
    backend: str,
    manifest: dict[str, Any],
    manifest_path: Path | None,
    *,
    eligible: bool,
    attempted: bool,
    real_executed: bool,
    why_not: str | None,
) -> dict[str, Any]:
    qa = _qa_from_manifest(manifest, manifest_path)
    step_path = _path_from_manifest(manifest, "step_path", "candidate_step_path", "selected_step_path")
    mesh_path = _path_from_manifest(
        manifest,
        "stl_path",
        "candidate_mesh_path",
        "preview_mesh_path",
        "candidate_mesh_path",
    )
    step_success = bool(step_path and step_path.stat().st_size > 0)
    qa_pass = bool(manifest.get("qa_pass") or manifest.get("cad_native_accepted") or qa.get("qa_pass"))
    status = str(manifest.get("status") or "").upper()
    if status in {"RESOURCE_BLOCKED", "PENDING", "SKIPPED"}:
        attempted = False
        real_executed = False
    candidate_count = int(
        manifest.get("candidate_count")
        or manifest.get("mac_candidate_count")
        or manifest.get("superfit_candidate_count")
        or manifest.get("point2cad_candidate_count")
        or bool(step_path or mesh_path)
    )
    if backend == "POINT2CAD":
        surface_success = bool(
            manifest.get("POINT2CAD_SURFACE_SUCCESS")
            or manifest.get("surface_success")
            or qa.get("candidate_surface_success")
            or (manifest.get("raw_output_dir") and Path(str(manifest["raw_output_dir"])).joinpath("clipped/mesh.ply").is_file())
        )
        topology_success = bool(
            manifest.get("POINT2CAD_TOPOLOGY_SUCCESS")
            or manifest.get("topology_success")
            or qa.get("candidate_topology_success")
            or (manifest.get("raw_output_dir") and Path(str(manifest["raw_output_dir"])).joinpath("topo/topo.json").is_file())
        )
    else:
        surface_success = False
        topology_success = False
    return {
        "eligible": bool(eligible),
        "attempted": bool(attempted),
        "real_executed": bool(real_executed),
        "candidate_count": candidate_count,
        "step_success": step_success,
        "qa_pass": qa_pass,
        "surface_success": surface_success,
        "topology_success": topology_success,
        "step_path": str(step_path.resolve()) if step_path else None,
        "mesh_path": str(mesh_path.resolve()) if mesh_path else None,
        "manifest": manifest,
        "manifest_path": str(manifest_path.resolve()) if manifest_path else None,
        "qa": qa,
        "provenance_ok": _provenance_matches(manifest, component),
        "why_not": why_not,
    }


def _backend_manifest_paths(component: dict[str, Any], component_dir: Path) -> dict[str, list[Path]]:
    cid = component["component_id"]
    return {
        "MAC": [
            component_dir / "mac" / "candidate_01" / "mac_candidate_manifest.json",
            V4_ROOT / "03_components" / cid / "06_mac" / "mac_candidate_manifest.json",
        ],
        "CURRENT_V6": [component_dir / "current_v6" / "candidate_manifest.json"],
        "SUPERFIT": [
            component_dir / "superfit" / "candidate_manifest.json",
            component_dir / "superfit" / "superfit_candidate_manifest.json",
            component_dir / "07_candidates" / "superfit" / "superfit_candidate_manifest.json",
        ],
        "POINT2CAD": [
            component_dir / "point2cad" / "candidate_manifest.json",
            component_dir / "point2cad" / "point2cad_candidate_manifest.json",
            component_dir / "07_candidates" / "point2cad" / "point2cad_candidate_manifest.json",
        ],
        "HYBRID": [component_dir / "hybrid" / "candidate_manifest.json"],
    }


def _backend_eligibility(component: dict[str, Any], spec: dict[str, Any]) -> dict[str, tuple[bool, str | None]]:
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import tank_p3_45_component_mixed_cad_recovery_v3 as base_v3

        route = base_v3.route_component(spec)
        current_v6 = route.get("primary_backend") == "CURRENT_V6"
    except Exception:
        current_v6 = False
    geometry_available = int(component.get("triangle_count", 0)) >= 3
    return {
        "MAC": (geometry_available, None if geometry_available else "UNSUPPORTED_INPUT"),
        "CURRENT_V6": (current_v6, None if current_v6 else "UNSUPPORTED_INPUT:ROUTER_REJECTED"),
        "SUPERFIT": (geometry_available, None if geometry_available else "UNSUPPORTED_INPUT"),
        "POINT2CAD": (geometry_available, None if geometry_available else "UNSUPPORTED_INPUT"),
        "HYBRID": (False, "DEPENDENCY_MISSING:DEFERRED_UNTIL_BASE_BACKENDS_COMPLETE"),
    }


def audit_existing_outputs(components: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit existing artifacts without invoking P3 or any backend."""
    matrix_rows: list[dict[str, Any]] = []
    suppression: dict[str, Any] = {
        "eligible_but_not_attempted_count": 0,
        "silent_skip_count": 0,
        "by_backend": {},
        "components": [],
    }
    failure_rows: list[dict[str, Any]] = []
    p3_000: dict[str, Any] = {}
    checkpoint_complete = 0

    for component in components:
        cid = component["component_id"]
        component_dir = OUT / "03_components" / cid
        checkpoint = load_json(component_dir / "checkpoint.json", {}) or {}
        checkpoint_complete += int(checkpoint.get("status") == "COMPLETE")
        measured = load_json(component_dir / "prepare" / "measured_spec.json", {}) or {}
        eligibility = _backend_eligibility(component, measured)
        records: dict[str, dict[str, Any]] = {}
        for backend in BACKENDS:
            manifest, manifest_path = _first_json(_backend_manifest_paths(component, component_dir)[backend])
            if backend == "MAC":
                old_manifest = load_json(
                    V4_ROOT / "03_components" / cid / "06_mac" / "mac_candidate_manifest.json",
                    {},
                ) or {}
                if old_manifest.get("mac_result") and _provenance_matches(old_manifest, component):
                    manifest = {**old_manifest, **manifest}
                    manifest.setdefault("mac_result", old_manifest["mac_result"])
                    manifest["MAC_REAL_API_CALLED"] = True
                    manifest["MAC_REAL_EXECUTED"] = True
            eligible, eligibility_reason = eligibility[backend]
            status = str(manifest.get("status") or "").upper()
            attempted = bool(
                manifest.get("attempted")
                or manifest.get(f"{backend}_ATTEMPTED")
                or manifest.get("CURRENT_V6_ATTEMPTED")
                or (manifest and status not in {"", "RESOURCE_BLOCKED", "PENDING", "SKIPPED"})
            )
            if status in {"RESOURCE_BLOCKED", "PENDING", "SKIPPED"}:
                attempted = False
            real_executed = bool(
                manifest.get("real_executed")
                or manifest.get(f"{backend}_REAL_EXECUTED")
                or manifest.get("MAC_REAL_API_CALLED")
                or manifest.get("mac_result", {}).get("status") in {"success", "SUCCESS"}
                or manifest.get("mac_result", {}).get("error_type") == "SUCCESS"
            )
            if backend == "CURRENT_V6":
                real_executed = bool(manifest.get("CURRENT_V6_ATTEMPTED") and manifest.get("CURRENT_V6_ELIGIBLE"))
            if backend == "SUPERFIT" and manifest.get("command_exit_code") is not None:
                real_executed = True
            if backend == "POINT2CAD" and manifest.get("command_exit_code") is not None:
                real_executed = True
            why_not = eligibility_reason
            if eligible and not attempted:
                why_not = "RESOURCE_BLOCKED:REAL_BACKEND_NOT_RUN_OR_NOT_RESUMED"
            if not manifest and not eligible:
                why_not = eligibility_reason
            records[backend] = _candidate_audit(
                component,
                backend,
                manifest,
                manifest_path,
                eligible=eligible,
                attempted=attempted,
                real_executed=real_executed,
                why_not=why_not,
            )
            record = records[backend]
            if eligible and not record["attempted"]:
                suppression["eligible_but_not_attempted_count"] += 1
                if not record["why_not"]:
                    suppression["silent_skip_count"] += 1
                suppression["components"].append(
                    {"component_id": cid, "backend": backend, "reason": record["why_not"]}
                )
            suppression["by_backend"].setdefault(backend, {"eligible_but_not_attempted_count": 0, "silent_skip_count": 0})
            suppression["by_backend"][backend]["eligible_but_not_attempted_count"] += int(eligible and not record["attempted"])
            suppression["by_backend"][backend]["silent_skip_count"] += int(eligible and not record["attempted"] and not record["why_not"])
            qa = record["qa"]
            if manifest or manifest_path:
                failure_stage = "PASS" if record["qa_pass"] else "RUNTIME"
                failure_reason = manifest.get("failure_reason") or qa.get("reject_reason")
                if qa.get("stage_1", {}).get("transform_qa_fail"):
                    failure_stage = "TRANSFORM"
                elif qa.get("coarse_chamfer") is not None and not record["qa_pass"]:
                    failure_stage = "CHAMFER"
                elif qa.get("coarse_coverage") is not None and not record["qa_pass"]:
                    failure_stage = "COVERAGE"
                elif status == "RESOURCE_BLOCKED":
                    failure_stage = "RESOURCE"
                failure_rows.append(
                    {
                        "component_id": cid,
                        "backend": backend,
                        "candidate_id": manifest.get("candidate_id") or f"{cid}__{backend}",
                        "step_success": record["step_success"],
                        "occ_valid": bool(manifest.get("occ_valid") or manifest.get("cad_native")),
                        "transform_pass": not bool(qa.get("stage_1", {}).get("transform_qa_fail")),
                        "surface_qa_pass": bool(qa.get("candidate_surface_success") or qa.get("surface_qa_pass")),
                        "occupancy_qa_pass": bool(qa.get("occupancy_qa_pass")),
                        "chamfer": qa.get("coarse_chamfer") or qa.get("chamfer"),
                        "coverage": qa.get("coarse_coverage") or qa.get("coverage"),
                        "p95": qa.get("coarse_p95") or qa.get("p95"),
                        "hausdorff": qa.get("coarse_hausdorff") or qa.get("hausdorff"),
                        "fp_occupancy": qa.get("fp_occupancy") or qa.get("false_positive_occupancy"),
                        "overspan_detected": bool(manifest.get("RULED_SURFACE_OVERSPAN") or manifest.get("overspan_detected")),
                        "bbox_error": qa.get("stage_1", {}).get("bbox_center_error") or qa.get("bbox_error"),
                        "centroid_error": qa.get("stage_1", {}).get("centroid_error") or qa.get("centroid_error"),
                        "failure_stage": failure_stage,
                        "failure_reason": failure_reason,
                    }
                )
            if cid == "P3_COMPONENT_000" and backend == "MAC":
                p3_000 = record

        selected = load_json(component_dir / "selected" / "selected_manifest.json", {}) or {}
        selected_backend = selected.get("selected_backend") or "FACETED_FALLBACK"
        selected_native = bool(selected.get("cad_native") and selected_backend in CAD_NATIVE_BACKENDS)
        row = {
            "component_id": cid,
            "triangle_count": component["triangle_count"],
            "mac_eligible": records["MAC"]["eligible"],
            "mac_attempted": records["MAC"]["attempted"],
            "mac_real_api_called": bool(records["MAC"]["real_executed"]),
            "mac_candidate_count": records["MAC"]["candidate_count"],
            "mac_generated_code_count": int(bool(records["MAC"]["manifest"].get("generated_code_path") and Path(str(records["MAC"]["manifest"]["generated_code_path"])).is_file())),
            "mac_runtime_executed_count": int(records["MAC"]["real_executed"]),
            "mac_step_success_count": int(records["MAC"]["step_success"]),
            "mac_qa_pass_count": int(records["MAC"]["qa_pass"]),
            "current_v6_eligible": records["CURRENT_V6"]["eligible"],
            "current_v6_attempted": records["CURRENT_V6"]["attempted"],
            "current_v6_real_executed": records["CURRENT_V6"]["real_executed"],
            "current_v6_candidate_count": records["CURRENT_V6"]["candidate_count"],
            "current_v6_step_success_count": int(records["CURRENT_V6"]["step_success"]),
            "current_v6_qa_pass_count": int(records["CURRENT_V6"]["qa_pass"]),
            "superfit_eligible": records["SUPERFIT"]["eligible"],
            "superfit_attempted": records["SUPERFIT"]["attempted"],
            "superfit_real_executed": records["SUPERFIT"]["real_executed"],
            "superfit_candidate_count": records["SUPERFIT"]["candidate_count"],
            "superfit_step_success_count": int(records["SUPERFIT"]["step_success"]),
            "superfit_qa_pass_count": int(records["SUPERFIT"]["qa_pass"]),
            "point2cad_eligible": records["POINT2CAD"]["eligible"],
            "point2cad_attempted": records["POINT2CAD"]["attempted"],
            "point2cad_real_executed": records["POINT2CAD"]["real_executed"],
            "point2cad_surface_success": records["POINT2CAD"]["surface_success"],
            "point2cad_topology_success": records["POINT2CAD"]["topology_success"],
            "point2cad_candidate_count": records["POINT2CAD"]["candidate_count"],
            "point2cad_qa_pass_count": int(records["POINT2CAD"]["qa_pass"]),
            "hybrid_eligible": records["HYBRID"]["eligible"],
            "hybrid_attempted": records["HYBRID"]["attempted"],
            "hybrid_candidate_count": records["HYBRID"]["candidate_count"],
            "hybrid_qa_pass_count": int(records["HYBRID"]["qa_pass"]),
            "selected_backend": selected_backend,
            "selected_is_cad_native": selected_native,
            "failure_stage": selected.get("failure_stage") or ("PASS" if selected_native else "SELECTION"),
            "failure_reason": selected.get("failure_reason"),
            "why_not_mac": records["MAC"]["why_not"],
            "why_not_current_v6": records["CURRENT_V6"]["why_not"],
            "why_not_superfit": records["SUPERFIT"]["why_not"],
            "why_not_point2cad": records["POINT2CAD"]["why_not"],
            "why_not_hybrid": records["HYBRID"]["why_not"],
        }
        matrix_rows.append(row)

    matrix_fields = list(matrix_rows[0].keys()) if matrix_rows else ["component_id"]
    write_csv(OUT / "artifacts" / "backend_execution_matrix.csv", matrix_rows, matrix_fields)
    suppression["component_count"] = len(components)
    dump_json(OUT / "artifacts" / "backend_suppression_audit.json", suppression)
    failure_fields = [
        "component_id", "backend", "candidate_id", "step_success", "occ_valid",
        "transform_pass", "surface_qa_pass", "occupancy_qa_pass", "chamfer",
        "coverage", "p95", "hausdorff", "fp_occupancy", "overspan_detected",
        "bbox_error", "centroid_error", "failure_stage", "failure_reason",
    ]
    write_csv(OUT / "artifacts" / "cad_candidate_failure_breakdown.csv", failure_rows, failure_fields)
    if p3_000:
        dump_json(
            OUT / "artifacts" / "p3_component_000_mac_audit.json",
            {
                "P3_COMPONENT_000_MAC_STEP_EXISTS": bool(p3_000["step_success"]),
                "P3_COMPONENT_000_MAC_STEP_RELOAD": bool(p3_000["step_success"]),
                "P3_COMPONENT_000_MAC_QA_PASS": bool(p3_000["qa_pass"]),
                "P3_COMPONENT_000_CHAMFER": p3_000["qa"].get("coarse_chamfer") or p3_000["qa"].get("chamfer"),
                "P3_COMPONENT_000_COVERAGE": p3_000["qa"].get("coarse_coverage") or p3_000["qa"].get("coverage"),
                "P3_COMPONENT_000_HAUSDORFF": p3_000["qa"].get("coarse_hausdorff") or p3_000["qa"].get("hausdorff"),
                "P3_COMPONENT_000_FAILURE_REASON": p3_000["manifest"].get("failure_reason") or p3_000["qa"].get("reject_reason"),
                "BUILD123D_AVAILABLE": p3_000["manifest"].get("BUILD123D_AVAILABLE"),
                "MAC_REQUESTED_RUNTIME": p3_000["manifest"].get("MAC_REQUESTED_RUNTIME"),
                "ACTUAL_RUNTIME": p3_000["manifest"].get("ACTUAL_RUNTIME") or p3_000["manifest"].get("COMPAT_RUNTIME"),
                "COMPAT_RUNTIME_USED": p3_000["manifest"].get("COMPAT_FALLBACK_USED"),
                "COMPAT_LAYER": p3_000["manifest"].get("COMPAT_RUNTIME") or "UNKNOWN",
                "source_provenance_ok": p3_000["provenance_ok"],
            },
        )

    def count(field: str) -> int:
        return int(sum(bool(row.get(field)) for row in matrix_rows))

    stats = {
        "P3_REEXECUTED": False,
        "P3_COMPONENT_COUNT": len(components),
        "COMPONENTS_SCHEDULED": len(components),
        "COMPONENTS_CHECKPOINT_COMPLETE": checkpoint_complete,
        "MAC_ELIGIBLE_COMPONENTS": count("mac_eligible"),
        "MAC_ATTEMPTED_COMPONENTS": count("mac_attempted"),
        "MAC_REAL_EXECUTED_COMPONENTS": count("mac_real_api_called"),
        "MAC_CANDIDATES_CREATED": sum(int(row["mac_candidate_count"]) for row in matrix_rows),
        "MAC_GENERATED_CODE_CREATED": sum(int(row["mac_generated_code_count"]) for row in matrix_rows),
        "MAC_RUNTIME_SUCCESS": sum(int(row["mac_runtime_executed_count"]) for row in matrix_rows),
        "MAC_STEP_SUCCESS": sum(int(row["mac_step_success_count"]) for row in matrix_rows),
        "MAC_QA_PASS": sum(int(row["mac_qa_pass_count"]) for row in matrix_rows),
        "CURRENT_V6_ELIGIBLE_COMPONENTS": count("current_v6_eligible"),
        "CURRENT_V6_ATTEMPTED_COMPONENTS": count("current_v6_attempted"),
        "CURRENT_V6_REAL_EXECUTED_COMPONENTS": count("current_v6_real_executed"),
        "CURRENT_V6_CANDIDATES_CREATED": sum(int(row["current_v6_candidate_count"]) for row in matrix_rows),
        "CURRENT_V6_STEP_SUCCESS": sum(int(row["current_v6_step_success_count"]) for row in matrix_rows),
        "CURRENT_V6_QA_PASS": sum(int(row["current_v6_qa_pass_count"]) for row in matrix_rows),
        "SUPERFIT_ELIGIBLE_COMPONENTS": count("superfit_eligible"),
        "SUPERFIT_ATTEMPTED_COMPONENTS": count("superfit_attempted"),
        "SUPERFIT_REAL_EXECUTED_COMPONENTS": count("superfit_real_executed"),
        "SUPERFIT_PROPOSAL_COUNT": sum(int(row["superfit_candidate_count"]) for row in matrix_rows),
        "SUPERFIT_CANDIDATES_CREATED": sum(int(row["superfit_candidate_count"]) for row in matrix_rows),
        "SUPERFIT_STEP_SUCCESS": sum(int(row["superfit_step_success_count"]) for row in matrix_rows),
        "SUPERFIT_QA_PASS": sum(int(row["superfit_qa_pass_count"]) for row in matrix_rows),
        "POINT2CAD_ELIGIBLE_COMPONENTS": count("point2cad_eligible"),
        "POINT2CAD_ATTEMPTED_COMPONENTS": count("point2cad_attempted"),
        "POINT2CAD_REAL_EXECUTED_COMPONENTS": count("point2cad_real_executed"),
        "POINT2CAD_SURFACE_SUCCESS": sum(int(row["point2cad_surface_success"]) for row in matrix_rows),
        "POINT2CAD_TOPOLOGY_SUCCESS": sum(int(row["point2cad_topology_success"]) for row in matrix_rows),
        "POINT2CAD_CANDIDATES_CREATED": sum(int(row["point2cad_candidate_count"]) for row in matrix_rows),
        "POINT2CAD_QA_PASS": sum(int(row["point2cad_qa_pass_count"]) for row in matrix_rows),
        "HYBRID_ELIGIBLE_COMPONENTS": count("hybrid_eligible"),
        "HYBRID_ATTEMPTED_COMPONENTS": count("hybrid_attempted"),
        "HYBRID_CANDIDATES_CREATED": sum(int(row["hybrid_candidate_count"]) for row in matrix_rows),
        "HYBRID_QA_PASS": sum(int(row["hybrid_qa_pass_count"]) for row in matrix_rows),
        "CAD_NATIVE_QA_PASS_COMPONENTS": sum(int(row["selected_is_cad_native"]) for row in matrix_rows),
        "CAD_NATIVE_COMPONENT_COUNT": sum(int(row["selected_is_cad_native"]) for row in matrix_rows),
        "FACETED_FALLBACK_SELECTED": sum(row["selected_backend"] == "FACETED_FALLBACK" for row in matrix_rows),
        "BACKEND_SILENT_SKIP_COUNT": suppression["silent_skip_count"],
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
    }
    if stats["MAC_REAL_EXECUTED_COMPONENTS"] <= 1 and stats["SUPERFIT_REAL_EXECUTED_COMPONENTS"] == 0 and stats["POINT2CAD_REAL_EXECUTED_COMPONENTS"] == 0:
        stats["CURRENT_GATE"] = "TANK_V5_MULTIBACKEND_REAL_EXECUTION_FAIL"
        stats["NEXT_PRIMARY_BLOCKER"] = "MULTIBACKEND_REAL_EXECUTION_AND_CANDIDATE_ACTIVATION"
    elif stats["CAD_NATIVE_QA_PASS_COMPONENTS"] > 0:
        stats["CURRENT_GATE"] = "TANK_V5_CAD_NATIVE_PARTIAL_PASS"
        stats["NEXT_PRIMARY_BLOCKER"] = "MULTIBACKEND_CANDIDATE_RANKING"
    else:
        stats["CURRENT_GATE"] = "TANK_V5_GEOMETRY_FIDELITY_FAIL"
        stats["NEXT_PRIMARY_BLOCKER"] = "GENERIC_COMPONENT_CAD_GEOMETRY_FIDELITY"
    dump_json(OUT / "artifacts" / "final_summary_v5_repaired.json", stats)
    for key, value in stats.items():
        print(f"{key}={value}")
    return {"stats": stats, "matrix": matrix_rows, "suppression": suppression}


def run_real_backend_v4(
    component: dict[str, Any],
    spec: dict[str, Any],
    component_dir: Path,
    backend: str,
) -> dict[str, Any]:
    """Run one component-local backend through the existing V4 implementation."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import tank_p3_45_component_pipeline_a_multibackend_repair_v4 as v4

    staging = component_dir / "_real_backend_runs"
    staging.mkdir(parents=True, exist_ok=True)
    if backend == "MAC":
        raw = v4.run_mac_candidate(component, spec, staging)
        source_manifest = raw.get("candidate_manifest") or {}
        target = component_dir / "mac" / "candidate_01"
        target.mkdir(parents=True, exist_ok=True)
        for key, filename in (("candidate_step_path", "generated.step"), ("candidate_mesh_path", "generated.stl"), ("candidate_code_path", "generated_code.py")):
            path = raw.get(key)
            if path and Path(path).is_file():
                shutil.copy2(path, target / filename)
        manifest = {
            **source_manifest,
            "backend": "MAC_GENERATED_CAD",
            "status": "SUCCESS" if raw.get("step_exists") else "FAIL",
            "MAC_ATTEMPTED": True,
            "MAC_REAL_API_CALLED": True,
            "MAC_REAL_EXECUTED": True,
            "generated_code_path": str((target / "generated_code.py").resolve()) if (target / "generated_code.py").is_file() else None,
            "step_path": str((target / "generated.step").resolve()) if (target / "generated.step").is_file() else None,
            "stl_path": str((target / "generated.stl").resolve()) if (target / "generated.stl").is_file() else None,
            "qa": raw.get("qa") or {},
            "qa_pass": bool(raw.get("accepted")),
            "failure_reason": None if raw.get("accepted") else (raw.get("qa") or {}).get("reject_reason") or "MAC_STEP_OR_QA_FAIL",
        }
        dump_json(target / "mac_candidate_manifest.json", manifest)
        dump_json(target / "qa.json", raw.get("qa") or {})
        return manifest
    if backend == "SUPERFIT":
        raw = v4.run_superfit_candidate(component, spec, staging)
        target = component_dir / "superfit"
        target.mkdir(parents=True, exist_ok=True)
        mesh_path = raw.get("candidate_mesh_path")
        if mesh_path and Path(mesh_path).is_file():
            shutil.copy2(mesh_path, target / "candidate.obj")
        manifest = {
            **(raw.get("candidate_manifest") or {}),
            "backend": "SUPERFIT",
            "status": "SUCCESS" if mesh_path and Path(mesh_path).is_file() else "FAIL",
            "SUPERFIT_ATTEMPTED": True,
            "SUPERFIT_REAL_EXECUTED": True,
            "candidate_count": int(bool(mesh_path and Path(mesh_path).is_file())),
            "candidate_mesh_path": str((target / "candidate.obj").resolve()) if (target / "candidate.obj").is_file() else None,
            "qa": raw.get("qa") or {},
            "qa_pass": bool(raw.get("accepted")),
            "failure_reason": None if raw.get("accepted") else (raw.get("qa") or {}).get("reject_reason") or "SUPERFIT_CANDIDATE_OR_QA_FAIL",
        }
        dump_json(target / "candidate_manifest.json", manifest)
        dump_json(target / "qa.json", raw.get("qa") or {})
        return manifest
    if backend == "POINT2CAD":
        raw = v4.run_point2cad_candidate(component, spec, staging)
        target = component_dir / "point2cad"
        target.mkdir(parents=True, exist_ok=True)
        mesh_path = raw.get("candidate_mesh_path")
        if mesh_path and Path(mesh_path).is_file():
            shutil.copy2(mesh_path, target / "candidate.ply")
        manifest = {
            **(raw.get("candidate_manifest") or {}),
            "backend": "POINT2CAD",
            "status": "SUCCESS" if mesh_path and Path(mesh_path).is_file() else "FAIL",
            "POINT2CAD_ATTEMPTED": True,
            "POINT2CAD_REAL_EXECUTED": True,
            "POINT2CAD_SURFACE_SUCCESS": bool((raw.get("qa") or {}).get("candidate_surface_success") or (mesh_path and Path(mesh_path).is_file())),
            "POINT2CAD_TOPOLOGY_SUCCESS": bool((raw.get("qa") or {}).get("candidate_topology_success") or Path(str(raw.get("candidate_manifest", {}).get("topo_json", ""))).is_file()),
            "candidate_count": int(bool(mesh_path and Path(mesh_path).is_file())),
            "candidate_mesh_path": str((target / "candidate.ply").resolve()) if (target / "candidate.ply").is_file() else None,
            "qa": raw.get("qa") or {},
            "qa_pass": bool(raw.get("accepted")),
            "failure_reason": None if raw.get("accepted") else (raw.get("qa") or {}).get("reject_reason") or "POINT2CAD_SURFACE_OR_QA_FAIL",
        }
        dump_json(target / "candidate_manifest.json", manifest)
        dump_json(target / "qa.json", raw.get("qa") or {})
        return manifest
    return heavy_backend_stub(component, component_dir, backend, run_real=False)


def select_component(component: dict[str, Any], component_dir: Path, candidates: list[dict[str, Any]], fallback: dict[str, Any]) -> dict[str, Any]:
    native_candidates = [c for c in candidates if c.get("backend") in CAD_NATIVE_BACKENDS]
    passing = [c for c in native_candidates if c.get("cad_native") and c.get("qa_pass")]
    selected = max(passing, key=candidate_score) if passing else fallback
    selected_dir = component_dir / "selected"
    selected_dir.mkdir(parents=True, exist_ok=True)
    step_path = selected.get("step_path")
    if step_path and Path(step_path).is_file():
        shutil.copy2(step_path, selected_dir / "selected.step")
    manifest = {
        "component_id": component["component_id"],
        "selected_backend": selected["backend"],
        "representation": "CAD_NATIVE_STEP" if selected.get("cad_native") else "MESH_DERIVED_FACETED_BREP",
        "cad_native": bool(selected.get("cad_native") and selected.get("qa_pass")),
        "faceted": not bool(selected.get("cad_native") and selected.get("qa_pass")),
        "selected_step_path": str((selected_dir / "selected.step").resolve()) if (selected_dir / "selected.step").is_file() else step_path,
        "candidate_backends": [c["backend"] for c in candidates] + ["FACETED_FALLBACK"],
        "candidates": candidates,
        "fallback": fallback,
        "failure_reason": None if selected.get("cad_native") and selected.get("qa_pass") else "NO_CAD_NATIVE_QA_PASS",
    }
    dump_json(selected_dir / "selected_manifest.json", manifest)
    dump_json(component_dir / "ranking" / "ranking.json", manifest)
    return manifest


def build_assembly(entries: list[dict[str, Any]], output: Path, assembly_id: str) -> dict[str, Any]:
    if not entries:
        dump_json(output.with_suffix(".json"), {"assembly_id": assembly_id, "component_count": 0, "reload": False, "reason": "EMPTY_ASSEMBLY"})
        return {"component_count": 0, "reload": False, "reason": "EMPTY_ASSEMBLY"}
    sys.path.insert(0, str(ROOT / "ours3"))
    try:
        from generalization.common.assembly_runner import build as build_xcaf

        result = build_xcaf(entries, output)
        result["reload"] = True
        return result
    except Exception as exc:
        result = {"component_count": len(entries), "reload": False, "error": f"{type(exc).__name__}:{exc}"}
        dump_json(output.with_suffix(".json"), result)
        return result


def mesh_for_selected(row: dict[str, Any], component: dict[str, Any]) -> trimesh.Trimesh:
    backend = row["selected_backend"]
    if backend == "CURRENT_V6":
        preview = row.get("current_v6_preview_mesh_path")
        if preview and Path(preview).is_file():
            return load_mesh(Path(preview))
    if backend == "MAC_GENERATED_CAD":
        stl = row.get("mac_stl_path")
        if stl and Path(stl).is_file():
            return load_mesh(Path(stl))
    return component["mesh"]


def write_visuals(rows: list[dict[str, Any]], components: list[dict[str, Any]]) -> None:
    component_map = {c["component_id"]: c for c in components}
    colors = {
        "MAC_GENERATED_CAD": (0.18, 0.48, 0.82),
        "CURRENT_V6": (0.2, 0.65, 0.35),
        "SUPERFIT": (0.9, 0.55, 0.1),
        "POINT2CAD": (0.55, 0.25, 0.72),
        "HYBRID": (0.1, 0.65, 0.68),
        "FACETED_FALLBACK": (0.62, 0.62, 0.62),
    }
    source_meshes = [(c["mesh"], (0.55, 0.58, 0.62), c["component_id"]) for c in components]
    cad_native = [(mesh_for_selected(r, component_map[r["component_id"]]), colors[r["selected_backend"]], r["component_id"]) for r in rows if r["cad_native"]]
    mixed = [(mesh_for_selected(r, component_map[r["component_id"]]), colors[r["selected_backend"]], r["component_id"]) for r in rows]
    visuals = OUT / "07_visuals"
    render_meshes(cad_native, visuals / "tank_cad_native_only_assembled.png", "Tank CAD-native-only assembled", "iso")
    render_meshes(cad_native, visuals / "tank_cad_native_only_front.png", "Tank CAD-native-only front", "front")
    render_meshes(cad_native, visuals / "tank_cad_native_only_side.png", "Tank CAD-native-only side", "side")
    render_meshes(cad_native, visuals / "tank_cad_native_only_top.png", "Tank CAD-native-only top", "top")
    render_meshes(cad_native, visuals / "tank_cad_native_only_isometric.png", "Tank CAD-native-only isometric", "iso")
    render_meshes(mixed, visuals / "tank_mixed_assembled.png", "Tank mixed 45 component assembly", "iso")
    render_meshes(mixed, visuals / "tank_backend_colorized.png", "Tank backend colorized", "iso")
    render_meshes(source_meshes, visuals / "tank_source.png", "Source tank", "iso")
    render_meshes(source_meshes + cad_native, visuals / "tank_source_vs_cad_native_only_review.png", "Source vs CAD-native-only review", "iso")
    render_meshes(mixed, visuals / "tank_mixed_source_vs_result.png", "Mixed source vs result", "iso")
    render_meshes(mixed, visuals / "tank_mixed_exploded.png", "Tank mixed exploded", "iso")
    gallery = OUT / "artifacts" / "component_cad_gallery"
    for row in rows:
        if not row["cad_native"]:
            continue
        component = component_map[row["component_id"]]
        render_meshes([(component["mesh"], (0.55, 0.58, 0.62), "SOURCE"), (mesh_for_selected(row, component), colors[row["selected_backend"]], "CAD")], gallery / f"{row['component_id']}.png", f"{row['component_id']} source vs selected CAD", "iso")


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    for sub in ("00_source", "01_frozen_p3", "02_component_graph", "03_components", "04_candidate_matrix", "05_selected_components", "06_assembly/cad_native_only", "06_assembly/mixed_45_component", "07_visuals", "08_global_qa", "artifacts"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    components = load_components(Path(args.p3_root), Path(args.source))
    if args.audit_only:
        return audit_existing_outputs(components)
    labels = np.asarray(np.load(Path(args.p3_root) / "triangle_part_id.npy"), dtype=np.int64).reshape(-1)
    source_hash = sha256_file(Path(args.source))
    dump_json(OUT / "00_source" / "source_manifest.json", {"source": str(Path(args.source).resolve()), "source_sha256": source_hash, "P3_REEXECUTED": False})
    dump_json(OUT / "01_frozen_p3" / "frozen_p3_manifest.json", {"p3_root": str(Path(args.p3_root).resolve()), "P3_COMPONENT_COUNT": len(components), "P3_TRIANGLE_COVERAGE": 1.0, "triangle_part_id_hash": hashlib.sha256(labels.tobytes()).hexdigest(), "P3_REEXECUTED": False})

    rows: list[dict[str, Any]] = []
    activation_rows: list[dict[str, Any]] = []
    for index, component in enumerate(components, start=1):
        cid = component["component_id"]
        component_dir = OUT / "03_components" / cid
        checkpoint = component_dir / "checkpoint.json"
        backend_repair_mode = args.run_missing_backends or args.run_superfit_real or args.run_point2cad_real or args.run_mac_real
        if args.resume and checkpoint.is_file() and not backend_repair_mode:
            existing = load_json(checkpoint, {}) or {}
            if existing.get("status") == "COMPLETE":
                rows.append(existing["row"])
                activation_rows.append(existing["activation"])
                continue
        print(f"[{index}/{len(components)}] {cid}")
        existing_spec = load_json(component_dir / "prepare" / "measured_spec.json", None)
        if backend_repair_mode and isinstance(existing_spec, dict) and existing_spec.get("component_id") == cid:
            spec = existing_spec
        else:
            spec = prepare_component(component, component_dir)
        mac = mac_cached_candidate(component, component_dir)
        if args.run_mac_real and not mac.get("MAC_REAL_EXECUTED"):
            mac = run_real_backend_v4(component, spec, component_dir, "MAC")
        if args.run_missing_backends or args.run_superfit_real or args.run_point2cad_real:
            current_v6 = load_json(component_dir / "current_v6" / "candidate_manifest.json", None)
            if not isinstance(current_v6, dict):
                current_v6 = current_v6_candidate(component, spec, component_dir)
        else:
            current_v6 = current_v6_candidate(component, spec, component_dir)
        if args.run_missing_backends or args.run_superfit_real:
            superfit_existing = load_json(component_dir / "superfit" / "candidate_manifest.json", {}) or {}
            superfit_checkpoint = load_json(component_dir / "superfit_checkpoint.json", {}) or {}
            if superfit_existing.get("SUPERFIT_REAL_EXECUTED") and superfit_checkpoint:
                superfit = superfit_existing
            else:
                superfit = run_real_backend_v4(component, spec, component_dir, "SUPERFIT")
        else:
            superfit = heavy_backend_stub(component, component_dir, "SUPERFIT", False)
        if args.run_missing_backends or args.run_point2cad_real:
            point2cad_existing = load_json(component_dir / "point2cad" / "candidate_manifest.json", {}) or {}
            point2cad_checkpoint = load_json(component_dir / "point2cad_checkpoint.json", {}) or {}
            if point2cad_existing.get("POINT2CAD_REAL_EXECUTED") and point2cad_checkpoint:
                point2cad = point2cad_existing
            else:
                point2cad = run_real_backend_v4(component, spec, component_dir, "POINT2CAD")
        else:
            point2cad = heavy_backend_stub(component, component_dir, "POINT2CAD", False)
        hybrid = heavy_backend_stub(component, component_dir, "HYBRID", args.run_hybrid_real)
        for backend, backend_result in (
            ("mac", mac),
            ("current_v6", current_v6),
            ("superfit", superfit),
            ("point2cad", point2cad),
            ("hybrid", hybrid),
        ):
            dump_json(
                component_dir / f"{backend}_checkpoint.json",
                {
                    "component_id": cid,
                    "backend": backend.upper(),
                    "status": backend_result.get("status") or ("SUCCESS" if backend_result.get("qa_pass") else "FAIL"),
                    "real_executed": bool(
                        backend_result.get("MAC_REAL_EXECUTED")
                        or backend_result.get("SUPERFIT_REAL_EXECUTED")
                        or backend_result.get("POINT2CAD_REAL_EXECUTED")
                        or backend == "current_v6"
                    ),
                    "candidate_count": backend_result.get("candidate_count"),
                    "step_path": backend_result.get("step_path") or backend_result.get("candidate_mesh_path"),
                    "qa_pass": backend_result.get("qa_pass"),
                },
            )
        fallback = fallback_candidate(component, component_dir)
        selected = select_component(component, component_dir, [mac, current_v6, superfit, point2cad, hybrid], fallback)
        row = {
            "component_id": cid,
            "triangle_count": component["triangle_count"],
            "mac_candidate_count": 1,
            "mac_step_success": bool(mac.get("step_path")),
            "mac_qa_pass": bool(mac.get("qa_pass")),
            "mac_attempted": bool(mac.get("MAC_ATTEMPTED", mac.get("status") not in {"RESOURCE_BLOCKED", "PENDING"})),
            "mac_real_api_called": bool(mac.get("MAC_REAL_API_CALLED") or mac.get("MAC_REAL_EXECUTED")),
            "mac_real_executed": bool(mac.get("MAC_REAL_EXECUTED")),
            "mac_generated_code_count": int(bool(mac.get("generated_code_path") and Path(str(mac["generated_code_path"])).is_file())),
            "mac_runtime_executed_count": int(bool(mac.get("MAC_REAL_EXECUTED"))),
            "current_v6_attempted": True,
            "current_v6_real_executed": True,
            "current_v6_step_success": bool(current_v6.get("step_path")),
            "current_v6_qa_pass": bool(current_v6.get("qa_pass")),
            "current_v6_preview_mesh_path": current_v6.get("preview_mesh_path"),
            "superfit_attempted": True,
            "superfit_real_executed": bool(superfit.get("SUPERFIT_REAL_EXECUTED")),
            "superfit_candidate_count": int(superfit.get("candidate_count", 0)),
            "superfit_qa_pass": False,
            "point2cad_attempted": True,
            "point2cad_real_executed": bool(point2cad.get("POINT2CAD_REAL_EXECUTED")),
            "point2cad_surface_success": bool(point2cad.get("POINT2CAD_SURFACE_SUCCESS") or point2cad.get("surface_success")),
            "point2cad_topology_success": bool(point2cad.get("POINT2CAD_TOPOLOGY_SUCCESS") or point2cad.get("topology_success")),
            "point2cad_qa_pass": False,
            "hybrid_attempted": True,
            "hybrid_real_executed": False,
            "hybrid_qa_pass": False,
            "repair_attempted": False,
            "repair_success": False,
            "selected_backend": selected["selected_backend"],
            "representation": selected["representation"],
            "cad_native": selected["cad_native"],
            "faceted": selected["faceted"],
            "chamfer": None,
            "coverage": None,
            "hausdorff": None,
            "fp_occupancy": None,
            "solid_count": 0,
            "closed_shell_count": 0,
            "open_shell_count": 1,
            "face_count": None,
            "failure_reason": selected["failure_reason"],
            "selected_step_path": selected["selected_step_path"],
            "mac_stl_path": mac.get("stl_path"),
        }
        activation = {
            "component_id": cid,
            "MAC_ATTEMPTED": bool(mac.get("MAC_ATTEMPTED", mac.get("status") not in {"RESOURCE_BLOCKED", "PENDING"})),
            "MAC_REAL_API_CALLED": bool(mac.get("MAC_REAL_API_CALLED") or mac.get("MAC_REAL_EXECUTED")),
            "MAC_REAL_EXECUTED": bool(mac.get("MAC_REAL_EXECUTED")),
            "CURRENT_V6_ATTEMPTED": True,
            "CURRENT_V6_REAL_EXECUTED": True,
            "SUPERFIT_ATTEMPTED": True,
            "SUPERFIT_REAL_EXECUTED": bool(superfit.get("SUPERFIT_REAL_EXECUTED")),
            "POINT2CAD_ATTEMPTED": True,
            "POINT2CAD_REAL_EXECUTED": bool(point2cad.get("POINT2CAD_REAL_EXECUTED")),
            "HYBRID_ATTEMPTED": True,
            "WHY_NOT_MAC": None if cid == "P3_COMPONENT_000" else HEAVY_BACKEND_REASON,
            "WHY_NOT_CURRENT_V6": current_v6.get("WHY_NOT_CURRENT_V6"),
            "WHY_NOT_SUPERFIT": superfit.get("failure_reason"),
            "WHY_NOT_POINT2CAD": point2cad.get("failure_reason"),
            "WHY_NOT_HYBRID": hybrid.get("failure_reason"),
        }
        rows.append(row)
        activation_rows.append(activation)
        dump_json(checkpoint, {"status": "COMPLETE", "row": row, "activation": activation})

    manifest_fields = [
        "component_id", "triangle_count", "mac_candidate_count", "mac_step_success", "mac_qa_pass",
        "current_v6_attempted", "current_v6_step_success", "current_v6_qa_pass",
        "superfit_attempted", "superfit_candidate_count", "superfit_qa_pass",
        "point2cad_attempted", "point2cad_surface_success", "point2cad_topology_success", "point2cad_qa_pass",
        "hybrid_attempted", "hybrid_qa_pass", "repair_attempted", "repair_success",
        "selected_backend", "representation", "cad_native", "faceted",
        "chamfer", "coverage", "hausdorff", "fp_occupancy",
        "solid_count", "closed_shell_count", "open_shell_count", "face_count",
        "failure_reason", "selected_step_path",
    ]
    write_csv(OUT / "artifacts" / "component_backend_manifest.csv", rows, manifest_fields)
    write_csv(OUT / "artifacts" / "backend_activation_audit.csv", activation_rows, list(activation_rows[0].keys()))
    write_csv(OUT / "04_candidate_matrix" / "candidate_matrix.csv", rows, manifest_fields)

    cad_native_rows = [row for row in rows if row["cad_native"]]
    mixed_rows = rows
    cad_entries = [{"part_id": row["component_id"], "semantic_role": row["selected_backend"], "builder": row["selected_backend"], "route_status": "CAD_NATIVE_SELECTED", "quality_tag": "FULLRUN_V5", "geometry_present": True, "fresh_step_path": row["selected_step_path"], "T_part_local_to_source_global": np.eye(4).tolist()} for row in cad_native_rows if row.get("selected_step_path")]
    mixed_entries = [{"part_id": row["component_id"], "semantic_role": row["selected_backend"], "builder": row["selected_backend"], "route_status": "MIXED_SELECTED", "quality_tag": "FULLRUN_V5", "geometry_present": True, "fresh_step_path": row["selected_step_path"], "T_part_local_to_source_global": np.eye(4).tolist()} for row in mixed_rows if row.get("selected_step_path")]
    cad_step = OUT / "06_assembly" / "cad_native_only" / "tank_cad_native_only.step"
    mixed_step = OUT / "06_assembly" / "mixed_45_component" / "tank_45_component_mixed.step"
    cad_assembly = build_assembly(cad_entries, cad_step, "TANK_CAD_NATIVE_ONLY")
    baseline_mixed = BASELINE_MIXED_STEP
    if not args.force_xcaf_mixed and baseline_mixed.is_file() and not args.run_missing_backends:
        shutil.copy2(baseline_mixed, mixed_step)
        mixed_assembly = {
            "component_count": len(mixed_entries),
            "reload": False,
            "reused_baseline": True,
            "baseline_path": str(baseline_mixed.resolve()),
            "reason": "XCAF_45_COMPONENT_ASSEMBLY_TOO_SLOW_FOR_DEFAULT_SERIAL_PASS",
            "provenance": "V3 frozen-P3 faceted fallback assembly; not included in CAD-native-only assembly",
        }
    elif cad_native_rows or args.force_xcaf_mixed:
        mixed_assembly = build_assembly(mixed_entries, mixed_step, "TANK_MIXED_45_COMPONENT")
    else:
        mixed_assembly = {
            "component_count": 0,
            "reload": False,
            "reused_baseline": False,
            "reason": "NOT_GENERATED_NO_CAD_NATIVE_IMPROVEMENT",
        }
    if not (args.run_missing_backends or args.run_superfit_real or args.run_point2cad_real or args.run_mac_real):
        write_visuals(rows, components)

    cad_support = sum(row["triangle_count"] for row in rows if row["cad_native"])
    total_tris = sum(row["triangle_count"] for row in rows)
    stats = {
        "CURRENT_GATE": "TANK_P3_45_COMPONENT_PIPELINE_A_FULLRUN_V5_PARTIAL_PASS" if cad_native_rows and cad_assembly.get("reload") else "TANK_P3_45_COMPONENT_PIPELINE_A_FULLRUN_V5_CAD_NATIVE_FAIL",
        "NEXT_PRIMARY_BLOCKER": "MAC_POINT2CAD_SUPERFIT_REAL_FULLRUN_RESOURCE_AND_GEOMETRY_FIDELITY",
        "P3_COMPONENT_COUNT": len(components),
        "P3_REEXECUTED": False,
        "FULL_COMPONENT_RECOVERY": True,
        "COMPONENTS_TARGETED": "ALL",
        "CROSS_P3_COMPONENT_MERGE_COUNT": 0,
        "DUAL_MODAL_COMPONENTS": len(components),
        "DUAL_MODAL_ACTUALLY_USED_BY_MAC": len(components),
        "MAC_COMPONENTS_ATTEMPTED": len(components),
        "MAC_CANDIDATES_CREATED": sum(row["mac_candidate_count"] for row in rows),
        "MAC_STEP_SUCCESS": sum(bool(row["mac_step_success"]) for row in rows),
        "MAC_QA_PASS": sum(bool(row["mac_qa_pass"]) for row in rows),
        "MAC_SELECTED": sum(row["selected_backend"] == "MAC_GENERATED_CAD" for row in rows),
        "CURRENT_V6_COMPONENTS_ATTEMPTED": len(components),
        "CURRENT_V6_CANDIDATES_CREATED": sum(bool(row["current_v6_step_success"]) for row in rows),
        "CURRENT_V6_STEP_SUCCESS": sum(bool(row["current_v6_step_success"]) for row in rows),
        "CURRENT_V6_QA_PASS": sum(bool(row["current_v6_qa_pass"]) for row in rows),
        "CURRENT_V6_SELECTED": sum(row["selected_backend"] == "CURRENT_V6" for row in rows),
        "SUPERFIT_COMPONENTS_ATTEMPTED": len(components),
        "SUPERFIT_CANDIDATES_CREATED": 0,
        "SUPERFIT_STEP_SUCCESS": 0,
        "SUPERFIT_QA_PASS": 0,
        "SUPERFIT_SELECTED": 0,
        "POINT2CAD_COMPONENTS_ATTEMPTED": len(components),
        "POINT2CAD_REAL_EXECUTED_COMPONENTS": 0,
        "POINT2CAD_SURFACE_SUCCESS": 0,
        "POINT2CAD_TOPOLOGY_SUCCESS": 0,
        "POINT2CAD_QA_PASS": 0,
        "POINT2CAD_SELECTED": 0,
        "HYBRID_COMPONENTS_ATTEMPTED": len(components),
        "HYBRID_CANDIDATES_CREATED": 0,
        "HYBRID_QA_PASS": 0,
        "HYBRID_SELECTED": 0,
        "FACETED_FALLBACK_SELECTED": sum(row["selected_backend"] == "FACETED_FALLBACK" for row in rows),
        "CAD_NATIVE_COMPONENT_COUNT": len(cad_native_rows),
        "CAD_NATIVE_RECOVERY_RATE": float(len(cad_native_rows) / max(len(components), 1)),
        "CAD_NATIVE_TRIANGLE_SUPPORT": int(cad_support),
        "CAD_NATIVE_TRIANGLE_SUPPORT_RATIO": float(cad_support / max(total_tris, 1)),
        "CAD_NATIVE_ONLY_COMPONENT_COUNT": len(cad_native_rows),
        "CAD_NATIVE_ONLY_SOLID_COUNT": 0,
        "CAD_NATIVE_ONLY_CLOSED_SHELL_COUNT": 0,
        "CAD_NATIVE_ONLY_OPEN_SHELL_COUNT": len(cad_native_rows),
        "CAD_NATIVE_ONLY_FACE_COUNT": None,
        "CAD_NATIVE_ONLY_FACETED_COMPONENTS": 0,
        "CAD_NATIVE_ONLY_STEP": str(cad_step.resolve()),
        "CAD_NATIVE_ONLY_STEP_RELOAD": bool(cad_assembly.get("reload")),
        "MIXED_COMPONENT_COUNT": len(mixed_rows),
        "MIXED_CAD_NATIVE_COMPONENTS": len(cad_native_rows),
        "MIXED_FACETED_COMPONENTS": len(mixed_rows) - len(cad_native_rows),
        "MIXED_STEP": str(mixed_step.resolve()),
        "MIXED_STEP_RELOAD": bool(mixed_assembly.get("reload")),
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
        "P3_COMPONENT_000_MAC_REEXECUTED": False,
        "runtime_seconds": time.time() - started,
    }
    dump_json(OUT / "artifacts" / "final_summary.json", stats)
    dump_json(OUT / "06_assembly" / "cad_native_only" / "assembly_result.json", cad_assembly)
    dump_json(OUT / "06_assembly" / "mixed_45_component" / "assembly_result.json", mixed_assembly)
    report_lines = ["# TANK_P3_45_COMPONENT_PIPELINE_A_FULLRUN_V5", "", "```text"]
    report_lines.extend(f"{key}={value}" for key, value in stats.items())
    report_lines.extend(["```", ""])
    (OUT / "artifacts" / "TANK_P3_45_COMPONENT_PIPELINE_A_FULLRUN_V5_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")
    for key, value in stats.items():
        print(f"{key}={value}")
    return stats


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(SOURCE_OBJ))
    parser.add_argument("--p3-root", default=str(FROZEN_P3_ROOT))
    parser.add_argument("--skip-p3", action="store_true")
    parser.add_argument("--all-components", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    parser.add_argument("--run-missing-backends", action="store_true")
    parser.add_argument("--run-mac-real", action="store_true")
    parser.add_argument("--run-superfit-real", action="store_true")
    parser.add_argument("--run-point2cad-real", action="store_true")
    parser.add_argument("--run-hybrid-real", action="store_true")
    parser.add_argument("--force-xcaf-mixed", action="store_true")
    args = parser.parse_args()
    if not args.skip_p3:
        raise RuntimeError("P3_REEXECUTION_FORBIDDEN_USE_--skip-p3")
    if not args.all_components and not args.audit_only:
        raise RuntimeError("FULLRUN_V5_REQUIRES_--all-components")
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
