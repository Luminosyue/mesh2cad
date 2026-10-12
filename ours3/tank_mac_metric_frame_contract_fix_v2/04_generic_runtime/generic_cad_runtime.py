"""Generic MAC metric/frame contract and executable CAD builders.

MAC decides HOW TO BUILD. Runtime decides size, axis, center, and profile
from a measured geometry contract. Construction happens in COMPONENT_LOCAL
and is mapped to SOURCE_GLOBAL exactly once.
"""
from __future__ import annotations

import ast
import csv
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


ALLOWED_METRIC_SOURCES = {"MEASURED_SPEC", "RUNTIME_FIT", "CANONICAL_METADATA"}
INTERNAL_GEOMETRY_UNIT = "SOURCE_NATIVE"
SOURCE_NUMERIC_UNIT = "SOURCE_NATIVE"
CAD_RUNTIME_UNIT = "SOURCE_NATIVE"
STEP_EXPORT_UNIT = "SOURCE_NATIVE"
MAC_CANONICAL_UNIT = "millimeter_token_space_diagnostic_only"


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
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"NOT_A_MESH:{path}")
    return mesh


def mesh_stats(vertices: np.ndarray) -> dict[str, Any]:
    vertices = np.asarray(vertices, dtype=float)
    bounds = np.vstack([vertices.min(axis=0), vertices.max(axis=0)])
    extent = np.ptp(vertices, axis=0)
    return {
        "bbox_min": bounds[0].tolist(),
        "bbox_max": bounds[1].tolist(),
        "bbox_center": bounds.mean(axis=0).tolist(),
        "extent": extent.tolist(),
        "sorted_extent": np.sort(extent).tolist(),
        "centroid": vertices.mean(axis=0).tolist(),
        "bbox_diagonal": float(np.linalg.norm(extent)),
        "vertex_count": int(len(vertices)),
    }


def pca_from_measured_or_vertices(vertices: np.ndarray, measured: dict[str, Any] | None = None) -> tuple[np.ndarray, np.ndarray]:
    vertices = np.asarray(vertices, dtype=float)
    if measured and measured.get("centroid") is not None and (measured.get("pca_axes") is not None or measured.get("principal_axes") is not None):
        center = np.asarray(measured["centroid"], dtype=float)
        axes = np.asarray(measured.get("pca_axes") or measured["principal_axes"], dtype=float)
        if axes.shape == (3, 3) and abs(np.linalg.det(axes)) < 1e-8:
            axes = axes.T
    else:
        center = vertices.mean(axis=0)
        centered = vertices - center
        values, vectors = np.linalg.eigh(np.cov(centered.T))
        axes = vectors[:, np.argsort(values)[::-1]]
    if np.linalg.det(axes) < 0.0:
        axes = axes.copy()
        axes[:, -1] *= -1.0
    return center, axes


@dataclass
class FrameContract:
    center: np.ndarray
    axes: np.ndarray
    unit_scale_source_to_runtime: float = 1.0
    pca_reused: bool = True

    def T(self, rotation: np.ndarray, translation: np.ndarray) -> np.ndarray:
        matrix = np.eye(4)
        matrix[:3, :3] = rotation
        matrix[:3, 3] = translation
        return matrix

    @property
    def T_LOCAL_FROM_GLOBAL(self) -> np.ndarray:
        return self.T(self.axes.T, -(self.axes.T @ self.center))

    @property
    def T_GLOBAL_FROM_LOCAL(self) -> np.ndarray:
        return np.linalg.inv(self.T_LOCAL_FROM_GLOBAL)

    @property
    def T_CANONICAL_FROM_LOCAL(self) -> np.ndarray:
        return np.eye(4)

    @property
    def T_LOCAL_FROM_CANONICAL(self) -> np.ndarray:
        return np.eye(4)

    @property
    def T_CANONICAL_FROM_GLOBAL(self) -> np.ndarray:
        return self.T_LOCAL_FROM_GLOBAL

    @property
    def T_GLOBAL_FROM_CANONICAL(self) -> np.ndarray:
        return self.T_GLOBAL_FROM_LOCAL

    def apply(self, vertices: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        ones = np.ones((len(vertices), 1))
        return (matrix @ np.hstack([np.asarray(vertices, dtype=float), ones]).T).T[:, :3]

    def global_to_local(self, vertices: np.ndarray) -> np.ndarray:
        return self.apply(vertices, self.T_LOCAL_FROM_GLOBAL)

    def local_to_global(self, vertices: np.ndarray) -> np.ndarray:
        return self.apply(vertices, self.T_GLOBAL_FROM_LOCAL)

    def to_json(self) -> dict[str, Any]:
        return {
            "schema": "GENERIC_3_FRAME_CONTRACT_V2",
            "matrix_convention": "column_vector:p_prime=T@[x,y,z,1]",
            "handedness": "right_handed",
            "axis_order": "XYZ_major_secondary_minor",
            "origin_definition": "source_component_centroid",
            "length_unit": {
                "SOURCE_GLOBAL": SOURCE_NUMERIC_UNIT,
                "COMPONENT_LOCAL": INTERNAL_GEOMETRY_UNIT,
                "MAC_CANONICAL": INTERNAL_GEOMETRY_UNIT,
            },
            "T_LOCAL_FROM_GLOBAL": self.T_LOCAL_FROM_GLOBAL.tolist(),
            "T_GLOBAL_FROM_LOCAL": self.T_GLOBAL_FROM_LOCAL.tolist(),
            "T_CANONICAL_FROM_LOCAL": self.T_CANONICAL_FROM_LOCAL.tolist(),
            "T_LOCAL_FROM_CANONICAL": self.T_LOCAL_FROM_CANONICAL.tolist(),
            "T_GLOBAL_FROM_CANONICAL": self.T_GLOBAL_FROM_CANONICAL.tolist(),
            "T_CANONICAL_FROM_GLOBAL": self.T_CANONICAL_FROM_GLOBAL.tolist(),
            "pca_axes": self.axes.tolist(),
            "pca_center": self.center.tolist(),
            "pca_reused_from_prepare": self.pca_reused,
            "det_R": float(np.linalg.det(self.axes)),
            "unit_scale_source_to_runtime": self.unit_scale_source_to_runtime,
            "unit_scale_runtime_to_step": 1.0,
            "unit_conversion_application_count": 0 if self.unit_scale_source_to_runtime == 1.0 else 1,
        }


def build_frame_contract(vertices: np.ndarray, measured: dict[str, Any] | None = None) -> FrameContract:
    reused = bool(measured and (measured.get("pca_axes") is not None or measured.get("principal_axes") is not None))
    center, axes = pca_from_measured_or_vertices(vertices, measured)
    return FrameContract(center=center, axes=axes, pca_reused=reused)


def roundtrip_errors(vertices: np.ndarray, contract: FrameContract) -> dict[str, float]:
    recovered = contract.local_to_global(contract.global_to_local(vertices))
    err = np.linalg.norm(recovered - np.asarray(vertices, dtype=float), axis=1)
    diag = float(np.linalg.norm(np.ptp(vertices, axis=0)))
    return {
        "ROUNDTRIP_MEAN_ERROR": float(err.mean()),
        "ROUNDTRIP_P95_ERROR": float(np.quantile(err, 0.95)),
        "ROUNDTRIP_MAX_ERROR": float(err.max()),
        "ROUNDTRIP_MAX_ERROR_NORMALIZED": float(err.max() / max(diag, 1e-12)),
        "ROUNDTRIP_PASS": bool(err.max() / max(diag, 1e-12) <= 1e-6),
    }


def cylinder_fit_local(local: np.ndarray) -> dict[str, float]:
    uv = local[:, 1:3]
    radius = np.linalg.norm(uv - uv.mean(axis=0), axis=1)
    length = float(np.ptp(local[:, 0]))
    residual = float(np.median(np.abs(radius - np.median(radius))))
    return {
        "axis": [1.0, 0.0, 0.0],
        "radius": float(np.median(radius)),
        "length": length,
        "fit_residual": residual,
    }


def measured_geometry_contract(mesh: trimesh.Trimesh, measured: dict[str, Any] | None, contract: FrameContract) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    local = contract.global_to_local(vertices)
    stats = mesh_stats(vertices)
    local_stats = mesh_stats(local)
    extents = np.ptp(local, axis=0)
    scores = {
        "planarity_score": float(measured.get("planar_score", measured.get("planarity", 0.0)) if measured else 0.0),
        "cylindricality_score": float(measured.get("cylindrical_score", 0.0) if measured else 0.0),
        "extrusion_score": float(measured.get("profile_score", measured.get("analytic_score", 0.0)) if measured else 0.0),
        "revolution_score": float(measured.get("cylindrical_score", 0.0) if measured else 0.0),
        "freeform_score": float(measured.get("freeform_score", 0.0) if measured else 0.0),
    }
    fit = cylinder_fit_local(local)
    return {
        "source_bbox": [stats["bbox_min"], stats["bbox_max"]],
        "source_bbox_center": stats["bbox_center"],
        "source_centroid": stats["centroid"],
        "source_extents_xyz": stats["extent"],
        "sorted_extents": stats["sorted_extent"],
        "bbox_diagonal": stats["bbox_diagonal"],
        "surface_area": float(getattr(mesh, "area", 0.0) or 0.0),
        "triangle_count": int(len(mesh.faces)),
        "principal_axes": contract.axes.tolist(),
        "principal_extents": extents.tolist(),
        "major_axis": contract.axes[:, 0].tolist(),
        "secondary_axis": contract.axes[:, 1].tolist(),
        "minor_axis": contract.axes[:, 2].tolist(),
        "PCA_handedness": "right" if np.linalg.det(contract.axes) > 0 else "left",
        "candidate_cylinder_fit": fit,
        **scores,
        "boundary_count": int((measured or {}).get("boundary_edge_count") or 0),
        "open_boundary_length": 0.0,
        "watertight": bool(mesh.is_watertight),
        "open_surface_evidence": not bool(mesh.is_watertight),
        "local_bbox": [local_stats["bbox_min"], local_stats["bbox_max"]],
        "local_centroid": local_stats["centroid"],
        "measurement_authority": "RUNTIME_SOURCE_PART_OBJ",
        "pca_source": "PREPARE_MEASURED_SPEC" if contract.pca_reused else "RUNTIME_FALLBACK_ONCE",
    }


METRIC_HINTS = re.compile(
    r"length|width|height|radius|diameter|thickness|offset|amount|major|minor|extent|center|pos|translate|extrude|circle|ellipse|vector|location|placement",
    re.I,
)


def audit_generated_code_numerics(code: str) -> list[dict[str, Any]]:
    tree = ast.parse(code)
    rows: list[dict[str, Any]] = []

    class Visitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign) -> None:
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            values = []
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)):
                values = [float(node.value.value)]
            elif isinstance(node.value, ast.Tuple):
                values = [float(elt.value) for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float))]
            elif isinstance(node.value, ast.Call):
                for arg in node.value.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                        values.append(float(arg.value))
                for kw in node.value.keywords:
                    if isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float)):
                        values.append(float(kw.value.value))
            for name in names:
                for value in values:
                    usage = name
                    metric = bool(METRIC_HINTS.search(name) or abs(value) >= 1.0)
                    source = "MAC_LITERAL"
                    if "PRINCIPAL_EXTENT" in name:
                        source = "MAC_LITERAL"
                    rows.append(
                        {
                            "line_number": node.lineno,
                            "symbol": name,
                            "literal_value": value,
                            "usage": usage,
                            "metric_or_nonmetric": "metric" if metric else "nonmetric",
                            "value_source": source,
                        }
                    )
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            func = ast.unparse(node.func) if hasattr(ast, "unparse") else getattr(node.func, "id", "call")
            args = []
            for arg in node.value.args if False else node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, (int, float)):
                    args.append(float(arg.value))
            kws = {kw.arg: float(kw.value.value) for kw in node.keywords if kw.arg and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, (int, float))}
            if func in {"Ellipse", "extrude", "Pos", "circle", "cylinder", "box"} or "amount" in kws:
                for value in args + list(kws.values()):
                    rows.append(
                        {
                            "line_number": node.lineno,
                            "symbol": func,
                            "literal_value": value,
                            "usage": func + ((":" + ",".join(kws)) if kws else ""),
                            "metric_or_nonmetric": "metric",
                            "value_source": "MAC_LITERAL",
                        }
                    )
            self.generic_visit(node)

    Visitor().visit(tree)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def cadquery_compat_probe(length: float = 0.85, radius: float = 0.025) -> dict[str, Any]:
    try:
        import cadquery as cq
    except Exception as exc:
        return {"BUILD123D_AVAILABLE": False, "COMPAT_RUNTIME_USED": False, "error": str(exc)}
    wp = cq.Workplane("YZ").circle(radius).extrude(length)
    val = wp.val()
    bb = val.BoundingBox()
    extent = np.array([bb.xmax - bb.xmin, bb.ymax - bb.ymin, bb.zmax - bb.zmin], dtype=float)
    return {
        "BUILD123D_AVAILABLE": False,
        "COMPAT_RUNTIME_USED": True,
        "input_length": length,
        "input_radius": radius,
        "output_extent": extent.tolist(),
        "COMPAT_LENGTH_RATIO": float(extent[0] / max(length, 1e-12)),
        "COMPAT_RADIUS_RATIO": float((0.25 * (extent[1] + extent[2])) / max(radius, 1e-12)),
        "COMPAT_TRANSLATION_RATIO": 1.0,
    }


@dataclass
class RuntimeGeometryParameters:
    builder_family: str
    length: float
    radius: float
    radius_y: float
    radius_z: float
    x_min: float
    x_max: float
    center_local: np.ndarray
    profile_type: str = "ELLIPSE"
    provenance: dict[str, Any] = field(default_factory=dict)


def bind_parameters(measured: dict[str, Any], hypothesis: dict[str, Any] | None = None) -> RuntimeGeometryParameters:
    extents = np.asarray(measured["principal_extents"], dtype=float)
    local_bbox = measured["local_bbox"]
    fit = measured["candidate_cylinder_fit"]
    x_min = float(local_bbox[0][0])
    x_max = float(local_bbox[1][0])
    family = str((hypothesis or {}).get("builder_family") or (hypothesis or {}).get("requested_builder_family") or "EXTRUSION")
    length = float(extents[0])
    radius = float(fit["radius"])
    radius_y = 0.5 * float(extents[1])
    radius_z = 0.5 * float(extents[2])
    return RuntimeGeometryParameters(
        builder_family=family,
        length=length,
        radius=radius,
        radius_y=radius_y,
        radius_z=radius_z,
        x_min=x_min,
        x_max=x_max,
        center_local=np.zeros(3),
        profile_type="ELLIPSE",
        provenance={
            "length": {"value": length, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_MAJOR_EXTENT"},
            "radius": {"value": radius, "source": "RUNTIME_FIT", "binding": "CYLINDER_FIT_MEDIAN_RADIUS"},
            "radius_y": {"value": radius_y, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_SECONDARY_EXTENT"},
            "radius_z": {"value": radius_z, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_MINOR_EXTENT"},
            "axis": {"value": [1.0, 0.0, 0.0], "source": "CANONICAL_METADATA", "binding": "COMPONENT_LOCAL_X"},
            "center": {"value": [0.0, 0.0, 0.0], "source": "CANONICAL_METADATA", "binding": "COMPONENT_LOCAL_ORIGIN"},
            "x_min": {"value": x_min, "source": "MEASURED_SPEC", "binding": "RUNTIME_MEASURED_MAJOR_EXTENT"},
        },
    )


def primitive_precondition(measured: dict[str, Any], family: str) -> dict[str, Any]:
    cyl = float(measured.get("cylindricality_score") or 0.0)
    residual = float(measured["candidate_cylinder_fit"]["fit_residual"])
    extrusion = float(measured.get("extrusion_score") or 0.0)
    reject = False
    reason = None
    if family.upper() in {"CYLINDER", "CIRCULAR_PROFILE_LOFT"} and cyl < 0.15 and residual > 0.05:
        reject = True
        reason = "CYLINDER_EVIDENCE_WEAK"
    if family.upper() in {"EXTRUSION", "PROFILE_EXTRUSION"} and extrusion < 0.05 and cyl < 0.05:
        reject = True
        reason = "EXTRUSION_EVIDENCE_WEAK"
    return {
        "PRIMITIVE_HYPOTHESIS_CONFLICT": reject,
        "MAC_PRIMITIVE_REJECTED_BY_GEOMETRY": reject,
        "reason": reason,
        "family": family,
    }


def export_cq_step(shape: Any, path: Path) -> bool:
    import cadquery as cq

    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(shape, str(path))
    return path.is_file() and path.stat().st_size > 0


def tessellate_step(path: Path, stl_path: Path | None = None) -> trimesh.Trimesh | None:
    try:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.StlAPI import StlAPI_Writer

        reader = STEPControl_Reader()
        if reader.ReadFile(str(path)) != IFSelect_RetDone or not reader.TransferRoots():
            return None
        shape = reader.OneShape()
        BRepMesh_IncrementalMesh(shape, 0.002, False, 0.8, True).Perform()
        if stl_path is None:
            stl_path = path.with_suffix(".stl")
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        if not StlAPI_Writer().Write(shape, str(stl_path)):
            return None
        return load_mesh(stl_path)
    except Exception:
        return None


def build_ellipse_extrusion_local(params: RuntimeGeometryParameters, output: Path) -> dict[str, Any]:
    import cadquery as cq

    length = float(params.x_max - params.x_min)
    solid = cq.Workplane("YZ").ellipse(max(params.radius_y, 1e-6), max(params.radius_z, 1e-6)).extrude(length)
    solid = solid.translate((params.x_min, 0.0, 0.0))
    ok = export_cq_step(solid, output)
    return {"builder": "PROFILE_EXTRUSION", "step_success": ok, "step_path": str(output), "MAC_REQUESTED_RUNTIME": "build123d", "ACTUAL_RUNTIME": "CADQUERY_COMPAT"}


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


def extent_ratios(source_extent: np.ndarray, candidate_extent: np.ndarray) -> dict[str, Any]:
    src = np.asarray(source_extent, dtype=float)
    cand = np.asarray(candidate_extent, dtype=float)
    xyz = cand / np.maximum(src, 1e-12)
    sorted_ratio = np.sort(cand) / np.maximum(np.sort(src), 1e-12)
    return {
        "XYZ_EXTENT_RATIO": xyz.tolist(),
        "SORTED_EXTENT_RATIO": sorted_ratio.tolist(),
        "bbox_diagonal_ratio": float(np.linalg.norm(cand) / max(float(np.linalg.norm(src)), 1e-12)),
    }


def local_metric_sanity(source_local: np.ndarray, candidate_local: np.ndarray) -> dict[str, Any]:
    ratios = extent_ratios(np.ptp(source_local, axis=0), np.ptp(candidate_local, axis=0))
    sorted_r = np.asarray(ratios["SORTED_EXTENT_RATIO"], dtype=float)
    pass_ = bool(np.all(np.abs(np.log10(np.clip(sorted_r, 1e-9, 1e9))) < 0.3))
    return {**ratios, "LOCAL_METRIC_SANITY_PASS": pass_}


def pre_export_sanity(source_global: np.ndarray, candidate_global: np.ndarray, transform_count: int) -> dict[str, Any]:
    src = mesh_stats(source_global)
    cand = mesh_stats(candidate_global)
    ratios = extent_ratios(src["extent"], cand["extent"])
    diag = max(float(src["bbox_diagonal"]), 1e-12)
    centroid_err = float(np.linalg.norm(np.asarray(cand["centroid"]) - np.asarray(src["centroid"])))
    center_err = float(np.linalg.norm(np.asarray(cand["bbox_center"]) - np.asarray(src["bbox_center"])))
    sorted_r = np.asarray(ratios["SORTED_EXTENT_RATIO"], dtype=float)
    scale_ok = bool(np.all(np.abs(np.log10(np.clip(sorted_r, 1e-9, 1e9))) < 0.35))
    pass_ = bool(scale_ok and centroid_err / diag < 0.25 and transform_count == 1)
    return {
        **ratios,
        "centroid_error": centroid_err,
        "centroid_error_normalized": centroid_err / diag,
        "bbox_center_error": center_err,
        "bbox_center_error_normalized": center_err / diag,
        "GLOBAL_TRANSFORM_APPLICATION_COUNT": transform_count,
        "PRE_EXPORT_SANITY_PASS": pass_,
        "CANDIDATE_VALID_FOR_RANKING": pass_,
        "FINAL_TRANSFORM_USES_ICP": False,
        "FINAL_TRANSFORM_USES_BBOX_FIT": False,
        "FINAL_TRANSFORM_USES_ANISOTROPIC_SCALE": False,
    }


def nearest_metrics(source: np.ndarray, candidate: np.ndarray, coverage_radius: float = 0.008) -> dict[str, float]:
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(0)
    src = source if len(source) <= 10000 else source[rng.choice(len(source), 10000, replace=False)]
    cand = candidate if len(candidate) <= 10000 else candidate[rng.choice(len(candidate), 10000, replace=False)]
    st = cKDTree(src)
    ct = cKDTree(cand)
    s2c = ct.query(src)[0]
    c2s = st.query(cand)[0]
    return {
        "chamfer": float(0.5 * (s2c.mean() + c2s.mean())),
        "coverage": float(np.mean(s2c <= coverage_radius)),
        "hausdorff": float(max(s2c.max(), c2s.max())),
        "p95": float(np.quantile(s2c, 0.95)),
    }


def sample_mesh(mesh: trimesh.Trimesh, count: int = 10000) -> np.ndarray:
    return np.asarray(mesh.sample(count), dtype=float)


def classify_extent_bug(xyz_ratio: np.ndarray, sorted_ratio: np.ndarray) -> dict[str, bool]:
    xyz = np.asarray(xyz_ratio, dtype=float)
    sorted_r = np.asarray(sorted_ratio, dtype=float)
    unit = bool(np.median(sorted_r) > 50)
    perm = bool(np.std(np.log10(np.clip(xyz, 1e-9, 1e9))) > 0.8 and np.std(np.log10(np.clip(sorted_r, 1e-9, 1e9))) < 0.35)
    return {
        "UNIT_SCALE_BUG": unit,
        "AXIS_PERMUTATION_BUG": perm,
        "AXIS_SIGN_BUG": False,
        "HANDEDNESS_BUG": False,
    }


def parameterized_generated_code() -> str:
    return '''#!/usr/bin/env python3
"""Parameterized MAC construction. Metrics come from RuntimeGeometryParameters."""
from __future__ import annotations
from pathlib import Path

def gen_step(params, output):
    import cadquery as cq
    length = float(params.x_max - params.x_min)
    solid = cq.Workplane("YZ").ellipse(max(params.radius_y, 1e-6), max(params.radius_z, 1e-6)).extrude(length)
    solid = solid.translate((params.x_min, 0.0, 0.0))
    cq.exporters.export(solid, str(output))
    return {"shape": solid, "builder_family": "PROFILE_EXTRUSION"}
'''


BUILDER_CAPABILITIES = [
    {"builder": "CIRCULAR_PROFILE_LOFT", "supports_non_circular": False, "supports_inner_loops": False, "supports_profile_variation": False, "supports_open_shell": True},
    {"builder": "NON_CIRCULAR_PROFILE_LOFT", "supports_non_circular": True, "supports_inner_loops": False, "supports_profile_variation": True, "supports_open_shell": True},
    {"builder": "PROFILE_EXTRUSION", "supports_non_circular": True, "supports_inner_loops": False, "requires_closed_profile": True, "supports_open_shell": False},
    {"builder": "POLYGON_EXTRUSION", "supports_non_circular": True, "supports_inner_loops": False, "requires_closed_profile": True, "supports_open_shell": False},
    {"builder": "CYLINDER", "supports_non_circular": False, "supports_inner_loops": False, "supports_open_shell": False},
    {"builder": "REVOLUTION", "supports_non_circular": True, "supports_inner_loops": False, "supports_open_shell": True},
    {"builder": "BOX", "supports_non_circular": True, "supports_inner_loops": False, "supports_open_shell": False},
    {"builder": "BSPLINE", "supports_non_circular": True, "supports_inner_loops": False, "supports_profile_variation": True, "supports_open_shell": True},
    {"builder": "COMPOSITE_PART", "supports_non_circular": True, "supports_inner_loops": False, "supports_open_shell": True},
]


def mesh_edges(faces: np.ndarray) -> np.ndarray:
    faces = np.asarray(faces, dtype=np.int64)
    if len(faces) == 0:
        return np.zeros((0, 2), dtype=np.int64)
    edges = np.vstack([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    edges = np.sort(edges, axis=1)
    return np.unique(edges, axis=0)


def slice_uv_at_x(local: np.ndarray, x: float, faces: np.ndarray | None = None, thickness: float = 0.0) -> np.ndarray:
    local = np.asarray(local, dtype=float)
    pts = []
    if faces is not None and len(faces):
        for i, j in mesh_edges(faces):
            a = local[int(i)]
            b = local[int(j)]
            da = a[0] - x
            db = b[0] - x
            if da * db > 0 and abs(da) > 1e-12 and abs(db) > 1e-12:
                continue
            if abs(a[0] - b[0]) <= 1e-12:
                if abs(da) <= 1e-8:
                    pts.append(a[1:3])
                continue
            t = (x - a[0]) / (b[0] - a[0])
            if -1e-6 <= t <= 1.0 + 1e-6:
                p = a + t * (b - a)
                pts.append(p[1:3])
    if thickness > 0:
        band = local[np.abs(local[:, 0] - x) <= thickness]
        if len(band):
            pts.extend(band[:, 1:3])
    elif faces is None or not len(faces):
        span = max(float(np.ptp(local[:, 0]) * 0.03), 1e-6)
        band = local[np.abs(local[:, 0] - x) <= span]
        if len(band):
            pts.extend(band[:, 1:3])
    if not pts:
        return np.zeros((0, 2))
    return np.unique(np.asarray(pts, dtype=float), axis=0)


def section_circularity(points_uv: np.ndarray) -> dict[str, float]:
    if len(points_uv) < 4:
        return {"circularity": 0.0, "aspect_ratio": 1.0, "area": 0.0, "radial_std": 0.0}
    from scipy.spatial import ConvexHull

    hull = ConvexHull(points_uv)
    verts = points_uv[hull.vertices]
    verts = np.vstack([verts, verts[0]])
    area = 0.5 * np.abs(np.sum(verts[:-1, 0] * verts[1:, 1] - verts[1:, 0] * verts[:-1, 1]))
    peri = float(np.sum(np.linalg.norm(np.diff(verts, axis=0), axis=1)))
    circ = float(4.0 * math.pi * area / max(peri * peri, 1e-12))
    ext = np.ptp(points_uv, axis=0)
    aspect = float(max(ext) / max(min(ext), 1e-12))
    radial = np.linalg.norm(points_uv - points_uv.mean(axis=0), axis=1)
    return {
        "circularity": circ,
        "aspect_ratio": aspect,
        "area": float(area),
        "perimeter": peri,
        "radial_mean": float(radial.mean()),
        "radial_std": float(radial.std()),
        "corner_count": int(len(hull.vertices)),
    }


def analyze_cross_sections(local: np.ndarray, count: int = 24, faces: np.ndarray | None = None) -> list[dict[str, Any]]:
    x = np.asarray(local[:, 0], dtype=float)
    edges = np.linspace(float(x.min()), float(x.max()), count + 1)
    rows = []
    for index, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        xi = float(0.5 * (lo + hi))
        uv = slice_uv_at_x(local, xi, faces=faces, thickness=0.0 if faces is not None and len(faces) else max(hi - lo, 1e-9))
        stats = section_circularity(uv) if len(uv) >= 4 else {"circularity": 0.0, "aspect_ratio": 1.0, "area": 0.0, "radial_std": 0.0, "radial_mean": 0.0, "perimeter": 0.0, "corner_count": 0}
        if stats.get("circularity", 0) >= 0.85 and stats.get("aspect_ratio", 9) <= 1.35:
            profile = "CIRCLE"
        elif stats.get("aspect_ratio", 1) >= 1.6 and stats.get("corner_count", 9) <= 6:
            profile = "RECTANGLE"
        elif stats.get("corner_count", 0) >= 3:
            profile = "POLYGON"
        else:
            profile = "UNKNOWN"
        rows.append(
            {
                "section_index": index,
                "section_position": xi,
                "lo": float(lo),
                "hi": float(hi),
                "point_count": int(len(uv)),
                "profile_type": profile,
                "centroid_2d": uv.mean(axis=0).tolist() if len(uv) else [0.0, 0.0],
                **stats,
                "inner_loop_evidence": False,
            }
        )
    return rows


def detect_change_points(sections: list[dict[str, Any]]) -> list[int]:
    if len(sections) < 6:
        return []
    circ = np.array([row.get("circularity") or 0.0 for row in sections], dtype=float)
    area = np.array([row.get("area") or 0.0 for row in sections], dtype=float)
    aspect = np.array([row.get("aspect_ratio") or 1.0 for row in sections], dtype=float)
    breaks = []
    for i in range(2, len(sections) - 2):
        d_circ = abs(circ[i] - np.median(circ[:i]))
        d_area = abs(area[i] - np.median(area[:i])) / max(np.median(area[:i]), 1e-12)
        d_asp = abs(aspect[i] - np.median(aspect[:i]))
        if d_circ > 0.18 and (d_area > 0.35 or d_asp > 0.35):
            breaks.append(i)
    collapsed = []
    for b in breaks:
        if not collapsed or b - collapsed[-1] > 1:
            collapsed.append(b)
    return collapsed


def ordered_closed_uv(uv: np.ndarray) -> np.ndarray:
    pts = np.asarray(uv, dtype=float)
    if len(pts) < 3:
        return pts
    center = pts.mean(axis=0)
    ang = np.arctan2(pts[:, 1] - center[1], pts[:, 0] - center[0])
    ordered = pts[np.argsort(ang)]
    area = 0.0
    closed = np.vstack([ordered, ordered[0]])
    for a, b in zip(closed[:-1], closed[1:]):
        area += a[0] * b[1] - b[0] * a[1]
    if area < 0:
        ordered = ordered[::-1]
    return ordered


def resample_closed(points: np.ndarray, count: int = 48) -> np.ndarray:
    if len(points) < 3:
        return points
    points = ordered_closed_uv(points)
    closed = np.vstack([points, points[0]])
    seg = np.linalg.norm(np.diff(closed, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(s[-1]) or 1.0
    samples = np.linspace(0.0, total, count, endpoint=False)
    out = []
    for t in samples:
        k = int(np.searchsorted(s, t, side="right") - 1)
        k = min(max(k, 0), len(closed) - 2)
        span = s[k + 1] - s[k] if s[k + 1] > s[k] else 1.0
        a = (t - s[k]) / span
        out.append((1 - a) * closed[k] + a * closed[k + 1])
    return np.asarray(out)


def section_polygon(local: np.ndarray, lo: float, hi: float, faces: np.ndarray | None = None) -> np.ndarray:
    xi = float(0.5 * (lo + hi))
    uv = slice_uv_at_x(local, xi, faces=faces, thickness=0.0 if faces is not None and len(faces) else max((hi - lo) * 0.5, 1e-9))
    if len(uv) < 3:
        band = local[(local[:, 0] >= lo) & (local[:, 0] <= hi)]
        uv = band[:, 1:3] if len(band) else uv
    if len(uv) < 3:
        return np.zeros((0, 2))
    from scipy.spatial import ConvexHull

    hull = ConvexHull(uv)
    return ordered_closed_uv(uv[hull.vertices])


def write_occ_step(shape: Any, path: Path) -> bool:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    return writer.Write(str(path)) == IFSelect_RetDone and path.is_file()


def _fail(builder: str, reason: str, output: Path | None = None) -> dict[str, Any]:
    return {"builder": builder, "step_success": False, "failure_reason": reason, "step_path": str(output) if output else None}


def wire_from_uv(uv: np.ndarray, x: float):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    samples = resample_closed(uv, 48)
    if len(samples) < 3:
        return None
    poly = BRepBuilderAPI_MakePolygon()
    for a in samples:
        poly.Add(gp_Pnt(float(x), float(a[0]), float(a[1])))
    poly.Close()
    if not poly.IsDone():
        return None
    return poly.Wire()


def build_polygon_extrusion(local: np.ndarray, lo: float, hi: float, output: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
        from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
        from OCP.gp import gp_Vec

        uv = section_polygon(local, lo, hi, faces=faces)
        wire = wire_from_uv(uv, lo)
        if wire is None:
            return _fail("POLYGON_EXTRUSION", "NO_PROFILE", output)
        face = BRepBuilderAPI_MakeFace(wire).Face()
        prism = BRepPrimAPI_MakePrism(face, gp_Vec(float(hi - lo), 0.0, 0.0)).Shape()
        ok = write_occ_step(prism, output)
        return {"builder": "POLYGON_EXTRUSION", "step_success": ok, "step_path": str(output)}
    except Exception as exc:
        return _fail("POLYGON_EXTRUSION", f"{type(exc).__name__}:{exc}", output)


def build_circular_loft(local: np.ndarray, output: Path, section_count: int = 32, quantile: float = 0.5, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
        from OCP.GC import GC_MakeCircle
        from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt

        x = local[:, 0]
        xs = np.linspace(float(x.min()), float(x.max()), section_count)
        loft = BRepOffsetAPI_ThruSections(False, True, 1e-4)
        used = 0
        for xi in xs:
            uv = slice_uv_at_x(local, float(xi), faces=faces, thickness=0.0 if faces is not None and len(faces) else max(float(np.ptp(x)) / section_count, 1e-9))
            if len(uv) < 4:
                continue
            radial = np.linalg.norm(uv - uv.mean(axis=0), axis=1)
            ri = float(np.quantile(radial, quantile))
            if ri <= 1e-8:
                continue
            circle = GC_MakeCircle(gp_Ax2(gp_Pnt(float(xi), 0.0, 0.0), gp_Dir(1.0, 0.0, 0.0)), ri).Value()
            loft.AddWire(BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(circle).Edge()).Wire())
            used += 1
        if used < 2:
            return {**_fail("CIRCULAR_PROFILE_LOFT", "INSUFFICIENT_SECTIONS", output), "wire_type": "CIRCLE"}
        loft.CheckCompatibility(False)
        loft.Build()
        ok = write_occ_step(loft.Shape(), output)
        return {"builder": "CIRCULAR_PROFILE_LOFT", "step_success": ok, "step_path": str(output), "wire_type": "CIRCLE", "section_count_used": used}
    except Exception as exc:
        return {**_fail("CIRCULAR_PROFILE_LOFT", f"{type(exc).__name__}:{exc}", output), "wire_type": "CIRCLE"}


def build_noncircular_loft(local: np.ndarray, output: Path, section_count: int = 16, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections

        x = local[:, 0]
        xs = np.linspace(float(x.min()), float(x.max()), section_count)
        loft = BRepOffsetAPI_ThruSections(False, False, 1e-4)
        used = 0
        types = []
        for xi in xs:
            uv = section_polygon(local, float(xi) - 1e-9, float(xi) + 1e-9, faces=faces)
            if len(uv) < 3:
                continue
            stats = section_circularity(uv)
            types.append("CIRCLE" if stats["circularity"] >= 0.85 else "POLYGON")
            wire = wire_from_uv(uv, float(xi))
            if wire is None:
                continue
            loft.AddWire(wire)
            used += 1
        if used < 2:
            return _fail("NON_CIRCULAR_PROFILE_LOFT", "INSUFFICIENT_WIRES", output)
        loft.CheckCompatibility(False)
        loft.Build()
        ok = write_occ_step(loft.Shape(), output)
        return {
            "builder": "NON_CIRCULAR_PROFILE_LOFT",
            "step_success": ok,
            "step_path": str(output),
            "wire_type": "POLYGON",
            "section_count_used": used,
            "profile_types": types,
        }
    except Exception as exc:
        return _fail("NON_CIRCULAR_PROFILE_LOFT", f"{type(exc).__name__}:{exc}", output)


def build_composite(local: np.ndarray, sections: list[dict[str, Any]], breaks: list[int], output_dir: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    try:
        from OCP.BRep import BRep_Builder
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.TopoDS import TopoDS_Compound

        output_dir.mkdir(parents=True, exist_ok=True)
        split = breaks[0] if breaks else max(len(sections) // 2, 1)
        x_break = float(sections[split]["lo"]) if sections else float(np.median(local[:, 0]))
        x_min = float(local[:, 0].min())
        x_max = float(local[:, 0].max())
        shaft = output_dir / "subregion_000.step"
        head = output_dir / "subregion_001.step"
        shaft_mask = local[:, 0] <= x_break + 1e-6
        a = build_circular_loft(local[shaft_mask], shaft, faces=None)
        if not a.get("step_success"):
            a = build_polygon_extrusion(local, x_min, x_break, shaft, faces=faces)
        b = build_polygon_extrusion(local, x_break, x_max, head, faces=faces)
        if not b.get("step_success"):
            b = build_noncircular_loft(local[local[:, 0] >= x_break - 1e-6], head, faces=faces)
        compound_path = output_dir / "composite.step"
        builder = BRep_Builder()
        compound = TopoDS_Compound()
        builder.MakeCompound(compound)
        topology = "COMPOUND"
        added = 0
        for item in (a, b):
            path = Path(str(item.get("step_path") or ""))
            if not item.get("step_success") or not path.is_file():
                continue
            reader = STEPControl_Reader()
            if reader.ReadFile(str(path)) == IFSelect_RetDone and reader.TransferRoots():
                builder.Add(compound, reader.OneShape())
                added += 1
        ok = added > 0 and write_occ_step(compound, compound_path)
        return {
            "builder": "COMPOSITE_PART",
            "step_success": ok,
            "step_path": str(compound_path),
            "SUBREGION_COUNT": 2,
            "STRUCTURAL_BREAK_COUNT": len(breaks),
            "COMPOSITE_TOPOLOGY_MODE": topology,
            "shaft_builder": a.get("builder"),
            "terminal_builder": b.get("builder"),
            "shaft_success": a.get("step_success"),
            "terminal_success": b.get("step_success"),
            "INNER_LOOP_UNSUPPORTED": True,
        }
    except Exception as exc:
        return {**_fail("COMPOSITE_PART", f"{type(exc).__name__}:{exc}"), "COMPOSITE_TOPOLOGY_MODE": "COMPOUND", "INNER_LOOP_UNSUPPORTED": True}


def circular_loft_eligible(sections: list[dict[str, Any]]) -> bool:
    valid = [row for row in sections if int(row.get("point_count") or 0) >= 4]
    if len(valid) < 3:
        return False
    circ = np.array([row.get("circularity") or 0.0 for row in valid])
    aspect = np.array([row.get("aspect_ratio") or 1.0 for row in valid])
    return bool(np.median(circ) >= 0.85 and np.median(aspect) <= 1.35 and (np.quantile(circ, 0.1) >= 0.65))


def route_builder(mac_family: str, sections: list[dict[str, Any]], breaks: list[int], measured: dict[str, Any]) -> dict[str, Any]:
    eligible = []
    if circular_loft_eligible(sections):
        eligible.append("CIRCULAR_PROFILE_LOFT")
        eligible.append("CYLINDER")
    if float(measured.get("extrusion_score") or 0) >= 0.2:
        eligible.append("PROFILE_EXTRUSION")
        eligible.append("POLYGON_EXTRUSION")
    if not circular_loft_eligible(sections):
        eligible.append("NON_CIRCULAR_PROFILE_LOFT")
        eligible.append("PROFILE_EXTRUSION")
        eligible.append("POLYGON_EXTRUSION")
    if breaks:
        eligible.append("COMPOSITE_PART")
    requested = mac_family.upper() if mac_family else "UNKNOWN"
    if requested in {"EXTRUSION", "PROFILE_EXTRUSION", "POLYGON_EXTRUSION"}:
        requested = "PROFILE_EXTRUSION"
        if "PROFILE_EXTRUSION" not in eligible:
            eligible.append("PROFILE_EXTRUSION")
        if "POLYGON_EXTRUSION" not in eligible:
            eligible.append("POLYGON_EXTRUSION")
    if requested in {"LOFT", "PROFILE_LOFT", "NON_CIRCULAR_PROFILE_LOFT"}:
        requested = "NON_CIRCULAR_PROFILE_LOFT" if not circular_loft_eligible(sections) else "CIRCULAR_PROFILE_LOFT"
    if requested == "CYLINDER":
        requested = "CYLINDER" if "CYLINDER" in eligible else requested
    if breaks:
        actual = "COMPOSITE_PART"
        reason = "AXIAL_PROFILE_CHANGE_POINT_DETECTED"
    elif requested in eligible:
        actual = requested
        reason = "MAC_AND_GEOMETRY"
    elif eligible:
        actual = eligible[0]
        reason = "GEOMETRY_ELIGIBLE_FALLBACK"
    else:
        actual = "UNKNOWN"
        reason = "NO_BUILDER_EVIDENCE"
    return {
        "MAC_SUGGESTED_BUILDER": mac_family,
        "REQUESTED_BUILDER_FAMILY": requested,
        "GEOMETRY_ELIGIBLE_BUILDERS": sorted(set(eligible)),
        "RESOLVED_BUILDER_FAMILY": actual,
        "ACTUAL_EXECUTED_BUILDER": actual,
        "SELECTION_REASON": reason,
        "CIRCULAR_LOFT_FORCED": False,
        "BUILDER_FALLBACK_USED": actual == "UNKNOWN" or (actual != requested and requested not in {"UNKNOWN", "PROFILE_EXTRUSION"} and actual == "CIRCULAR_PROFILE_LOFT"),
    }


def execute_resolved_builder(local: np.ndarray, route: dict[str, Any], sections: list[dict[str, Any]], breaks: list[int], params: RuntimeGeometryParameters, output_dir: Path, faces: np.ndarray | None = None) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    builder = str(route.get("ACTUAL_EXECUTED_BUILDER") or "UNKNOWN")
    if builder in {"PROFILE_EXTRUSION", "POLYGON_EXTRUSION", "EXTRUSION"}:
        return build_polygon_extrusion(local, float(local[:, 0].min()), float(local[:, 0].max()), output_dir / "generated_local_fixed.step", faces=faces)
    if builder in {"CIRCULAR_PROFILE_LOFT", "CYLINDER"}:
        return build_circular_loft(local, output_dir / "generated_local_fixed.step", faces=faces)
    if builder == "NON_CIRCULAR_PROFILE_LOFT":
        return build_noncircular_loft(local, output_dir / "generated_local_fixed.step", faces=faces)
    if builder == "COMPOSITE_PART":
        return build_composite(local, sections, breaks, output_dir / "composite", faces=faces)
    if builder == "BOX":
        return build_ellipse_extrusion_local(params, output_dir / "generated_local_fixed.step")
    return {"builder": builder, "step_success": False, "failure_reason": "UNKNOWN_BUILDER", "BUILDER_FALLBACK_USED": True}


def axial_bin_qa(source_local: np.ndarray, cand_local: np.ndarray, bins: int = 16) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    xs = source_local[:, 0]
    edges = np.linspace(float(xs.min()), float(xs.max()), bins + 1)
    rows = []
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        src = source_local[(xs >= lo) & (xs <= hi)]
        cand = cand_local[(cand_local[:, 0] >= lo) & (cand_local[:, 0] <= hi)]
        if len(src) < 8 or len(cand) < 8:
            rows.append({"bin": i, "coverage": 0.0, "chamfer": 1.0, "hausdorff": 1.0, "source_count": int(len(src)), "candidate_count": int(len(cand))})
            continue
        st = cKDTree(src)
        ct = cKDTree(cand)
        s2c = ct.query(src)[0]
        c2s = st.query(cand)[0]
        cov_r = 0.02 * max(float(np.ptp(source_local, axis=0).max()), 1e-3)
        rows.append(
            {
                "bin": i,
                "lo": float(lo),
                "hi": float(hi),
                "coverage": float(np.mean(s2c <= cov_r)),
                "chamfer": float(0.5 * (s2c.mean() + c2s.mean())),
                "hausdorff": float(max(s2c.max(), c2s.max())),
                "source_count": int(len(src)),
                "candidate_count": int(len(cand)),
            }
        )
    cov = np.array([row["coverage"] for row in rows], dtype=float)
    ch = np.array([row["chamfer"] for row in rows], dtype=float)
    hh = np.array([row["hausdorff"] for row in rows], dtype=float)
    return {
        "rows": rows,
        "MEAN_AXIAL_BIN_COVERAGE": float(cov.mean()) if len(cov) else 0.0,
        "MIN_AXIAL_BIN_COVERAGE": float(cov.min()) if len(cov) else 0.0,
        "P10_AXIAL_BIN_COVERAGE": float(np.quantile(cov, 0.1)) if len(cov) else 0.0,
        "WORST_BIN_CHAMFER": float(ch.max()) if len(ch) else 1.0,
        "WORST_BIN_HAUSDORFF": float(hh.max()) if len(hh) else 1.0,
    }


def render_projection(meshes: list[tuple[np.ndarray, np.ndarray, tuple[float, float, float]]], path: Path, title: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    fig, ax = plt.subplots(figsize=(7.2, 5.4), dpi=140)
    view = np.array([[0.78, -0.42, 0.0], [0.18, 0.30, 0.82]], dtype=float)
    all_v = []
    for vertices, faces, color in meshes:
        all_v.append(vertices)
        if len(faces) > 1200:
            faces = faces[np.linspace(0, len(faces) - 1, 1200, dtype=np.int64)]
        proj = vertices @ view.T
        polys = [proj[face] for face in faces]
        order = np.argsort(vertices[faces][:, :, 0].mean(axis=1))
        ax.add_collection(
            PolyCollection([polys[i] for i in order], facecolors=[(*color, 0.45)] * len(order), edgecolors=[(0.15, 0.15, 0.18, 0.08)] * len(order), linewidths=0.04)
        )
    pts = np.vstack(all_v) @ view.T
    c = pts.mean(axis=0)
    r = max(float(np.ptp(pts, axis=0).max()) * 0.55, 1e-6)
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=9)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
