from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import cKDTree

OUT = Path(__file__).resolve().parent / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20260802)


def subdivide_mesh(mesh: trimesh.Trimesh, iterations: int) -> trimesh.Trimesh:
    out = mesh.copy()
    for _ in range(iterations):
        out = out.subdivide()
    out.remove_unreferenced_vertices()
    return out


def make_highpoly_table() -> trimesh.Trimesh:
    top = trimesh.creation.box(extents=[4.0, 2.5, 0.30])
    top.apply_translation([0.0, 0.0, 3.05])
    top = subdivide_mesh(top, 6)

    parts = [top]
    for x in (-1.65, 1.65):
        for y in (-0.90, 0.90):
            leg = trimesh.creation.cylinder(radius=0.18, height=3.0, sections=256)
            leg.apply_translation([x, y, 1.50])
            parts.append(leg)

    assembly = trimesh.util.concatenate(parts)
    assembly.metadata["description"] = "Synthetic high-poly table: 1 box tabletop + 4 cylindrical legs"
    return assembly


def vertex_cluster_simplify(mesh: trimesh.Trimesh, cell_size: float) -> trimesh.Trimesh:
    """Simple dependency-free vertex clustering baseline.

    This is intentionally a baseline, not a replacement for QEM/CGAL/PyMeshLab.
    """
    v = np.asarray(mesh.vertices)
    f = np.asarray(mesh.faces)
    vmin = v.min(axis=0)
    keys = np.floor((v - vmin) / cell_size).astype(np.int64)
    _, inverse = np.unique(keys, axis=0, return_inverse=True)
    n = inverse.max() + 1

    counts = np.bincount(inverse, minlength=n).astype(np.float64)
    new_v = np.column_stack([
        np.bincount(inverse, weights=v[:, i], minlength=n) / np.maximum(counts, 1.0)
        for i in range(3)
    ])
    new_f = inverse[f]
    nondeg = (
        (new_f[:, 0] != new_f[:, 1])
        & (new_f[:, 1] != new_f[:, 2])
        & (new_f[:, 0] != new_f[:, 2])
    )
    new_f = new_f[nondeg]

    # Remove duplicate faces regardless of winding.
    canon = np.sort(new_f, axis=1)
    _, keep = np.unique(canon, axis=0, return_index=True)
    new_f = new_f[np.sort(keep)]

    out = trimesh.Trimesh(vertices=new_v, faces=new_f, process=True)
    out.remove_unreferenced_vertices()
    return out


def simplify_by_component(mesh: trimesh.Trimesh, target_cells_across_diag: int = 80) -> trimesh.Trimesh:
    components = mesh.split(only_watertight=False)
    simplified = []
    for comp in components:
        diag = float(np.linalg.norm(comp.extents))
        cell = max(diag / target_cells_across_diag, 1e-6)
        simplified.append(vertex_cluster_simplify(comp, cell))
    return trimesh.util.concatenate(simplified)


def fit_box(comp: trimesh.Trimesh) -> tuple[dict[str, Any], trimesh.Trimesh]:
    to_origin, extents = trimesh.bounds.oriented_bounds(comp)
    transform = np.linalg.inv(to_origin)
    fitted = trimesh.creation.box(extents=extents, transform=transform)
    return {
        "type": "box",
        "extents": [float(x) for x in extents],
        "transform": transform.tolist(),
    }, fitted


def rotation_from_z(axis: np.ndarray) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    z = np.array([0.0, 0.0, 1.0])
    dot = float(np.clip(np.dot(z, axis), -1.0, 1.0))
    if dot > 1.0 - 1e-10:
        return np.eye(3)
    if dot < -1.0 + 1e-10:
        return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=float)
    v = np.cross(z, axis)
    s = np.linalg.norm(v)
    vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + vx + vx @ vx * ((1 - dot) / (s * s))


def fit_cylinder(comp: trimesh.Trimesh) -> tuple[dict[str, Any], trimesh.Trimesh]:
    pts = np.asarray(comp.vertices)
    center = pts.mean(axis=0)
    cov = np.cov(pts - center, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(cov)
    axis = eigvecs[:, np.argmax(eigvals)]
    axis = axis / np.linalg.norm(axis)
    # Keep deterministic orientation.
    if axis[2] < 0:
        axis = -axis
    t = (pts - center) @ axis
    tmin, tmax = float(t.min()), float(t.max())
    height = tmax - tmin
    axis_center = center + axis * ((tmin + tmax) / 2.0)
    perp = pts - (center + np.outer(t, axis))
    radii = np.linalg.norm(perp, axis=1)
    # Median is robust to cap-center vertices.
    radius = float(np.median(radii[radii > 1e-8]))

    transform = np.eye(4)
    transform[:3, :3] = rotation_from_z(axis)
    transform[:3, 3] = axis_center
    fitted = trimesh.creation.cylinder(radius=radius, height=height, sections=96, transform=transform)
    return {
        "type": "cylinder",
        "radius": radius,
        "height": height,
        "axis": axis.tolist(),
        "center": axis_center.tolist(),
        "transform": transform.tolist(),
    }, fitted


def classify_and_fit(comp: trimesh.Trimesh) -> tuple[dict[str, Any], trimesh.Trimesh]:
    pts = np.asarray(comp.vertices)
    cov = np.cov(pts - pts.mean(axis=0), rowvar=False)
    eigvals = np.sort(np.linalg.eigvalsh(cov))[::-1]
    long_ratio = eigvals[0] / max(eigvals[1], 1e-12)
    cross_ratio = eigvals[1] / max(eigvals[2], 1e-12)
    if long_ratio > 5.0 and 0.55 < cross_ratio < 1.8:
        params, fitted = fit_cylinder(comp)
    else:
        params, fitted = fit_box(comp)
    params["input_vertices"] = int(len(comp.vertices))
    params["input_faces"] = int(len(comp.faces))
    params["eigenvalues"] = [float(x) for x in eigvals]
    return params, fitted


def symmetric_metrics(a: trimesh.Trimesh, b: trimesh.Trimesh, samples: int = 30000) -> dict[str, float]:
    pa, _ = trimesh.sample.sample_surface(a, samples)
    pb, _ = trimesh.sample.sample_surface(b, samples)
    da, _ = cKDTree(pb).query(pa, k=1, workers=-1)
    db, _ = cKDTree(pa).query(pb, k=1, workers=-1)
    diag = max(float(np.linalg.norm(a.extents)), 1e-12)
    chamfer = float((da.mean() + db.mean()) / 2.0)
    hausdorff = float(max(da.max(), db.max()))
    return {
        "chamfer_mean": chamfer,
        "chamfer_normalized_by_bbox_diag": chamfer / diag,
        "hausdorff": hausdorff,
        "hausdorff_normalized_by_bbox_diag": hausdorff / diag,
    }


def scad_matrix(m: np.ndarray) -> str:
    rows = []
    for row in m:
        rows.append("[" + ", ".join(f"{float(v):.9g}" for v in row) + "]")
    return "[" + ", ".join(rows) + "]"


def write_scad(primitives: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "// Auto-generated parametric CAD approximation from a triangulated mesh",
        "$fn = 96;",
        "union() {",
    ]
    for p in primitives:
        m = np.array(p["transform"], dtype=float)
        if p["type"] == "box":
            ex = p["extents"]
            lines.append(f"  multmatrix(m={scad_matrix(m)}) cube([{ex[0]:.9g}, {ex[1]:.9g}, {ex[2]:.9g}], center=true);")
        elif p["type"] == "cylinder":
            lines.append(
                f"  multmatrix(m={scad_matrix(m)}) cylinder(h={p['height']:.9g}, r={p['radius']:.9g}, center=true);"
            )
    lines.append("}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_preview(mesh: trimesh.Trimesh, path: Path, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pts, _ = trimesh.sample.sample_surface(mesh, min(18000, max(5000, len(mesh.faces))))
    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], s=0.5, alpha=0.65)
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    mins, maxs = pts.min(axis=0), pts.max(axis=0)
    center = (mins + maxs) / 2
    span = max(maxs - mins) / 2
    ax.set_xlim(center[0] - span, center[0] + span)
    ax.set_ylim(center[1] - span, center[1] + span)
    ax.set_zlim(center[2] - span, center[2] + span)
    ax.view_init(elev=25, azim=40)
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    high = make_highpoly_table()
    high.export(OUT / "01_input_highpoly_table.ply")
    high.export(OUT / "01_input_highpoly_table.obj")

    low = simplify_by_component(high, target_cells_across_diag=65)
    low.export(OUT / "02_lowpoly_vertex_cluster.ply")
    low.export(OUT / "02_lowpoly_vertex_cluster.obj")

    components = low.split(only_watertight=False)
    primitives: list[dict[str, Any]] = []
    fitted_meshes: list[trimesh.Trimesh] = []
    for idx, comp in enumerate(sorted(components, key=lambda m: float(m.volume), reverse=True)):
        params, fitted = classify_and_fit(comp)
        params["component_id"] = idx
        primitives.append(params)
        fitted_meshes.append(fitted)
        comp.export(OUT / f"part_{idx:02d}_mesh.ply")

    reconstructed = trimesh.util.concatenate(fitted_meshes)
    reconstructed.export(OUT / "03_parametric_reconstruction.ply")
    reconstructed.export(OUT / "03_parametric_reconstruction.obj")
    write_scad(primitives, OUT / "03_parametric_reconstruction.scad")

    metrics = {
        "input": {
            "vertices": int(len(high.vertices)),
            "faces": int(len(high.faces)),
            "components": int(len(high.split(only_watertight=False))),
            "watertight": bool(high.is_watertight),
            "bbox_extents": [float(x) for x in high.extents],
        },
        "lowpoly": {
            "vertices": int(len(low.vertices)),
            "faces": int(len(low.faces)),
            "components": int(len(components)),
            "watertight": bool(low.is_watertight),
            "reduction_ratio_faces": 1.0 - len(low.faces) / len(high.faces),
            **symmetric_metrics(high, low),
        },
        "parametric_reconstruction": {
            "vertices": int(len(reconstructed.vertices)),
            "faces": int(len(reconstructed.faces)),
            "primitive_count": len(primitives),
            "primitive_types": [p["type"] for p in primitives],
            **symmetric_metrics(high, reconstructed),
        },
        "scope_warning": (
            "This controlled MVP uses disconnected, axis-regular parts and supports only boxes and cylinders. "
            "It validates the data/metric/export loop, not open-world Mesh-to-CAD generalization."
        ),
    }

    (OUT / "primitives.json").write_text(json.dumps(primitives, indent=2), encoding="utf-8")
    (OUT / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    render_preview(high, OUT / "preview_input_highpoly.png", "Input high-poly mesh")
    render_preview(low, OUT / "preview_lowpoly.png", "Low-poly mesh (vertex clustering baseline)")
    render_preview(reconstructed, OUT / "preview_parametric_cad.png", "Recovered parametric primitives")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
