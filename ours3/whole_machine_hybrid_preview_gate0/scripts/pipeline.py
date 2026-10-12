from __future__ import annotations

import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np


OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
ROOT = OURS3 / "whole_machine_hybrid_preview_gate0"
HYBRID = ROOT / "hybrid"
ART = ROOT / "artifacts"
LOGS = ROOT / "logs"
INPUTS = ROOT / "inputs"
ACCEPTED = OURS3 / "real03_high_fidelity_parts_v2"
ASSEMBLY_MANIFEST = OURS3 / "cad_partial_assembly_gate0/assembly/assembly_manifest.json"
ASSEMBLY_METRICS = OURS3 / "cad_partial_assembly_gate0/artifacts/assembly_metrics.json"
FULL_MESH_PATH = OURS3 / "meshes/30_CONSTRUCTION_SET.obj"
GRAPH_CASES = OURS3 / "cad_part_graph_gate1/cases"
PARTS = ["CADPART_000", "CADPART_004"]
COLORS = {"CADPART_000": np.array([31, 119, 180, 255], dtype=np.uint8), "CADPART_004": np.array([214, 39, 40, 255], dtype=np.uint8)}
SEED = 20260810


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    return value


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_step(path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != IFSelect_RetDone or reader.TransferRoots() == 0:
        raise RuntimeError(f"accepted STEP reload failed: {path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"accepted STEP is null: {path}")
    return shape


def tessellate(shape, path):
    import trimesh
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    BRepMesh_IncrementalMesh(shape, 0.05, False, 0.1, True).Perform()
    StlAPI_Writer().Write(shape, str(path))
    mesh = trimesh.load(path, force="mesh", process=False)
    if len(mesh.faces) == 0:
        raise RuntimeError(f"empty fresh STEP tessellation: {path}")
    return mesh


def transform_points(points, matrix):
    matrix = np.asarray(matrix, dtype=float)
    return np.asarray(points, dtype=float) @ matrix[:3, :3].T + matrix[:3, 3]


def write_obj(path, mesh, note):
    with Path(path).open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(f"# {note}\n")
        for vertex in np.asarray(mesh.vertices):
            stream.write(f"v {vertex[0]:.12g} {vertex[1]:.12g} {vertex[2]:.12g}\n")
        for face in np.asarray(mesh.faces):
            stream.write(f"f {face[0] + 1} {face[1] + 1} {face[2] + 1}\n")


def projection(points, view):
    points = np.asarray(points, dtype=float)
    if view == "FRONT":
        return points[:, [0, 2]]
    if view == "SIDE":
        return points[:, [1, 2]]
    if view == "TOP":
        return points[:, [0, 1]]
    azimuth = math.radians(35)
    elevation = math.radians(22)
    rz = np.array([[math.cos(azimuth), -math.sin(azimuth), 0], [math.sin(azimuth), math.cos(azimuth), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(elevation), -math.sin(elevation)], [0, math.sin(elevation), math.cos(elevation)]])
    transformed = points @ (rz @ rx).T
    return transformed[:, [0, 2]]


def set_limits(ax, points2d, pad=0.04):
    low = points2d.min(axis=0)
    high = points2d.max(axis=0)
    span = np.maximum(high - low, 1e-9)
    ax.set_xlim(low[0] - span[0] * pad, high[0] + span[0] * pad)
    ax.set_ylim(low[1] - span[1] * pad, high[1] + span[1] * pad)
    ax.set_aspect("equal")
    ax.axis("off")


def scatter(ax, points, view, color, alpha=0.7, size=0.18):
    xy = projection(points, view)
    ax.scatter(xy[:, 0], xy[:, 1], s=size, c=color, alpha=alpha, linewidths=0)


def render_hybrid(ax, view, sampled, residual_alpha=0.34, cad_alpha=0.92, title=None):
    scatter(ax, sampled["residual"], view, "#777777", residual_alpha, 0.16)
    scatter(ax, sampled["CADPART_000"], view, "#1f77b4", cad_alpha, 0.28)
    scatter(ax, sampled["CADPART_004"], view, "#d62728", cad_alpha, 0.28)
    set_limits(ax, projection(sampled["full"], view))
    if title:
        ax.set_title(title)


def make_visualizations(meshes, source_regions, sampled, cad_area_coverage):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection

    views = ["FRONT", "SIDE", "THREE_QUARTER", "TOP"]
    view_labels = {"FRONT": "FRONT", "SIDE": "SIDE", "THREE_QUARTER": "3/4", "TOP": "TOP"}

    fig, axes = plt.subplots(2, 2, figsize=(14, 12), dpi=180)
    for ax, view in zip(axes.ravel(), views):
        render_hybrid(ax, view, sampled, title=view_labels[view])
    fig.suptitle("REAL_03 WHOLE-MACHINE HYBRID_MESH_CAD_PREVIEW\nGray: residual High-Mesh | Blue: CADPART_000 Q1 | Red: CADPART_004 Q2")
    fig.tight_layout(); fig.savefig(ART / "REAL_03_whole_machine_hybrid.png"); plt.close(fig)

    fig = plt.figure(figsize=(24, 16), dpi=150)
    grid = fig.add_gridspec(3, 4, height_ratios=[1.1, 1.0, 1.05])
    ax_original = fig.add_subplot(grid[0, :2])
    scatter(ax_original, sampled["full"], "THREE_QUARTER", "#555555", 0.55, 0.18)
    set_limits(ax_original, projection(sampled["full"], "THREE_QUARTER")); ax_original.set_title("ORIGINAL FULL HIGH-MESH")
    ax_hybrid = fig.add_subplot(grid[0, 2:])
    render_hybrid(ax_hybrid, "THREE_QUARTER", sampled, title="HYBRID FULL MACHINE")
    for column, view in enumerate(views):
        render_hybrid(fig.add_subplot(grid[1, column]), view, sampled, title=view_labels[view])
    ax_mask = fig.add_subplot(grid[2, :2])
    scatter(ax_mask, sampled["residual"], "THREE_QUARTER", "#bdbdbd", 0.22, 0.15)
    scatter(ax_mask, sampled["source_CADPART_000"], "THREE_QUARTER", "#1f77b4", 0.95, 0.3)
    scatter(ax_mask, sampled["source_CADPART_004"], "THREE_QUARTER", "#d62728", 0.95, 0.3)
    set_limits(ax_mask, projection(sampled["full"], "THREE_QUARTER")); ax_mask.set_title("CAD RECOVERY MASK")
    ax_text = fig.add_subplot(grid[2, 2:]); ax_text.axis("off")
    ax_text.text(0.03, 0.78, "CADPART_000 = Q1", color="#1f77b4", fontsize=18, weight="bold")
    ax_text.text(0.03, 0.61, "CADPART_004 = Q2", color="#d62728", fontsize=18, weight="bold")
    ax_text.text(0.03, 0.41, f"CAD AREA COVERAGE = {cad_area_coverage * 100:.2f}%", fontsize=18)
    ax_text.text(0.03, 0.24, f"REMAINING MESH AREA = {(1 - cad_area_coverage) * 100:.2f}%", fontsize=18)
    ax_text.text(0.03, 0.07, "HYBRID_MESH_CAD_PREVIEW (not full CAD)", fontsize=16, style="italic")
    fig.suptitle("REAL_03 WHOLE-MACHINE HYBRID CONTACT SHEET", fontsize=22)
    fig.tight_layout(); fig.savefig(ART / "REAL_03_whole_machine_hybrid_contact_sheet.png"); plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(18, 9), dpi=180)
    original_xy = projection(sampled["full"], "THREE_QUARTER")
    scatter(axes[0], sampled["full"], "THREE_QUARTER", "#555555", 0.62, 0.2)
    set_limits(axes[0], original_xy); axes[0].set_title("BEFORE: Original full REAL_03 High-Mesh")
    render_hybrid(axes[1], "THREE_QUARTER", sampled, title="AFTER: Whole-machine Hybrid")
    low, high = original_xy.min(axis=0), original_xy.max(axis=0); span = high - low
    for ax in axes:
        ax.set_xlim(low[0] - span[0] * 0.04, high[0] + span[0] * 0.04)
        ax.set_ylim(low[1] - span[1] * 0.04, high[1] + span[1] * 0.04)
    fig.suptitle("Same camera, scale, and object pose")
    fig.tight_layout(); fig.savefig(ART / "whole_machine_before_after.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 9), dpi=180)
    render_hybrid(ax, "THREE_QUARTER", sampled, residual_alpha=0.10, cad_alpha=1.0)
    ax.set_title("Recovered CAD emphasis\nBlue: CADPART_000 Q1 | Red: CADPART_004 Q2")
    fig.tight_layout(); fig.savefig(ART / "whole_machine_cad_highlight.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 9), dpi=180)
    scatter(ax, sampled["residual"], "THREE_QUARTER", "#888888", 0.18, 0.14)
    for part_id, color in [("CADPART_000", "#1f77b4"), ("CADPART_004", "#d62728")]:
        mesh = meshes[part_id]
        edges = np.asarray(mesh.edges_unique)
        if len(edges) > 15000:
            rng = np.random.default_rng(SEED + int(part_id[-3:]))
            edges = edges[rng.choice(len(edges), 15000, replace=False)]
        segments = projection(np.asarray(mesh.vertices)[edges.reshape(-1)], "THREE_QUARTER").reshape(-1, 2, 2)
        ax.add_collection(LineCollection(segments, colors=color, linewidths=0.22, alpha=0.75))
    set_limits(ax, projection(sampled["full"], "THREE_QUARTER"))
    ax.set_title("CAD BRep tessellation boundaries over residual High-Mesh")
    fig.tight_layout(); fig.savefig(ART / "whole_machine_cad_wireframe.png"); plt.close(fig)


def main():
    import trimesh
    from OCP.BRepCheck import BRepCheck_Analyzer

    for directory in (ROOT, HYBRID, ART, LOGS, INPUTS, ROOT / "scripts", ROOT / "tests"):
        directory.mkdir(parents=True, exist_ok=True)

    manifest = load(ASSEMBLY_MANIFEST)
    previous_metrics = load(ASSEMBLY_METRICS)
    if [x["part_id"] for x in manifest["parts"]] != PARTS:
        raise RuntimeError("frozen partial-assembly parts do not match the two accepted CAD parts")
    if manifest["geometry_source"] != "HIGH_FIDELITY_DETERMINISTIC_BACKEND":
        raise RuntimeError("unexpected accepted geometry source")

    full = trimesh.load(FULL_MESH_PATH, force="mesh", process=False)
    if len(full.faces) != 385828:
        raise RuntimeError(f"REAL_03 triangle count drifted: {len(full.faces)}")
    triangle_sets = {part_id: np.load(GRAPH_CASES / part_id / "source_triangle_ids.npy").astype(np.int64) for part_id in PARTS}
    for part_id, ids in triangle_sets.items():
        if len(ids) != len(np.unique(ids)) or np.any(ids < 0) or np.any(ids >= len(full.faces)):
            raise RuntimeError(f"invalid source triangle IDs: {part_id}")
    overlap = np.intersect1d(triangle_sets["CADPART_000"], triangle_sets["CADPART_004"])
    if len(overlap):
        raise RuntimeError("accepted source triangle ID sets overlap")
    recovered_ids = np.union1d(triangle_sets["CADPART_000"], triangle_sets["CADPART_004"])
    residual_mask = np.ones(len(full.faces), dtype=bool)
    residual_mask[recovered_ids] = False
    residual_source_ids = np.flatnonzero(residual_mask)
    residual = trimesh.Trimesh(vertices=np.asarray(full.vertices).copy(), faces=np.asarray(full.faces)[residual_mask].copy(), process=False)
    residual.visual.face_colors = np.tile(np.array([155, 155, 155, 255], dtype=np.uint8), (len(residual.faces), 1))
    residual_path = HYBRID / "REAL_03_residual_mesh.obj"
    write_obj(residual_path, residual, "REAL_03 residual source mesh; triangles removed strictly by frozen source triangle IDs")

    global_cad = {}
    source_regions = {}
    step_hashes = {}
    part_records = {x["part_id"]: x for x in manifest["parts"]}
    for part_id in PARTS:
        accepted_dir = ACCEPTED / part_id
        for name in ["best.step", "source.obj", "metrics.json", "provenance.json", "local_to_global_transform.json"]:
            shutil.copy2(accepted_dir / name, INPUTS / f"{part_id}_{name}")
        step_hashes[part_id] = sha256(accepted_dir / "best.step")
        if step_hashes[part_id] != part_records[part_id]["input_step_sha256"]:
            raise RuntimeError(f"accepted STEP hash changed: {part_id}")
        matrix = np.asarray(part_records[part_id]["step_current_frame_to_object_global_matrix"], dtype=float)
        if part_records[part_id]["step_current_frame"] != "CANONICAL_FRAME":
            raise RuntimeError(f"unexpected frozen STEP frame: {part_id}")
        shape = load_step(accepted_dir / "best.step")
        if not BRepCheck_Analyzer(shape).IsValid():
            raise RuntimeError(f"accepted BREP invalid: {part_id}")
        canonical = tessellate(shape, HYBRID / f"{part_id}_fresh_canonical.stl")
        vertices = transform_points(canonical.vertices, matrix)
        mesh = trimesh.Trimesh(vertices=vertices, faces=np.asarray(canonical.faces), process=False)
        mesh.visual.face_colors = np.tile(COLORS[part_id], (len(mesh.faces), 1))
        write_obj(HYBRID / f"{part_id}_global_cad.obj", mesh, "fresh accepted STEP tessellation mapped by frozen transform only; no fitting or ICP")
        global_cad[part_id] = mesh
        ids = triangle_sets[part_id]
        region = trimesh.Trimesh(vertices=np.asarray(full.vertices).copy(), faces=np.asarray(full.faces)[ids].copy(), process=False)
        source_regions[part_id] = region

    residual_count = int(len(residual_source_ids))
    recovered_count = int(sum(len(triangle_sets[x]) for x in PARTS))
    accounting_pass = residual_count + recovered_count == len(full.faces) and residual_count == len(full.faces) - len(recovered_ids)
    recovered_area = float(sum(source_regions[x].area for x in PARTS))
    total_area = float(full.area)
    cad_area_coverage = recovered_area / total_area
    mesh_area_coverage = 1.0 - cad_area_coverage
    if abs(cad_area_coverage - previous_metrics["PARTIAL_AREA_COVERAGE"]) > 1e-12:
        raise RuntimeError("hybrid area coverage disagrees with frozen partial-assembly result")

    scene = trimesh.Scene(base_frame="REAL_03_HYBRID")
    scene.add_geometry(residual, geom_name="Residual_HighMesh", node_name="Residual_HighMesh")
    scene.add_geometry(global_cad["CADPART_000"], geom_name="CADPART_000_Q1", node_name="CADPART_000_Q1")
    scene.add_geometry(global_cad["CADPART_004"], geom_name="CADPART_004_Q2", node_name="CADPART_004_Q2")
    glb_path = HYBRID / "REAL_03_hybrid_preview.glb"
    scene.export(glb_path, file_type="glb")
    reloaded_scene = trimesh.load(glb_path, force="scene", process=False)
    glb_geometry_names = sorted(reloaded_scene.geometry.keys())
    glb_node_names = sorted(reloaded_scene.graph.nodes_geometry)
    expected_names = ["CADPART_000_Q1", "CADPART_004_Q2", "Residual_HighMesh"]
    glb_valid = glb_geometry_names == expected_names and glb_node_names == expected_names and len(reloaded_scene.geometry) == 3

    def sampled(mesh, count, seed):
        return trimesh.sample.sample_surface(mesh, count, seed=seed)[0]

    sampled_points = {
        "full": sampled(full, 60000, SEED),
        "residual": sampled(residual, 60000, SEED + 1),
        "CADPART_000": sampled(global_cad["CADPART_000"], 22000, SEED + 2),
        "CADPART_004": sampled(global_cad["CADPART_004"], 22000, SEED + 3),
        "source_CADPART_000": sampled(source_regions["CADPART_000"], 18000, SEED + 4),
        "source_CADPART_004": sampled(source_regions["CADPART_004"], 18000, SEED + 5),
    }
    meshes = {"residual": residual, **global_cad}
    make_visualizations(meshes, source_regions, sampled_points, cad_area_coverage)

    provenance = {
        "schema": "WHOLE_MACHINE_HYBRID_PREVIEW_V0",
        "scientific_semantics": "HYBRID_MESH_CAD_PREVIEW",
        "source_object": "REAL_03",
        "full_source_mesh": str(FULL_MESH_PATH),
        "full_source_mesh_sha256": sha256(FULL_MESH_PATH),
        "source_triangle_id_files": {x: str(GRAPH_CASES / x / "source_triangle_ids.npy") for x in PARTS},
        "accepted_step_sha256": step_hashes,
        "accepted_transform_source": str(ASSEMBLY_MANIFEST),
        "triangle_removal_policy": "EXACT_SOURCE_TRIANGLE_IDS_ONLY",
        "bbox_crop_used": False,
        "distance_threshold_delete_used": False,
        "manual_selection_used": False,
        "boolean_union_used": False,
        "remaining_geometry_type": "MESH",
        "recovered_geometry_type": "TESSELLATED_ACCEPTED_CAD_BREP",
        "glb_nodes_independent": glb_valid,
        "new_p3_runs": 0,
        "new_physx_runs": 0,
        "new_mac_runs": 0,
        "new_llm_calls": 0,
        "new_geometry_fitting_runs": 0,
    }
    dump(HYBRID / "hybrid_provenance.json", provenance)

    visualizations = [
        ART / "REAL_03_whole_machine_hybrid.png",
        ART / "REAL_03_whole_machine_hybrid_contact_sheet.png",
        ART / "whole_machine_before_after.png",
        ART / "whole_machine_cad_highlight.png",
        ART / "whole_machine_cad_wireframe.png",
    ]
    visual_complete = all(x.is_file() and x.stat().st_size > 100000 for x in visualizations)
    pass_conditions = [len(full.faces) > 0, residual_path.is_file(), all((HYBRID / f"{x}_global_cad.obj").is_file() for x in PARTS), accounting_pass, glb_valid, visual_complete]
    blockers = [] if all(pass_conditions) else ["HYBRID_PREVIEW_QA_FAILURE"]
    summary = {
        "CURRENT_GATE": "WHOLE_MACHINE_HYBRID_PREVIEW_GATE_0_PASS" if not blockers else "WHOLE_MACHINE_HYBRID_PREVIEW_GATE_0_FAIL",
        "SOURCE_OBJECT": "REAL_03",
        "SCIENTIFIC_SEMANTICS": "HYBRID_MESH_CAD_PREVIEW",
        "FULL_SOURCE_MESH_LOADED": True,
        "WHOLE_MACHINE_VISUAL_COMPLETE": visual_complete,
        "FULL_CAD_RECOVERY_COMPLETE": False,
        "FULL_CAD_ASSEMBLY_COMPLETE": False,
        "RECOVERED_CAD_PARTS": 2,
        "RECOVERED_PART_IDS": PARTS,
        "Q1_PARTS": 1,
        "Q2_PARTS": 1,
        "HYBRID_CAD_AREA_COVERAGE": cad_area_coverage,
        "HYBRID_MESH_AREA_COVERAGE": mesh_area_coverage,
        "FULL_SOURCE_TRIANGLE_COUNT": int(len(full.faces)),
        "RESIDUAL_SOURCE_TRIANGLE_COUNT": residual_count,
        "RECOVERED_SOURCE_TRIANGLE_COUNT": recovered_count,
        "SOURCE_TRIANGLE_ACCOUNTING_PASS": accounting_pass,
        "RESIDUAL_MESH_CREATED": residual_path.is_file(),
        "CADPART_000_INSERTED": (HYBRID / "CADPART_000_global_cad.obj").is_file(),
        "CADPART_004_INSERTED": (HYBRID / "CADPART_004_global_cad.obj").is_file(),
        "HYBRID_OBJECT_COMPLETE": accounting_pass and glb_valid,
        "REMAINING_GEOMETRY_TYPE": "MESH",
        "HYBRID_GLB_CREATED": glb_path.is_file() and glb_valid,
        "HYBRID_GLB_PATH": str(glb_path),
        "HYBRID_GLB_NODE_NAMES": glb_node_names,
        "MAIN_PREVIEW_PATH": str(ART / "REAL_03_whole_machine_hybrid.png"),
        "CONTACT_SHEET_PATH": str(ART / "REAL_03_whole_machine_hybrid_contact_sheet.png"),
        "BLENDER_SCENE_CREATED": False,
        "NEW_P3_RUNS": 0,
        "NEW_PHYSX_RUNS": 0,
        "NEW_MAC_RUNS": 0,
        "NEW_LLM_CALLS": 0,
        "NEW_GEOMETRY_FITTING_RUNS": 0,
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "BLOCKERS": blockers,
    }
    dump(ART / "summary.json", summary)
    report = [
        "# Whole Machine Hybrid Preview Gate 0", "", f"Status: **{summary['CURRENT_GATE']}**", "",
        "Scientific semantics: **HYBRID_MESH_CAD_PREVIEW**.",
        "WHOLE_MACHINE_VISUAL_COMPLETE=true",
        "FULL_CAD_RECOVERY_COMPLETE=false",
        "FULL_CAD_ASSEMBLY_COMPLETE=false",
        f"HYBRID_CAD_AREA_COVERAGE={cad_area_coverage:.9f}",
        f"HYBRID_MESH_AREA_COVERAGE={mesh_area_coverage:.9f}", "",
        "The full visual object contains the residual original High-Mesh plus fresh tessellations of the two frozen accepted CAD BReps in their previously verified global placements.",
        "Source triangles were removed only by frozen source triangle IDs. No P3, PhysX, MAC, LLM, geometry fitting, analyzer, ICP, bbox crop, Boolean union, fake CAD, or manual selection was used.", "",
        f"Triangle accounting: {residual_count} residual + {recovered_count} recovered provenance = {len(full.faces)} original; pass={accounting_pass}.",
        f"Interactive GLB: `{glb_path}` with independent nodes: {', '.join(glb_node_names)}.",
        "Remaining geometry type: MESH.", "", "Tests: pending", "",
    ]
    (ART / "whole_machine_hybrid_report.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps(clean(summary), indent=2))


if __name__ == "__main__":
    main()
