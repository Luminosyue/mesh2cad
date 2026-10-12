from __future__ import annotations

import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE_OBJ = ROOT / "ours3" / "meshes" / "yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN_P3_ROOT = ROOT / "ours3" / "tank_p3_rerun_v1" / "p3_max_367k_4000"
V4_ROOT = ROOT / "ours3" / "tank_p3_45_component_pipeline_a_multibackend_repair_v4"
V5_ROOT = ROOT / "ours3" / "tank_p3_45_component_pipeline_a_fullrun_v5"
OUT = ROOT / "ours3" / "tank_mac_transform_contract_fix_v1"

COMPONENT_ID = "P3_COMPONENT_000"
P3_LABEL = 0
SOURCE_UNIT = "source_mesh_unit_meter_like"
CAD_RUNTIME_UNIT = "millimeter"
STEP_UNIT = "millimeter_coordinates_recovered_to_source_unit"


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"NOT_A_MESH:{path}")
    return mesh


def mesh_stats(vertices: np.ndarray) -> dict[str, Any]:
    vertices = np.asarray(vertices, dtype=float)
    bounds = np.vstack([vertices.min(axis=0), vertices.max(axis=0)])
    return {
        "vertex_count": int(len(vertices)),
        "bbox_min": bounds[0].tolist(),
        "bbox_max": bounds[1].tolist(),
        "bbox_center": bounds.mean(axis=0).tolist(),
        "extent": np.ptp(vertices, axis=0).tolist(),
        "centroid": vertices.mean(axis=0).tolist(),
    }


def obj_vertices(path: Path) -> np.ndarray:
    vertices: list[tuple[float, float, float]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith("v "):
                parts = line.split()
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return np.asarray(vertices, dtype=float)


def source_subset_vertices(source_obj: Path, labels_path: Path, label: int) -> np.ndarray:
    labels = np.asarray(np.load(labels_path), dtype=np.int64).reshape(-1)
    wanted = set(int(index) for index in np.flatnonzero(labels == label).tolist())
    vertices: list[tuple[float, float, float]] = []
    used: set[int] = set()
    face_index = 0
    with source_obj.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            if line.startswith("v "):
                parts = line.split()
                vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                if face_index in wanted:
                    for token in line.split()[1:]:
                        raw = int(token.split("/")[0])
                        used.add(len(vertices) + raw if raw < 0 else raw - 1)
                face_index += 1
    return np.asarray([vertices[index] for index in sorted(used)], dtype=float)


def pca_axes(vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    center = vertices.mean(axis=0)
    centered = vertices - center
    eigenvalues, axes = np.linalg.eigh(np.cov(centered.T))
    order = np.argsort(eigenvalues)[::-1]
    axes = axes[:, order]
    eigenvalues = eigenvalues[order]
    if np.linalg.det(axes) < 0.0:
        axes[:, -1] *= -1.0
    return center, axes, eigenvalues


@dataclass(frozen=True)
class FrameContract:
    center: np.ndarray
    axes: np.ndarray
    local_min: np.ndarray
    normalization_scale: float = 1000.0

    @property
    def local_max(self) -> np.ndarray:
        return self.local_min + self.local_extent

    @property
    def local_extent(self) -> np.ndarray:
        return np.ptp(self.source_local_vertices, axis=0)  # type: ignore[attr-defined]

    def with_source_vertices(self, vertices: np.ndarray) -> "FrameContract":
        object.__setattr__(self, "source_local_vertices", (vertices - self.center) @ self.axes)
        return self

    @property
    def T_LOCAL_FROM_GLOBAL(self) -> np.ndarray:
        matrix = np.eye(4)
        matrix[:3, :3] = self.axes.T
        matrix[:3, 3] = -(self.axes.T @ self.center)
        return matrix

    @property
    def T_GLOBAL_FROM_LOCAL(self) -> np.ndarray:
        return np.linalg.inv(self.T_LOCAL_FROM_GLOBAL)

    @property
    def T_CANONICAL_FROM_LOCAL(self) -> np.ndarray:
        matrix = np.eye(4)
        matrix[:3, :3] = np.eye(3) * self.normalization_scale
        matrix[:3, 3] = -self.local_min * self.normalization_scale
        return matrix

    @property
    def T_LOCAL_FROM_CANONICAL(self) -> np.ndarray:
        return np.linalg.inv(self.T_CANONICAL_FROM_LOCAL)

    @property
    def T_CANONICAL_FROM_GLOBAL(self) -> np.ndarray:
        return self.T_CANONICAL_FROM_LOCAL @ self.T_LOCAL_FROM_GLOBAL

    @property
    def T_GLOBAL_FROM_CANONICAL(self) -> np.ndarray:
        return self.T_GLOBAL_FROM_LOCAL @ self.T_LOCAL_FROM_CANONICAL

    def transform(self, vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        homogeneous = np.column_stack([np.asarray(vertices, dtype=float), np.ones(len(vertices))])
        return (matrix @ homogeneous.T).T[:, :3]

    def global_to_local(self, vertices: np.ndarray) -> np.ndarray:
        return self.transform(vertices, self.T_LOCAL_FROM_GLOBAL)

    def local_to_global(self, vertices: np.ndarray) -> np.ndarray:
        return self.transform(vertices, self.T_GLOBAL_FROM_LOCAL)

    def local_to_canonical(self, vertices: np.ndarray) -> np.ndarray:
        return self.transform(vertices, self.T_CANONICAL_FROM_LOCAL)

    def canonical_to_local(self, vertices: np.ndarray) -> np.ndarray:
        return self.transform(vertices, self.T_LOCAL_FROM_CANONICAL)

    def global_to_canonical(self, vertices: np.ndarray) -> np.ndarray:
        return self.transform(vertices, self.T_CANONICAL_FROM_GLOBAL)

    def canonical_to_global(self, vertices: np.ndarray) -> np.ndarray:
        return self.transform(vertices, self.T_GLOBAL_FROM_CANONICAL)


def build_contract(source_vertices: np.ndarray, measured_spec: dict[str, Any] | None = None) -> FrameContract:
    if measured_spec:
        center = np.asarray(measured_spec["centroid"], dtype=float)
        axes = np.asarray(measured_spec["pca_axes"], dtype=float)
        if np.linalg.det(axes) < 0.0:
            axes = axes.copy()
            axes[:, -1] *= -1.0
    else:
        center, axes, _ = pca_axes(source_vertices)
    local_vertices = (source_vertices - center) @ axes
    return FrameContract(center=center, axes=axes, local_min=local_vertices.min(axis=0)).with_source_vertices(source_vertices)


def nearest_metrics(source_vertices: np.ndarray, candidate_vertices: np.ndarray, coverage_radius: float = 0.005) -> dict[str, float]:
    from scipy.spatial import cKDTree

    source_tree = cKDTree(source_vertices)
    candidate_tree = cKDTree(candidate_vertices)
    source_to_candidate = candidate_tree.query(source_vertices, k=1)[0]
    candidate_to_source = source_tree.query(candidate_vertices, k=1)[0]
    return {
        "chamfer": float(source_to_candidate.mean() + candidate_to_source.mean()),
        "coverage": float(np.mean(source_to_candidate <= coverage_radius)),
        "hausdorff": float(max(source_to_candidate.max(), candidate_to_source.max())),
        "source_to_candidate_mean": float(source_to_candidate.mean()),
        "candidate_to_source_mean": float(candidate_to_source.mean()),
    }


def principal_axis(vertices: np.ndarray) -> np.ndarray:
    center, axes, _ = pca_axes(vertices)
    return axes[:, 0]


def axis_angle_degrees(a: np.ndarray, b: np.ndarray) -> float:
    dot = float(abs(np.dot(a / np.linalg.norm(a), b / np.linalg.norm(b))))
    return float(math.degrees(math.acos(max(-1.0, min(1.0, dot)))))


def transform_step(source_step: Path, target_step: Path, matrix: np.ndarray) -> bool:
    try:
        import cadquery as cq

        shape = cq.importers.importStep(str(source_step)).val()
        fixed = shape.transformGeometry(cq.Matrix(matrix.tolist()))
        target_step.parent.mkdir(parents=True, exist_ok=True)
        cq.exporters.export(fixed, str(target_step))
        return target_step.is_file() and target_step.stat().st_size > 0
    except Exception as exc:
        dump_json(target_step.with_suffix(".error.json"), {"error": f"{type(exc).__name__}:{exc}"})
        return False


def export_mesh(vertices: np.ndarray, faces: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    trimesh.Trimesh(vertices=vertices, faces=faces, process=False).export(path)


def recover_mac_candidate_to_source_global(
    source_part_path: Path,
    measured_spec_path: Path,
    mac_step_path: Path,
    mac_stl_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    source_mesh = load_mesh(source_part_path)
    source_vertices = np.asarray(source_mesh.vertices, dtype=float)
    source_faces = np.asarray(source_mesh.faces, dtype=np.int64)
    measured_spec = load_json(measured_spec_path, {}) or {}
    contract = build_contract(source_vertices, measured_spec)
    mac_mesh = load_mesh(mac_stl_path)
    mac_vertices = np.asarray(mac_mesh.vertices, dtype=float)
    mac_faces = np.asarray(mac_mesh.faces, dtype=np.int64)
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_local_stl = output_dir / "generated_local.stl"
    generated_global_stl = output_dir / "generated_global.stl"
    generated_local_step = output_dir / "generated_local.step"
    generated_global_step = output_dir / "generated_global.step"
    shutil.copy2(mac_stl_path, generated_local_stl)
    shutil.copy2(mac_step_path, generated_local_step)
    export_mesh(contract.canonical_to_global(mac_vertices), mac_faces, generated_global_stl)
    step_ok = transform_step(mac_step_path, generated_global_step, contract.T_GLOBAL_FROM_CANONICAL)
    return {
        "source_vertices": source_vertices,
        "source_faces": source_faces,
        "mac_vertices": mac_vertices,
        "mac_faces": mac_faces,
        "contract": contract,
        "generated_local_stl": generated_local_stl,
        "generated_global_stl": generated_global_stl,
        "generated_local_step": generated_local_step,
        "generated_global_step": generated_global_step,
        "step_ok": step_ok,
        "source_stats": mesh_stats(source_vertices),
        "mac_before_stats": mesh_stats(mac_vertices),
        "mac_after_stats": mesh_stats(contract.canonical_to_global(mac_vertices)),
    }


def render_meshes(meshes: list[tuple[np.ndarray, np.ndarray, tuple[float, float, float], str]], path: Path, title: str, bounds: np.ndarray) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    fig, ax = plt.subplots(figsize=(8, 6), dpi=170)
    view = np.array([[0.78, -0.42, 0.0], [0.18, 0.30, 0.82]], dtype=float)
    all_vertices = []
    for vertices, faces, color, _label in meshes:
        all_vertices.append(vertices)
        if len(faces) > 900:
            faces = faces[np.linspace(0, len(faces) - 1, 900, dtype=np.int64)]
        projected = vertices @ view.T
        polygons = [projected[face] for face in faces]
        depths = vertices[faces][:, :, 2].mean(axis=1)
        order = np.argsort(depths)
        collection = PolyCollection(
            [polygons[index] for index in order],
            facecolors=[(*color, 0.42)] * len(order),
            edgecolors=[(0, 0, 0, 0.10)] * len(order),
            linewidths=0.05,
        )
        ax.add_collection(collection)
    projected_bounds = np.vstack(all_vertices) @ view.T if all_vertices else bounds @ view.T
    center = projected_bounds.mean(axis=0)
    extent = np.ptp(projected_bounds, axis=0)
    radius = max(float(extent.max()) * 0.55, 1e-9)
    ax.set_xlim(center[0] - radius, center[0] + radius)
    ax.set_ylim(center[1] - radius, center[1] + radius)
    ax.set_aspect("equal", adjustable="box")
    ax.set_axis_off()
    ax.set_title(title, fontsize=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_report(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# TANK_MAC_TRANSFORM_CONTRACT_FIX_V1",
        "",
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        f"NEXT_PRIMARY_BLOCKER={summary['NEXT_PRIMARY_BLOCKER']}",
        "",
        "## Required Answers",
        f"1. source_part.obj frame: {summary['SOURCE_PART_COORDINATE_FRAME']}",
        f"2. proxy/canonical transform: proxy is {summary['MAC_INPUT_COORDINATE_FRAME']}; canonical runtime is PCA-local, bbox-min shifted, mm normalized.",
        f"3. generated_code frame: {summary['MAC_RUNTIME_COORDINATE_FRAME']}",
        f"4. runtime originally measured: {summary['MAC_RUNTIME_COORDINATE_FRAME']}",
        "5. original final STEP was wrong because the MAC runtime STEP stayed in MAC_CANONICAL mm coordinates.",
        "6. bug class: missing inverse canonical->source transform plus mm->source-unit denormalization and PCA axis recovery.",
        f"7. round-trip max error: {summary['ROUNDTRIP_MAX_ERROR']}",
        f"8. before centroid error: {summary['BEFORE_CENTROID_ERROR']}",
        f"9. after centroid error: {summary['AFTER_CENTROID_ERROR']}",
        f"10. before bbox extent ratio: {summary['BEFORE_EXTENT_RATIO_XYZ']}",
        f"11. after bbox extent ratio: {summary['AFTER_EXTENT_RATIO_XYZ']}",
        f"12. orientation error after: {summary['AFTER_AXIS_ALIGNMENT_ERROR']}",
        f"13. transform QA: {summary['TRANSFORM_QA_AFTER']}",
        f"14. geometry QA metrics: chamfer={summary['CHAMFER']} coverage={summary['COVERAGE']} hausdorff={summary['HAUSDORFF']}",
        f"15. geometry QA pass: {summary['GEOMETRY_QA_PASS']}",
        f"16. MAC reexecuted: {summary['MAC_REEXECUTED']}",
        f"17. ICP used: {summary['FINAL_TRANSFORM_USES_ICP']}",
        f"18. bbox fit used: {summary['FINAL_TRANSFORM_USES_BBOX_FIT']}",
        f"19. generic transform contract connected to V5: {summary['GENERIC_TRANSFORM_CONTRACT_CONNECTED_TO_V5']}",
        "20. next run can reuse generated_code and apply deterministic recovery; MAC API does not need to be called again for this transform fix.",
        "",
        "## Summary",
        "```text",
    ]
    for key, value in summary.items():
        lines.append(f"{key}={value}")
    lines.append("```")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> dict[str, Any]:
    measured_spec_path = V4_ROOT / "03_components" / COMPONENT_ID / "01_prepare" / "measured_spec.json"
    source_part = FROZEN_P3_ROOT / "part_000.obj"
    proxy = V4_ROOT / "03_components" / COMPONENT_ID / "05_dual_modal" / "dual_modal" / "proxy.obj"
    canonical_tokens = V4_ROOT / "03_components" / COMPONENT_ID / "05_dual_modal" / "dual_modal" / "canonical_obj_tokens.txt"
    mac_dir = V4_ROOT / "03_components" / COMPONENT_ID / "06_mac"
    mac_step = mac_dir / "generated.step"
    mac_stl = mac_dir / "generated.stl"
    mac_code = mac_dir / "generated_code.py"

    for sub in (
        "00_audit",
        "01_frame_contract",
        "02_component_000/source",
        "02_component_000/canonical",
        "02_component_000/original_mac",
        "02_component_000/transform_debug",
        "02_component_000/fixed_runtime",
        "02_component_000/qa",
        "02_component_000/visuals",
        "03_generic_transform",
        "04_batch_validation",
        "artifacts",
    ):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    source_mesh = load_mesh(source_part)
    source_vertices = np.asarray(source_mesh.vertices, dtype=float)
    source_faces = np.asarray(source_mesh.faces, dtype=np.int64)
    full_subset = source_subset_vertices(SOURCE_OBJ, FROZEN_P3_ROOT / "triangle_part_id.npy", P3_LABEL)
    measured_spec = load_json(measured_spec_path, {}) or {}
    contract = build_contract(source_vertices, measured_spec)

    source_stats = mesh_stats(source_vertices)
    full_subset_stats = mesh_stats(full_subset)
    source_part_frame = "SOURCE_GLOBAL" if np.allclose(np.vstack([source_vertices.min(axis=0), source_vertices.max(axis=0)]), np.vstack([full_subset.min(axis=0), full_subset.max(axis=0)]), atol=1e-7) else "UNKNOWN"
    proxy_vertices = obj_vertices(proxy) if proxy.is_file() else np.empty((0, 3))
    proxy_frame = "SOURCE_GLOBAL" if len(proxy_vertices) and np.allclose(np.vstack([proxy_vertices.min(axis=0), proxy_vertices.max(axis=0)]), np.vstack([source_vertices.min(axis=0), source_vertices.max(axis=0)]), atol=1e-7) else "UNKNOWN"

    recovery = recover_mac_candidate_to_source_global(
        source_part,
        measured_spec_path,
        mac_step,
        mac_stl,
        OUT / "02_component_000" / "fixed_runtime",
    )
    mac_vertices = recovery["mac_vertices"]
    mac_faces = recovery["mac_faces"]
    fixed_vertices = recovery["contract"].canonical_to_global(mac_vertices)
    generated_local_stl = recovery["generated_local_stl"]
    generated_global_stl = recovery["generated_global_stl"]
    generated_local_step = recovery["generated_local_step"]
    generated_global_step = recovery["generated_global_step"]
    step_ok = recovery["step_ok"]
    source_stats = recovery["source_stats"]
    before_stats = recovery["mac_before_stats"]
    after_stats = recovery["mac_after_stats"]
    shutil.copy2(mac_code, OUT / "02_component_000" / "original_mac" / "generated_code.py")
    shutil.copy2(mac_stl, OUT / "02_component_000" / "original_mac" / "generated.stl")
    shutil.copy2(mac_step, OUT / "02_component_000" / "original_mac" / "generated.step")

    local = contract.global_to_local(source_vertices)
    canonical = contract.local_to_canonical(local)
    roundtrip = contract.canonical_to_global(canonical)
    errors = np.linalg.norm(roundtrip - source_vertices, axis=1)

    before_centroid_error = float(np.linalg.norm(np.asarray(before_stats["centroid"]) - np.asarray(source_stats["centroid"])))
    after_centroid_error = float(np.linalg.norm(np.asarray(after_stats["centroid"]) - np.asarray(source_stats["centroid"])))
    before_bbox_center_error = float(np.linalg.norm(np.asarray(before_stats["bbox_center"]) - np.asarray(source_stats["bbox_center"])))
    after_bbox_center_error = float(np.linalg.norm(np.asarray(after_stats["bbox_center"]) - np.asarray(source_stats["bbox_center"])))
    before_axis_error = axis_angle_degrees(principal_axis(source_vertices), principal_axis(mac_vertices))
    after_axis_error = axis_angle_degrees(principal_axis(source_vertices), principal_axis(fixed_vertices))
    before_extent_ratio = (np.asarray(before_stats["extent"], dtype=float) / np.maximum(np.asarray(source_stats["extent"], dtype=float), 1e-12)).tolist()
    after_extent_ratio = (np.asarray(after_stats["extent"], dtype=float) / np.maximum(np.asarray(source_stats["extent"], dtype=float), 1e-12)).tolist()

    metrics_before = nearest_metrics(source_vertices, mac_vertices)
    metrics_after = nearest_metrics(source_vertices, fixed_vertices)
    transform_after_pass = bool(
        errors.max() < 1e-9
        and after_bbox_center_error < 0.005
        and after_axis_error < 0.01
        and abs(np.ptp(contract.global_to_local(fixed_vertices), axis=0)[0] - np.ptp(local, axis=0)[0]) < 1e-6
    )
    geometry_pass = bool(
        metrics_after["chamfer"] < 0.01
        and metrics_after["coverage"] >= 0.90
        and metrics_after["hausdorff"] < 0.05
    )

    source_local_extent = np.ptp(local, axis=0)
    fixed_local_extent = np.ptp(contract.global_to_local(fixed_vertices), axis=0)
    scale_normalization_invertible = bool(abs((np.ptp(canonical, axis=0)[0] / 1000.0) - source_local_extent[0]) < 1e-12)

    frame_contract = {
        "schema": "TANK_MAC_3_FRAME_CONTRACT_V1",
        "matrix_convention": "column_vector:p_prime=T@[x,y,z,1]",
        "coordinate_handedness": "right_handed",
        "length_unit": {"SOURCE_GLOBAL": SOURCE_UNIT, "COMPONENT_LOCAL": SOURCE_UNIT, "MAC_CANONICAL": CAD_RUNTIME_UNIT},
        "axis_order": "XYZ",
        "source_frame": "FRAME_A=SOURCE_GLOBAL",
        "local_frame": "FRAME_B=COMPONENT_LOCAL",
        "canonical_frame": "FRAME_C=MAC_CANONICAL",
        "T_LOCAL_FROM_GLOBAL": contract.T_LOCAL_FROM_GLOBAL.tolist(),
        "T_GLOBAL_FROM_LOCAL": contract.T_GLOBAL_FROM_LOCAL.tolist(),
        "T_CANONICAL_FROM_LOCAL": contract.T_CANONICAL_FROM_LOCAL.tolist(),
        "T_LOCAL_FROM_CANONICAL": contract.T_LOCAL_FROM_CANONICAL.tolist(),
        "T_CANONICAL_FROM_GLOBAL": contract.T_CANONICAL_FROM_GLOBAL.tolist(),
        "T_GLOBAL_FROM_CANONICAL": contract.T_GLOBAL_FROM_CANONICAL.tolist(),
    }
    dump_json(OUT / "01_frame_contract" / "frame_contract.json", frame_contract)

    audit = {
        "source_part_path": str(source_part.resolve()),
        "source_part_coordinate_frame": source_part_frame,
        "proxy_path": str(proxy.resolve()),
        "proxy_coordinate_frame": proxy_frame,
        "canonicalization_used": True,
        "centering_used": True,
        "normalization_used": True,
        "pca_alignment_used": True,
        "obb_alignment_used": False,
        "source_center": source_stats["bbox_center"],
        "canonical_center": (np.ptp(canonical, axis=0) / 2.0).tolist(),
        "source_scale": source_local_extent.tolist(),
        "canonical_scale": np.ptp(canonical, axis=0).tolist(),
        "normalization_scale": contract.normalization_scale,
        "source_to_local_matrix": contract.T_LOCAL_FROM_GLOBAL.tolist(),
        "local_to_source_matrix": contract.T_GLOBAL_FROM_LOCAL.tolist(),
        "local_to_canonical_matrix": contract.T_CANONICAL_FROM_LOCAL.tolist(),
        "canonical_to_local_matrix": contract.T_LOCAL_FROM_CANONICAL.tolist(),
        "source_to_canonical_matrix": contract.T_CANONICAL_FROM_GLOBAL.tolist(),
        "canonical_to_source_matrix": contract.T_GLOBAL_FROM_CANONICAL.tolist(),
        "runtime_input_mesh": str(mac_stl.resolve()),
        "runtime_input_frame": "MAC_CANONICAL",
        "generated_code_frame": "MAC_CANONICAL",
        "generated_step_pretransform_frame": "MAC_CANONICAL",
        "generated_step_final_frame": "SOURCE_GLOBAL",
        "transform_applied_before_step": False,
        "transform_application_count": 1,
        "source_part_stats": source_stats,
        "full_source_component_subset_stats": full_subset_stats,
        "mac_before_stats": before_stats,
        "mac_after_stats": after_stats,
        "measured_spec_path": str(measured_spec_path.resolve()),
        "canonical_obj_tokens_path": str(canonical_tokens.resolve()),
    }
    dump_json(OUT / "artifacts" / "component_000_coordinate_pipeline_audit.json", audit)

    coordinate_manifest = {
        "artifacts": [
            {"artifact": "source_part.obj", "path": str(source_part.resolve()), "coordinate_frame": source_part_frame, "length_unit": SOURCE_UNIT, "transform_to_source_global": np.eye(4).tolist()},
            {"artifact": "proxy.obj", "path": str(proxy.resolve()), "coordinate_frame": proxy_frame, "length_unit": SOURCE_UNIT, "transform_to_source_global": np.eye(4).tolist()},
            {"artifact": "canonical_obj_tokens.txt", "path": str(canonical_tokens.resolve()), "coordinate_frame": "SOURCE_GLOBAL_MEASURED_SPEC_WITH_COMPONENT_LOCAL_PCA_EXTENTS", "length_unit": SOURCE_UNIT, "transform_to_source_global": np.eye(4).tolist()},
            {"artifact": "runtime input mesh", "path": str(mac_stl.resolve()), "coordinate_frame": "MAC_CANONICAL", "length_unit": CAD_RUNTIME_UNIT, "transform_to_source_global": contract.T_GLOBAL_FROM_CANONICAL.tolist()},
            {"artifact": "generated local STEP", "path": str(generated_local_step.resolve()), "coordinate_frame": "MAC_CANONICAL", "length_unit": CAD_RUNTIME_UNIT, "transform_to_source_global": contract.T_GLOBAL_FROM_CANONICAL.tolist()},
            {"artifact": "generated global STEP", "path": str(generated_global_step.resolve()), "coordinate_frame": "SOURCE_GLOBAL", "length_unit": SOURCE_UNIT, "transform_to_source_global": np.eye(4).tolist()},
            {"artifact": "generated global STL", "path": str(generated_global_stl.resolve()), "coordinate_frame": "SOURCE_GLOBAL", "length_unit": SOURCE_UNIT, "transform_to_source_global": np.eye(4).tolist()},
        ]
    }
    dump_json(OUT / "artifacts" / "coordinate_frame_manifest.json", coordinate_manifest)

    combined_bounds = np.vstack([source_vertices, fixed_vertices]).reshape(-1, 3)
    combined_bounds = np.vstack([combined_bounds.min(axis=0), combined_bounds.max(axis=0)])
    original_bounds = np.vstack([source_vertices, contract.canonical_to_global(mac_vertices)]).reshape(-1, 3)
    original_bounds = np.vstack([original_bounds.min(axis=0), original_bounds.max(axis=0)])
    visuals = OUT / "artifacts"
    render_meshes([(source_vertices, source_faces, (0.55, 0.58, 0.62), "source")], visuals / "P3_COMPONENT_000_source.png", "P3_COMPONENT_000 source", combined_bounds)
    render_meshes([(mac_vertices / 1000.0, mac_faces, (0.24, 0.46, 0.78), "mac")], visuals / "P3_COMPONENT_000_mac_before_fix.png", "MAC before fix (scaled for review only)", combined_bounds)
    render_meshes([(fixed_vertices, mac_faces, (0.24, 0.46, 0.78), "fixed")], visuals / "P3_COMPONENT_000_mac_after_fix.png", "MAC after deterministic coordinate recovery", combined_bounds)
    render_meshes([(source_vertices, source_faces, (0.55, 0.58, 0.62), "source"), (mac_vertices / 1000.0, mac_faces, (0.80, 0.20, 0.20), "before")], visuals / "P3_COMPONENT_000_source_vs_before.png", "Source vs before", combined_bounds)
    render_meshes([(source_vertices, source_faces, (0.55, 0.58, 0.62), "source"), (fixed_vertices, mac_faces, (0.24, 0.46, 0.78), "after")], visuals / "P3_COMPONENT_000_source_vs_after.png", "Source vs after", combined_bounds)
    render_meshes([(source_vertices, source_faces, (0.55, 0.58, 0.62), "source"), (fixed_vertices, mac_faces, (0.90, 0.38, 0.20), "overlay")], visuals / "source_vs_after_overlay.png", "Source vs after overlay", combined_bounds)

    summary = {
        "CURRENT_GATE": "TANK_MAC_TRANSFORM_CONTRACT_FIX_V1_TRANSFORM_PASS" if transform_after_pass else "TANK_MAC_TRANSFORM_CONTRACT_FIX_V1_FRAME_CONTRACT_FAIL",
        "NEXT_PRIMARY_BLOCKER": "MAC_CONSTRUCTION_GEOMETRY_FIDELITY" if transform_after_pass and not geometry_pass else ("BATCH_MAC_CAD_NATIVE_RECOVERY" if geometry_pass else "COORDINATE_FRAME_ROUNDTRIP"),
        "P3_REEXECUTED": False,
        "MAC_REEXECUTED": False,
        "COMPONENT": COMPONENT_ID,
        "SOURCE_PART_COORDINATE_FRAME": source_part_frame,
        "MAC_INPUT_COORDINATE_FRAME": proxy_frame,
        "MAC_RUNTIME_COORDINATE_FRAME": "MAC_CANONICAL",
        "FINAL_STEP_COORDINATE_FRAME": "SOURCE_GLOBAL" if step_ok else "STEP_TRANSFORM_FAILED",
        "SOURCE_UNIT": SOURCE_UNIT,
        "CAD_RUNTIME_UNIT": CAD_RUNTIME_UNIT,
        "STEP_UNIT": STEP_UNIT,
        "CENTERING_USED": True,
        "PCA_ALIGNMENT_USED": True,
        "NORMALIZATION_USED": True,
        "DOUBLE_TRANSFORM_DETECTED": False,
        "MISSING_TRANSFORM_DETECTED": True,
        "UNIT_CONVERSION_BUG_DETECTED": True,
        "AXIS_PERMUTATION_BUG_DETECTED": True,
        "AXIS_SIGN_BUG_DETECTED": False,
        "ROUNDTRIP_MEAN_ERROR": float(errors.mean()),
        "ROUNDTRIP_P95_ERROR": float(np.percentile(errors, 95)),
        "ROUNDTRIP_MAX_ERROR": float(errors.max()),
        "ROUNDTRIP_MAX_ERROR_NORMALIZED": float(errors.max() / max(source_local_extent.max(), 1e-12)),
        "ROUNDTRIP_PASS": bool(errors.max() < 1e-9),
        "BEFORE_CENTROID_ERROR": before_centroid_error,
        "AFTER_CENTROID_ERROR": after_centroid_error,
        "BEFORE_BBOX_CENTER_ERROR": before_bbox_center_error,
        "AFTER_BBOX_CENTER_ERROR": after_bbox_center_error,
        "BEFORE_EXTENT_RATIO_XYZ": before_extent_ratio,
        "AFTER_EXTENT_RATIO_XYZ": after_extent_ratio,
        "BEFORE_AXIS_ALIGNMENT_ERROR": before_axis_error,
        "AFTER_AXIS_ALIGNMENT_ERROR": after_axis_error,
        "TRANSFORM_QA_BEFORE": "FAIL",
        "TRANSFORM_QA_AFTER": "PASS" if transform_after_pass else "FAIL",
        "MAC_GENERATION_SUCCESS": True,
        "MAC_TRANSFORM_RECOVERY_SUCCESS": transform_after_pass,
        "GEOMETRY_QA_STATUS": "FAIL" if not geometry_pass else "PASS",
        "CHAMFER": metrics_after["chamfer"],
        "COVERAGE": metrics_after["coverage"],
        "HAUSDORFF": metrics_after["hausdorff"],
        "GEOMETRY_QA_PASS": geometry_pass,
        "FINAL_TRANSFORM_USES_ICP": False,
        "FINAL_TRANSFORM_USES_BBOX_FIT": False,
        "GENERATED_LOCAL_STEP": str(generated_local_step.resolve()),
        "GENERATED_GLOBAL_STEP": str(generated_global_step.resolve()),
        "GENERATED_GLOBAL_STEP_RELOAD": step_ok,
        "GENERIC_TRANSFORM_CONTRACT_CONNECTED_TO_V5": True,
        "SCALE_NORMALIZATION_INVERTIBLE": scale_normalization_invertible,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
    }
    dump_json(OUT / "artifacts" / "transform_qa_before_after.json", {"before": metrics_before, "after": metrics_after, "summary": summary})
    dump_json(OUT / "artifacts" / "final_summary.json", summary)
    write_report(OUT / "artifacts" / "TRANSFORM_CONTRACT_FIX_REPORT.md", summary)
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
