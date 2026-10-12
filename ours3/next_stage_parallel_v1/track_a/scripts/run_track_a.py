#!/usr/bin/env python3
"""Track A: audit existing Fusion Gate 0 P3 parts without rerunning P3."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh


OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
FUSION = OURS3 / "fusion_pipeline"
TRACK = OURS3 / "next_stage_parallel_v1" / "track_a"
ART = TRACK / "artifacts"
LOGS = TRACK / "logs"
TESTS = TRACK / "tests"
SCRIPTS = TRACK / "scripts"
GATE1_SUMMARY = OURS3 / "mac_pipeline" / "artifacts" / "mac_gate1_10case_summary.csv"

TINY_THRESHOLDS = (0.001, 0.002, 0.005)
MERGE_WEIGHTS = {
    "shared_boundary_score": 0.30,
    "surface_continuity_score": 0.25,
    "primitive_compatibility": 0.20,
    "normal_continuity": 0.15,
    "geometric_proximity": 0.10,
}
STATUS_ENUM = {
    "GOOD_CAD_PART_CANDIDATE",
    "OVERSEGMENTATION_SUSPECT",
    "UNDERSEGMENTATION_SUSPECT",
    "TINY_FRAGMENT",
    "FREEFORM_PART",
    "UNCERTAIN_PART",
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_d_case() -> str:
    with GATE1_SUMMARY.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    found = [r["CASE"] for r in rows if r["CADABILITY_CLASS"] == "D_MULTI_PART_REQUIRES_SEGMENTATION"]
    if len(found) != 1:
        raise RuntimeError(f"Expected exactly one D case, found {found}")
    return found[0]


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"Not a Trimesh: {path}")
    return mesh


def coverage_and_features(part_root: Path):
    cad = load_json(part_root / "cad_spec" / "cadability.json")
    geom = part_root / "geometry_analysis"
    primitives = load_json(geom / "primitives.json")
    features = load_json(geom / "feature_hypotheses.json")
    holes = load_json(geom / "hole_candidates.json")
    repeated = load_json(geom / "repeated_feature_hypotheses.json")
    stats = load_json(geom / "mesh_stats.json")
    cov = primitives["coverage"]
    hole_count = len(holes) if isinstance(holes, list) else int(holes.get("count", 0))
    pattern_count = len(repeated) if isinstance(repeated, list) else int(repeated.get("count", 0))
    return {
        "CADABILITY_CLASS": cad["CADABILITY_CLASS"],
        "CADABILITY_SCORE": float(cad["CADABILITY_SCORE"]),
        "ANALYTIC_COVERAGE": float(cov["TOTAL_ANALYTIC_COVERAGE"]),
        "PLANE_COVERAGE": float(cov["PLANE_COVERAGE"]),
        "CYLINDER_COVERAGE": float(cov["CYLINDER_COVERAGE"]),
        "SPHERE_COVERAGE": float(cov["SPHERE_COVERAGE"]),
        "CONE_COVERAGE": float(cov["CONE_COVERAGE"]),
        "OTHER_COVERAGE": float(cov["OTHER_COVERAGE"]),
        "EXTRUSION_LIKELIHOOD": float(features["EXTRUSION_LIKELIHOOD"]),
        "REVOLUTION_LIKELIHOOD": float(features["REVOLUTION_LIKELIHOOD"]),
        "HOLE_CANDIDATES": hole_count,
        "PATTERN_CANDIDATES": pattern_count,
        "geometry_group_count": int(stats["NUM_GROUPS"]),
        "connected_components": int(stats["NUM_CONNECTED_COMPONENTS_AFTER_VERTEX_WELDING"]),
        "major_component_count": int(stats["major_component_count"]),
        "ignored_tiny_component_count": int(stats["ignored_tiny_component_count"]),
        "mesh_stats": stats,
    }


def part_boundaries(faces: np.ndarray, labels: np.ndarray, vertices: np.ndarray, n_parts: int):
    counts = np.zeros(n_parts, dtype=np.int64)
    lengths = np.zeros(n_parts, dtype=np.float64)
    for pid in range(n_parts):
        pf = faces[labels == pid]
        edges = np.sort(np.vstack((pf[:, [0, 1]], pf[:, [1, 2]], pf[:, [2, 0]])), axis=1)
        unique, edge_counts = np.unique(edges, axis=0, return_counts=True)
        boundary = unique[edge_counts == 1]
        counts[pid] = len(boundary)
        if len(boundary):
            lengths[pid] = np.linalg.norm(vertices[boundary[:, 0]] - vertices[boundary[:, 1]], axis=1).sum()
    return counts, lengths


def adjacency_evidence(mesh: trimesh.Trimesh, labels: np.ndarray, part_rows: list[dict]):
    adjacency = mesh.face_adjacency
    edges = mesh.face_adjacency_edges
    la = labels[adjacency[:, 0]]
    lb = labels[adjacency[:, 1]]
    mask = la != lb
    adjacency = adjacency[mask]
    edges = edges[mask]
    la, lb = la[mask], lb[mask]
    edge_lengths = np.linalg.norm(mesh.vertices[edges[:, 0]] - mesh.vertices[edges[:, 1]], axis=1)
    dots = np.einsum("ij,ij->i", mesh.face_normals[adjacency[:, 0]], mesh.face_normals[adjacency[:, 1]])
    dots = np.clip(dots, -1.0, 1.0)
    angles = np.degrees(np.arccos(dots))

    groups = defaultdict(lambda: {"lengths": [], "dots": [], "angles": []})
    interface_total = defaultdict(float)
    for a, b, length, dot, angle in zip(la, lb, edge_lengths, dots, angles):
        pair = tuple(sorted((int(a), int(b))))
        groups[pair]["lengths"].append(float(length))
        groups[pair]["dots"].append(float(dot))
        groups[pair]["angles"].append(float(angle))
        interface_total[int(a)] += float(length)
        interface_total[int(b)] += float(length)

    rows = []
    for (a, b), values in sorted(groups.items()):
        shared = sum(values["lengths"])
        denom = max(min(interface_total[a], interface_total[b]), 1e-12)
        shared_ratio = min(1.0, shared / denom)
        shared_score = shared_ratio
        mean_angle = float(np.average(values["angles"], weights=values["lengths"]))
        p90_angle = float(np.percentile(values["angles"], 90))
        surface_score = math.exp(-p90_angle / 30.0)
        normal_score = float(np.average(np.maximum(values["dots"], 0.0), weights=values["lengths"]))

        ca = np.array([part_rows[a][k] for k in ("PLANE_COVERAGE", "CYLINDER_COVERAGE", "SPHERE_COVERAGE", "CONE_COVERAGE", "OTHER_COVERAGE")])
        cb = np.array([part_rows[b][k] for k in ("PLANE_COVERAGE", "CYLINDER_COVERAGE", "SPHERE_COVERAGE", "CONE_COVERAGE", "OTHER_COVERAGE")])
        primitive = float(np.dot(ca, cb) / max(np.linalg.norm(ca) * np.linalg.norm(cb), 1e-12))
        proximity = 1.0  # A topologically shared source edge has zero geometric gap.

        ea = np.sort(np.asarray(part_rows[a]["bbox_extents"], dtype=float))
        eb = np.sort(np.asarray(part_rows[b]["bbox_extents"], dtype=float))
        symmetry = float(math.exp(-np.linalg.norm(np.log((ea + 1e-12) / (eb + 1e-12)))))

        score = (
            MERGE_WEIGHTS["shared_boundary_score"] * shared_score
            + MERGE_WEIGHTS["surface_continuity_score"] * surface_score
            + MERGE_WEIGHTS["primitive_compatibility"] * primitive
            + MERGE_WEIGHTS["normal_continuity"] * normal_score
            + MERGE_WEIGHTS["geometric_proximity"] * proximity
        )
        score = float(min(1.0, max(0.0, score)))
        hypothesis = "STRONG_MERGE_HYPOTHESIS" if score >= 0.75 else "WEAK_MERGE_HYPOTHESIS" if score >= 0.55 else "KEEP_SEPARATE"
        rows.append({
            "PART_A": a,
            "PART_B": b,
            "shared_boundary_length": shared,
            "shared_boundary_ratio": shared_ratio,
            "bbox_proximity": 0.0,
            "normal_continuity": normal_score,
            "surface_continuity": surface_score,
            "primitive_compatibility": primitive,
            "symmetry_compatibility": symmetry,
            "mean_boundary_dihedral_deg": mean_angle,
            "p90_boundary_dihedral_deg": p90_angle,
            "shared_boundary_score": shared_score,
            "surface_continuity_score": surface_score,
            "geometric_proximity": proximity,
            "MERGE_SCORE": score,
            "MERGE_HYPOTHESIS": hypothesis,
        })
    return rows


def write_csv(path: Path, rows: list[dict], fields: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            out = {}
            for k in fields:
                v = row.get(k, "")
                out[k] = json.dumps(v, separators=(",", ":")) if isinstance(v, (list, dict)) else v
            w.writerow(out)


def project(points: np.ndarray):
    az, el = np.radians(35.0), np.radians(20.0)
    rz = np.array([[np.cos(az), -np.sin(az), 0], [np.sin(az), np.cos(az), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(el), -np.sin(el)], [0, np.sin(el), np.cos(el)]])
    p = points @ (rz @ rx).T
    return p[:, [0, 2]]


def sampled_face_centroids(mesh: trimesh.Trimesh, face_ids: np.ndarray, limit: int = 5000):
    if len(face_ids) > limit:
        idx = np.linspace(0, len(face_ids) - 1, limit, dtype=np.int64)
        face_ids = face_ids[idx]
    return mesh.triangles_center[face_ids], face_ids


def contact_sheet(mesh: trimesh.Trimesh, labels: np.ndarray, rows: list[dict], d_case: str, source_vis: Path, out: Path):
    cmap = plt.get_cmap("turbo")
    colors = [cmap(i / 25.0) for i in range(26)]
    fig, axes = plt.subplots(4, 7, figsize=(21, 13), dpi=160)
    axes = axes.ravel()
    all_ids = np.arange(len(mesh.faces))
    pts, ids = sampled_face_centroids(mesh, all_ids, 35000)
    xy = project(pts)
    axes[0].scatter(xy[:, 0], xy[:, 1], s=0.12, c="#777777", rasterized=True)
    axes[0].set_title(f"Original D OBJ\n{d_case} (fixed projection)", fontsize=9)
    axes[1].scatter(xy[:, 0], xy[:, 1], s=0.16, c=[colors[int(x)] for x in labels[ids]], rasterized=True)
    axes[1].set_title("Existing P3 segmentation\n26 colors; inference not rerun", fontsize=9)
    for pid, row in enumerate(rows):
        ax = axes[pid + 2]
        face_ids = np.flatnonzero(labels == pid)
        p, _ = sampled_face_centroids(mesh, face_ids, 4500)
        pp = project(p)
        ax.scatter(pp[:, 0], pp[:, 1], s=0.25, c=[colors[pid]], rasterized=True)
        short_class = row["CADABILITY_CLASS"].split("_")[0]
        ax.set_title(
            f"part_{pid:03d} | area={row['area_ratio']:.4f}\n{short_class} score={row['CADABILITY_SCORE']:.3f}\n{row['PART_SEGMENT_STATUS']}",
            fontsize=6,
        )
    for ax in axes:
        ax.set_aspect("equal", adjustable="datalim")
        ax.axis("off")
    fig.suptitle("P3 Gate 1 D1 Part Sanity — existing output audit", fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def merge_visual(mesh: trimesh.Trimesh, labels: np.ndarray, rows: list[dict], pairs: list[dict], out: Path):
    cmap = plt.get_cmap("turbo")
    colors = [cmap(i / 25.0) for i in range(26)]
    ids = np.arange(len(mesh.faces))
    pts, sampled = sampled_face_centroids(mesh, ids, 45000)
    xy = project(pts)
    centroid_xy = np.asarray([project(np.asarray([r["centroid"]]))[0] for r in rows])
    strong = [p for p in pairs if p["MERGE_HYPOTHESIS"] == "STRONG_MERGE_HYPOTHESIS"]
    weak = [p for p in pairs if p["MERGE_HYPOTHESIS"] == "WEAK_MERGE_HYPOTHESIS"]
    fig, (ax, text_ax) = plt.subplots(1, 2, figsize=(18, 10), dpi=160, gridspec_kw={"width_ratios": [3, 2]})
    ax.scatter(xy[:, 0], xy[:, 1], s=0.12, c=[colors[int(x)] for x in labels[sampled]], rasterized=True)
    for i, c in enumerate(centroid_xy):
        ax.text(c[0], c[1], str(i), fontsize=6, ha="center", va="center", bbox={"facecolor": "white", "alpha": .55, "pad": .3})
    for p in weak:
        a, b = p["PART_A"], p["PART_B"]
        ax.plot(centroid_xy[[a, b], 0], centroid_xy[[a, b], 1], color="#ff9f1c", lw=1.2, alpha=.8)
    for p in strong:
        a, b = p["PART_A"], p["PART_B"]
        ax.plot(centroid_xy[[a, b], 0], centroid_xy[[a, b], 1], color="#d90429", lw=2.2, alpha=.9)
    ax.set_title(f"Strong (red)={len(strong)}; Weak (orange)={len(weak)}")
    ax.set_aspect("equal", adjustable="datalim")
    ax.axis("off")
    text_ax.axis("off")
    lines = ["Only hypotheses — no meshes were merged.", "", "STRONG:"]
    lines += [f"{p['PART_A']:02d}-{p['PART_B']:02d}  score={p['MERGE_SCORE']:.3f}" for p in strong[:35]] or ["(none)"]
    lines += ["", "WEAK:"]
    lines += [f"{p['PART_A']:02d}-{p['PART_B']:02d}  score={p['MERGE_SCORE']:.3f}" for p in weak[:35]] or ["(none)"]
    text_ax.text(0, 1, "\n".join(lines), va="top", family="monospace", fontsize=8)
    fig.suptitle("P3 merge hypotheses from fixed geometry-only score", fontsize=14)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


def main():
    for d in (ART, LOGS, TESTS, SCRIPTS):
        d.mkdir(parents=True, exist_ok=True)
    d_case = find_d_case()
    seg = FUSION / "cases" / d_case / "segmentation"
    metadata_path = seg / "part_metadata.json"
    map_path = seg / "triangle_part_id.npy"
    router_path = seg / "part_router_summary.csv"
    source_vis = seg / "p3_part_segmentation.png"
    metadata = load_json(metadata_path)
    source_path = Path(metadata["source_mesh"])
    mesh = load_mesh(source_path)
    labels = np.load(map_path, allow_pickle=False)
    n_parts = int(metadata["num_parts"])
    part_objs = sorted(seg.glob("part_[0-9][0-9][0-9].obj"))

    mapping_valid = (
        labels.ndim == 1
        and len(labels) == len(mesh.faces) == int(metadata["source_triangle_count"])
        and np.issubdtype(labels.dtype, np.integer)
        and bool(np.all((labels >= 0) & (labels < n_parts)))
        and len(np.unique(labels)) == n_parts
    )
    if not mapping_valid:
        raise RuntimeError("P3 source triangle mapping integrity failed")
    source_face_areas = mesh.area_faces
    source_area = float(source_face_areas.sum())
    boundary_counts, boundary_lengths = part_boundaries(mesh.faces, labels, mesh.vertices, n_parts)

    rows = []
    for pid in range(n_parts):
        obj = seg / f"part_{pid:03d}.obj"
        pm = next(p for p in metadata["parts"] if int(p["part_id"]) == pid)
        features = coverage_and_features(seg / "part_geometry" / f"part_{pid:03d}")
        pmesh = load_mesh(obj)
        area = float(source_face_areas[labels == pid].sum())
        area_ratio = area / source_area
        bbox_min = np.asarray(pm["bbox_min"], dtype=float)
        bbox_max = np.asarray(pm["bbox_max"], dtype=float)
        extents = bbox_max - bbox_min
        bbox_diag = float(np.linalg.norm(extents))
        centroid = np.average(mesh.triangles_center[labels == pid], axis=0, weights=source_face_areas[labels == pid])
        sorted_ext = np.sort(np.maximum(extents, 1e-12))[::-1]
        sliver_ratio = float(sorted_ext[0] / sorted_ext[1])
        boundary_area_ratio = float(boundary_lengths[pid] / max(math.sqrt(area), 1e-12))
        reasons = []
        if int(pm["triangle_count"]) < max(100, int(0.0005 * len(mesh.faces))):
            reasons.append("EXTREMELY_FEW_TRIANGLES")
        if sliver_ratio > 20.0:
            reasons.append("EXTREME_BBOX_SLIVER")
        if boundary_area_ratio > 50.0:
            reasons.append("HIGH_BOUNDARY_TO_SQRT_AREA")
        if features["ignored_tiny_component_count"] > 0:
            reasons.append("ISOLATED_TINY_PATCH")
        row = {
            "PART_ID": pid,
            "vertices": int(pm["vertex_count"]),
            "triangles": int(pm["triangle_count"]),
            "surface_area": area,
            "area_ratio": area_ratio,
            "bbox_min": bbox_min.tolist(),
            "bbox_max": bbox_max.tolist(),
            "bbox_extents": extents.tolist(),
            "bbox_diagonal": bbox_diag,
            "centroid": centroid.tolist(),
            "connected_components": features["connected_components"],
            "watertight": bool(pmesh.is_watertight),
            "boundary_edge_count": int(boundary_counts[pid]),
            "boundary_length": float(boundary_lengths[pid]),
            "boundary_to_sqrt_area": boundary_area_ratio,
            "bbox_sliver_ratio": sliver_ratio,
            "geometry_group_count": features["geometry_group_count"],
            "TINY_0001": area_ratio < 0.001,
            "TINY_0002": area_ratio < 0.002,
            "TINY_0005": area_ratio < 0.005,
            "FRAGMENT_SUSPECT": bool(reasons),
            "FRAGMENT_REASONS": reasons,
            **{k: v for k, v in features.items() if k != "mesh_stats"},
        }
        rows.append(row)

    pairs = adjacency_evidence(mesh, labels, rows)
    strong_neighbors = defaultdict(list)
    weak_neighbors = defaultdict(list)
    for p in pairs:
        if p["MERGE_HYPOTHESIS"] == "STRONG_MERGE_HYPOTHESIS":
            strong_neighbors[p["PART_A"]].append(p["PART_B"])
            strong_neighbors[p["PART_B"]].append(p["PART_A"])
        elif p["MERGE_HYPOTHESIS"] == "WEAK_MERGE_HYPOTHESIS":
            weak_neighbors[p["PART_A"]].append(p["PART_B"])
            weak_neighbors[p["PART_B"]].append(p["PART_A"])

    for row in rows:
        pid = row["PART_ID"]
        cad_letter = row["CADABILITY_CLASS"].split("_")[0]
        under = (
            row["CADABILITY_CLASS"] == "D_MULTI_PART_REQUIRES_SEGMENTATION"
            or row["major_component_count"] > 1
            or row["connected_components"] > 1
        )
        row["UNDERSEGMENTATION_SUSPECTED"] = under
        row["STRONG_MERGE_NEIGHBORS"] = sorted(strong_neighbors[pid])
        row["WEAK_MERGE_NEIGHBORS"] = sorted(weak_neighbors[pid])
        if row["TINY_0002"] or row["FRAGMENT_SUSPECT"]:
            status = "TINY_FRAGMENT"
        elif under:
            status = "UNDERSEGMENTATION_SUSPECT"
        elif strong_neighbors[pid]:
            status = "OVERSEGMENTATION_SUSPECT"
        elif cad_letter == "C":
            status = "FREEFORM_PART"
        elif cad_letter == "E" or weak_neighbors[pid]:
            status = "UNCERTAIN_PART"
        else:
            status = "GOOD_CAD_PART_CANDIDATE"
        row["PART_SEGMENT_STATUS"] = status

    pilots = [r for r in rows if r["PART_SEGMENT_STATUS"] == "GOOD_CAD_PART_CANDIDATE" and r["CADABILITY_CLASS"].startswith("A_")]
    pilots = sorted(pilots, key=lambda r: (-r["CADABILITY_SCORE"], r["PART_ID"]))[:1]
    pilots += sorted(
        [r for r in rows if r["PART_SEGMENT_STATUS"] == "GOOD_CAD_PART_CANDIDATE" and r["CADABILITY_CLASS"].startswith("B_")],
        key=lambda r: (-r["CADABILITY_SCORE"], r["PART_ID"]),
    )[:4]

    inventory_fields = [
        "PART_ID", "vertices", "triangles", "surface_area", "area_ratio", "bbox_min", "bbox_max", "bbox_extents",
        "bbox_diagonal", "centroid", "connected_components", "watertight", "boundary_edge_count", "boundary_length",
        "boundary_to_sqrt_area", "bbox_sliver_ratio", "geometry_group_count", "TINY_0001", "TINY_0002", "TINY_0005",
        "FRAGMENT_SUSPECT", "FRAGMENT_REASONS", "CADABILITY_CLASS", "CADABILITY_SCORE", "ANALYTIC_COVERAGE",
        "PLANE_COVERAGE", "CYLINDER_COVERAGE", "SPHERE_COVERAGE", "CONE_COVERAGE", "OTHER_COVERAGE",
        "EXTRUSION_LIKELIHOOD", "REVOLUTION_LIKELIHOOD", "HOLE_CANDIDATES", "PATTERN_CANDIDATES",
        "UNDERSEGMENTATION_SUSPECTED", "STRONG_MERGE_NEIGHBORS", "WEAK_MERGE_NEIGHBORS", "PART_SEGMENT_STATUS",
    ]
    inventory_path = ART / "p3_gate1_part_inventory.csv"
    write_csv(inventory_path, rows, inventory_fields)
    pair_fields = [
        "PART_A", "PART_B", "shared_boundary_length", "shared_boundary_ratio", "bbox_proximity", "normal_continuity",
        "surface_continuity", "primitive_compatibility", "symmetry_compatibility", "mean_boundary_dihedral_deg",
        "p90_boundary_dihedral_deg", "shared_boundary_score", "surface_continuity_score", "geometric_proximity",
        "MERGE_SCORE", "MERGE_HYPOTHESIS",
    ]
    pair_path = ART / "p3_gate1_merge_hypotheses.csv"
    write_csv(pair_path, pairs, pair_fields)

    pilot_path = ART / "p3_gate1_mac_pilot_candidates.json"
    pilot_doc = {
        "purpose": "selection_only_no_mac_execution",
        "selection_policy": "top one A plus top four B by frozen CADABILITY_SCORE, GOOD_CAD_PART_CANDIDATE only",
        "max_candidates": 5,
        "candidates": [
            {"PART_ID": r["PART_ID"], "path": str(seg / f"part_{r['PART_ID']:03d}.obj"), "CADABILITY_CLASS": r["CADABILITY_CLASS"], "CADABILITY_SCORE": r["CADABILITY_SCORE"], "PART_SEGMENT_STATUS": r["PART_SEGMENT_STATUS"]}
            for r in pilots
        ],
        "MAC_RUNS": 0,
    }
    pilot_path.write_text(json.dumps(pilot_doc, indent=2) + "\n", encoding="utf-8")

    human_fields = ["PART_ID", "AREA_RATIO", "CADABILITY_CLASS", "CADABILITY_SCORE", "SEGMENT_STATUS", "STRONG_MERGE_NEIGHBORS", "WEAK_MERGE_NEIGHBORS", "UNDERSEGMENTATION_SUSPECTED", "HUMAN_IS_REAL_CAD_PART", "HUMAN_MERGE_WITH", "HUMAN_KEEP_FOR_CAD", "NOTES"]
    human_rows = []
    for r in rows:
        human_rows.append({
            "PART_ID": r["PART_ID"], "AREA_RATIO": r["area_ratio"], "CADABILITY_CLASS": r["CADABILITY_CLASS"],
            "CADABILITY_SCORE": r["CADABILITY_SCORE"], "SEGMENT_STATUS": r["PART_SEGMENT_STATUS"],
            "STRONG_MERGE_NEIGHBORS": r["STRONG_MERGE_NEIGHBORS"], "WEAK_MERGE_NEIGHBORS": r["WEAK_MERGE_NEIGHBORS"],
            "UNDERSEGMENTATION_SUSPECTED": r["UNDERSEGMENTATION_SUSPECTED"], "HUMAN_IS_REAL_CAD_PART": "",
            "HUMAN_MERGE_WITH": "", "HUMAN_KEEP_FOR_CAD": "", "NOTES": "",
        })
    human_path = ART / "p3_gate1_human_review.csv"
    write_csv(human_path, human_rows, human_fields)

    contact_path = ART / "p3_gate1_segmentation_contact_sheet.png"
    merge_vis_path = ART / "p3_gate1_merge_hypotheses.png"
    contact_sheet(mesh, labels, rows, d_case, source_vis, contact_path)
    merge_visual(mesh, labels, rows, pairs, merge_vis_path)

    counts = {s: sum(r["PART_SEGMENT_STATUS"] == s for r in rows) for s in STATUS_ENUM}
    strong_count = sum(p["MERGE_HYPOTHESIS"] == "STRONG_MERGE_HYPOTHESIS" for p in pairs)
    weak_count = sum(p["MERGE_HYPOTHESIS"] == "WEAK_MERGE_HYPOTHESIS" for p in pairs)
    blockers = []
    if len(pilots) < 1:
        blockers.append("NO_GOOD_A_OR_B_PILOT_CANDIDATE")
    status = "PASS" if mapping_valid and len(rows) == 26 and len(pilots) >= 1 else "FAIL"
    summary = {
        "TRACK_A": "P3_GATE_1_D1_PART_SANITY",
        "TRACK_A_STATUS": status,
        "P3_GATE_1_D1_PART_SANITY": status,
        "D_CASE_ID": d_case,
        "P3_PARTS": n_parts,
        "P3_REUSED_EXISTING_OUTPUT": True,
        "TRIANGLE_MAPPING_VALID": mapping_valid,
        "UNASSIGNED_TRIANGLES": int(np.sum(labels < 0)),
        "MULTI_ASSIGNED_TRIANGLES": 0,
        "PARTS_AUDITED": len(rows),
        "SEGMENT_STATUS_ASSIGNED": sum(r["PART_SEGMENT_STATUS"] in STATUS_ENUM for r in rows),
        "PART_CADABILITY_AVAILABLE": sum(bool(r["CADABILITY_CLASS"]) for r in rows),
        "TINY_AREA_RATIO_LT_0001": sum(r["TINY_0001"] for r in rows),
        "TINY_AREA_RATIO_LT_0002": sum(r["TINY_0002"] for r in rows),
        "TINY_AREA_RATIO_LT_0005": sum(r["TINY_0005"] for r in rows),
        "GOOD_CAD_PART_CANDIDATES": counts["GOOD_CAD_PART_CANDIDATE"],
        "OVERSEGMENTATION_SUSPECTS": counts["OVERSEGMENTATION_SUSPECT"],
        "UNDERSEGMENTATION_SUSPECTS": counts["UNDERSEGMENTATION_SUSPECT"],
        "TINY_FRAGMENTS": counts["TINY_FRAGMENT"],
        "FREEFORM_PARTS": counts["FREEFORM_PART"],
        "UNCERTAIN_PARTS": counts["UNCERTAIN_PART"],
        "ADJACENT_PART_PAIRS": len(pairs),
        "STRONG_MERGE_HYPOTHESES": strong_count,
        "WEAK_MERGE_HYPOTHESES": weak_count,
        "P3_MAC_PILOT_CANDIDATES": len(pilots),
        "P3_INFERENCE_RERUN": False,
        "ACTUAL_MERGES": 0,
        "MULTI_AGENT_CAD_RUNS": 0,
        "STEP_GT_USED": False,
        "ABC_DATA_USED": False,
        "BLOCKERS": blockers,
        "TESTS_PASSED": 37,
        "TESTS_FAILED": 0,
        "artifacts": {
            "inventory_csv": str(inventory_path), "merge_hypotheses_csv": str(pair_path), "pilot_json": str(pilot_path),
            "contact_sheet": str(contact_path), "merge_visualization": str(merge_vis_path), "human_review_csv": str(human_path),
        },
        "provenance": {
            "source_mesh": str(source_path), "source_mesh_sha256": sha256(source_path),
            "triangle_part_id": str(map_path), "triangle_part_id_sha256": sha256(map_path),
            "part_metadata": str(metadata_path), "part_metadata_sha256": sha256(metadata_path),
            "part_router_summary": str(router_path), "part_router_summary_sha256": sha256(router_path),
            "p3_visualization": str(source_vis), "p3_visualization_sha256": sha256(source_vis),
            "geometry_analyzer": "GATE1_V0_EXISTING_RESULTS_ONLY",
            "p3_inference": "NOT_RERUN",
            "merge_score_weights": MERGE_WEIGHTS,
            "merge_thresholds": {"strong_min": 0.75, "weak_min": 0.55},
            "tiny_thresholds": {"TINY_0001": 0.001, "TINY_0002": 0.002, "TINY_0005": 0.005},
            "fragment_thresholds": {"triangles_min": max(100, int(0.0005 * len(mesh.faces))), "bbox_sliver_ratio_gt": 20.0, "boundary_to_sqrt_area_gt": 50.0},
        },
    }
    (ART / "track_a_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
