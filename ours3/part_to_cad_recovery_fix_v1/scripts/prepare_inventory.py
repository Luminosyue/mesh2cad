#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import trimesh
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "part_to_cad_recovery_fix_v1"
DIAG = ROOT / "parallel_pipeline_diagnostics_v1/task_b/artifacts"
BATCH = ROOT / "batch_real_mesh2cad_v1/cases"


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path, default=None):
    try: return json.loads(Path(path).read_text())
    except Exception: return default


def global_p3_components(mesh, tri_map):
    """Reproduce Task B's global sparse-component labels exactly.

    ``p3_connected_component`` is not a per-segment rank.  It is the component
    label returned for the full source-face graph after removing adjacency
    edges crossing P3 labels.
    """
    adjacency = np.asarray(mesh.face_adjacency, np.int64)
    keep = (tri_map[adjacency[:, 0]] == tri_map[adjacency[:, 1]]) & (tri_map[adjacency[:, 0]] >= 0)
    a, b = adjacency[keep].T
    data = np.ones(len(a) * 2, dtype=np.uint8)
    graph = coo_matrix((data, (np.r_[a, b], np.r_[b, a])), shape=(len(mesh.faces), len(mesh.faces))).tocsr()
    return connected_components(graph, directed=False, return_labels=True)[1]


def main():
    manifest = {"schema": "PART_TO_CAD_RECOVERY_FIX_V1_INPUTS", "cases": {}}
    for case_num in (6, 7):
        cid = f"CASE_{case_num:02d}"; case_lower = f"case{case_num:02d}"
        graph_path = DIAG / f"case{case_num:02d}_cad_part_graph.json"
        graph = read(graph_path); source_path = Path(graph["source_obj"])
        mesh = trimesh.load(source_path, force="mesh", process=False)
        tri_map_path = BATCH / cid / "p3/triangle_part_id.npy"
        tri_map = np.load(tri_map_path)
        if len(tri_map) != len(mesh.faces): raise RuntimeError(f"triangle map mismatch {cid}: {len(tri_map)} != {len(mesh.faces)}")
        p3_cc = global_p3_components(mesh, tri_map)
        case_entry = {"source_obj": str(source_path), "source_sha256": sha(source_path), "graph": str(graph_path), "parts": []}
        for node in graph["nodes"]:
            part_id = node["cad_part_id"]; segment = int(node["p3_segment_id"]); component_label = int(node["p3_connected_component"])
            face_ids = np.flatnonzero((tri_map == segment) & (p3_cc == component_label))
            if not len(face_ids): raise RuntimeError(f"global component {component_label} unavailable for {cid}/{part_id}")
            if len(face_ids) != int(node["triangle_count"]):
                raise RuntimeError(f"triangle-count mismatch for {cid}/{part_id}: {len(face_ids)} != {node['triangle_count']}")
            sub = mesh.submesh([face_ids], append=True, repair=False)
            part_dir = OUT / case_lower / "parts" / part_id; inp = part_dir / "input"; inp.mkdir(parents=True, exist_ok=True)
            mesh_path = inp / "source_part.obj"; sub.export(mesh_path)

            old = BATCH / cid / "cad_part_graph" / f"CADPART_{segment:03d}" / "router"
            ga = old / "geometry_analysis"; spec_path = old / "cad_spec/cad_spec_v0.json"; cadability_path = old / "cad_spec/cadability.json"
            feature_graph = {
                "schema": "CAD_FEATURE_GRAPH_V1", "case_id": cid, "part_id": part_id,
                "source": "EXISTING_GEOMETRY_ANALYZER_ONLY", "raw_mesh_included": False,
                "feature_hypotheses": read(ga / "feature_hypotheses.json", {}),
                "primitives": read(ga / "primitives.json", {}),
                "hole_candidates": read(ga / "hole_candidates.json", {}),
                "repeated_feature_hypotheses": read(ga / "repeated_feature_hypotheses.json", {}),
                "symmetry": read(ga / "symmetry.json", {}), "principal_axes": read(ga / "principal_axes.json", {}),
            }
            bounds = np.asarray(sub.bounds, float); extents = bounds[1] - bounds[0]
            measured = read(spec_path, {}) or {}
            measured_spec = {
                "schema": "MEASURED_CAD_SPEC_V1", "case_id": cid, "part_id": part_id,
                "source": "EXISTING_CAD_SPEC_PLUS_MEASURED_GRAPH_NODE", "raw_mesh_included": False,
                "existing_cad_spec": measured, "cadability": read(cadability_path, {}),
                "measurements_source_frame": {"bbox_min": bounds[0].tolist(), "bbox_max": bounds[1].tolist(), "extents": extents.tolist(), "centroid": np.asarray(sub.center_mass if np.isfinite(sub.center_mass).all() else sub.centroid).tolist(), "surface_area": float(sub.area), "volume": float(abs(sub.volume)) if sub.is_volume else None},
                "graph_evidence": {k: node[k] for k in ("p3_segment_id", "p3_connected_component", "triangle_count", "source_area", "source_area_ratio", "source_connected_components", "assignment_source")},
            }
            dump(inp / "cad_feature_graph.json", feature_graph); dump(inp / "measured_cad_spec.json", measured_spec)
            old_candidates = []
            recovery = BATCH / cid / "cad_recovery" / f"CADPART_{segment:03d}"
            if recovery.is_dir():
                for step in sorted(recovery.rglob("*.step")): old_candidates.append({"path": str(step), "sha256": sha(step), "bytes": step.stat().st_size})
            entry = {
                "part_id": part_id, "p3_segment_id": segment, "p3_connected_component": component_label,
                "mesh": str(mesh_path), "mesh_sha256": sha(mesh_path), "triangle_count": len(sub.faces),
                "source_area": float(node["source_area"]), "source_area_ratio": float(node["source_area_ratio"]),
                "cad_feature_graph": str(inp / "cad_feature_graph.json"), "measured_cad_spec": str(inp / "measured_cad_spec.json"),
                "old_candidates": old_candidates,
            }
            dump(inp / "input_manifest.json", entry); case_entry["parts"].append(entry)
        manifest["cases"][cid] = case_entry
        dump(OUT / case_lower / "input_manifest.json", case_entry)
        print(cid, "PARTS", len(case_entry["parts"]), "AREA", sum(p["source_area_ratio"] for p in case_entry["parts"]), flush=True)
    dump(OUT / "manifest/input_inventory.json", manifest)


if __name__ == "__main__": main()
