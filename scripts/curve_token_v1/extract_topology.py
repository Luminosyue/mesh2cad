#!/usr/bin/env python3
"""B-Rep topology extraction for Track B.

Curve Tokens are meant to grow from "geometry only" to "geometry + topology +
surface-curve incidence", so an isolated curve list is not enough. Local indices
are the 0-based OCC IndexedMap order, which is deterministic for a given STEP
file and shared by curves.json / curve_samples.npz / topology.json.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from .config import SCHEMA_VERSION
from .occ_curve_v1 import pnt_to_np


def _is_closed(edge_id: int, curve_records: list[dict]) -> bool:
    for r in curve_records:
        if int(r["edge_id"]) == edge_id:
            return bool(r.get("is_closed", False))
    return False


def extract_topology(shape, curve_records: list[dict]) -> dict:
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_VERTEX
    from OCP.TopExp import TopExp
    from OCP.TopoDS import TopoDS
    from OCP.TopTools import (
        TopTools_IndexedDataMapOfShapeListOfShape,
        TopTools_IndexedMapOfShape,
    )

    edge_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, edge_map)
    vert_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_VERTEX, vert_map)
    face_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_FACE, face_map)

    n_e, n_v, n_f = int(edge_map.Size()), int(vert_map.Size()), int(face_map.Size())

    vertex_xyz = np.zeros((n_v, 3), dtype=np.float64)
    for i in range(1, n_v + 1):
        vertex_xyz[i - 1] = pnt_to_np(BRep_Tool.Pnt_s(TopoDS.Vertex_s(vert_map.FindKey(i))))

    edge_faces_map = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, edge_faces_map)
    vert_edges_map = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_VERTEX, TopAbs_EDGE, vert_edges_map)

    # Only edges that survived into curve_records get topology rows, so indices
    # line up 1:1 with curves.json / the npz arrays.
    kept_edge_ids = [int(r["edge_id"]) for r in curve_records]
    kept = set(kept_edge_ids)

    edge_to_vertex: dict[int, list[int]] = {}
    edge_to_face: dict[int, list[int]] = {}
    face_to_edge: dict[int, list[int]] = defaultdict(list)
    vertex_to_edge: dict[int, list[int]] = defaultdict(list)

    from OCP.TopoDS import TopoDS_Vertex

    for eid in kept_edge_ids:
        edge = TopoDS.Edge_s(edge_map.FindKey(eid + 1))

        va, vb = TopoDS_Vertex(), TopoDS_Vertex()
        vs: list[int] = []
        try:
            TopExp.Vertices_s(edge, va, vb)
            for v in (va, vb):
                if v.IsNull():
                    vs.append(-1)
                    continue
                idx = vert_map.FindIndex(v)
                vs.append(int(idx) - 1 if idx > 0 else -1)
        except Exception:  # noqa: BLE001
            vs = [-1, -1]
        while len(vs) < 2:
            vs.append(-1)
        edge_to_vertex[eid] = vs[:2]

        fs: list[int] = []
        if edge_faces_map.Contains(edge):
            for f in edge_faces_map.FindFromKey(edge):
                idx = face_map.FindIndex(f)
                if idx > 0:
                    fs.append(int(idx) - 1)
        fs = sorted(set(fs))
        edge_to_face[eid] = fs
        for fid in fs:
            face_to_edge[fid].append(eid)

    for i in range(1, n_v + 1):
        v = vert_map.FindKey(i)
        es: list[int] = []
        if vert_edges_map.Contains(v):
            for e in vert_edges_map.FindFromKey(v):
                idx = edge_map.FindIndex(e)
                if idx > 0 and (int(idx) - 1) in kept:
                    es.append(int(idx) - 1)
        vertex_to_edge[i - 1] = sorted(set(es))

    # curve adjacency: edges sharing at least one vertex
    adjacency: dict[int, list[int]] = {}
    for eid in kept_edge_ids:
        neigh: set[int] = set()
        for vid in edge_to_vertex[eid]:
            if vid < 0:
                continue
            neigh.update(vertex_to_edge.get(vid, []))
        neigh.discard(eid)
        adjacency[eid] = sorted(neigh)

    n_faces_per_edge = np.array([len(edge_to_face[e]) for e in kept_edge_ids], dtype=np.int64)
    n_edges_per_face = np.array(
        [len(face_to_edge.get(f, [])) for f in range(n_f)], dtype=np.int64
    )

    n_kept = max(len(kept_edge_ids), 1)
    stats = {
        "num_curves": len(kept_edge_ids),
        "num_vertices": n_v,
        "num_faces": n_f,
        "num_topo_edges": n_e,
        "free_edges": int((n_faces_per_edge == 0).sum()),
        "boundary_edges": int((n_faces_per_edge == 1).sum()),
        "manifold_two_face_edges": int((n_faces_per_edge == 2).sum()),
        "non_manifold_edges": int((n_faces_per_edge > 2).sum()),
        "free_edge_pct": 100.0 * float((n_faces_per_edge == 0).sum()) / n_kept,
        "boundary_edge_pct": 100.0 * float((n_faces_per_edge == 1).sum()) / n_kept,
        "manifold_two_face_edge_pct": 100.0 * float((n_faces_per_edge == 2).sum()) / n_kept,
        "non_manifold_edge_pct": 100.0 * float((n_faces_per_edge > 2).sum()) / n_kept,
        "faces_per_edge_mean": float(n_faces_per_edge.mean()) if len(n_faces_per_edge) else 0.0,
        "faces_per_edge_max": int(n_faces_per_edge.max()) if len(n_faces_per_edge) else 0,
        "edges_per_face_mean": float(n_edges_per_face.mean()) if n_f else 0.0,
        "edges_per_face_max": int(n_edges_per_face.max()) if n_f else 0,
        "edges_with_missing_vertex": int(
            sum(1 for e in kept_edge_ids if -1 in edge_to_vertex[e])
        ),
    }

    # Self-consistency of the extracted incidence relations. Note this is
    # separate from manifoldness: a non-manifold edge (>2 faces) is a legitimate
    # property of unioned solids and is faithfully representable, so it is
    # reported as a statistic rather than treated as an extraction failure.
    issues: list[str] = []
    if not kept_edge_ids:
        issues.append("no curves")
    if stats["edges_with_missing_vertex"]:
        issues.append(f"{stats['edges_with_missing_vertex']} edge(s) missing a bounding vertex")
    for eid in kept_edge_ids:
        for fid in edge_to_face[eid]:
            if eid not in face_to_edge.get(fid, []):
                issues.append(f"edge {eid} not listed in face {fid}")
                break
        for vid in edge_to_vertex[eid]:
            if vid >= 0 and eid not in vertex_to_edge.get(vid, []):
                issues.append(f"edge {eid} not listed in vertex {vid}")
                break
        if len(issues) > 20:
            break
    for eid in kept_edge_ids:
        vs = edge_to_vertex[eid]
        # an open edge must be bounded by two distinct vertices; a closed one
        # legitimately references the same vertex twice
        if vs[0] == vs[1] and vs[0] >= 0 and eid in kept and not _is_closed(eid, curve_records):
            issues.append(f"open edge {eid} has coincident bounding vertices")
            break

    stats["consistency_issues"] = issues[:20]
    stats["is_manifold"] = bool(stats["non_manifold_edges"] == 0 and stats["free_edges"] == 0)
    valid = not issues

    return {
        "schema_version": SCHEMA_VERSION,
        "index_convention": "0-based OCC TopTools_IndexedMapOfShape order (shared with curves.json)",
        "validity_definition": (
            "topology_valid means the extracted incidence relations are mutually "
            "consistent and every curve is bounded; non-manifold edges are reported "
            "separately via stats.is_manifold and are not a validity failure"
        ),
        "edge_to_vertex": {str(k): v for k, v in edge_to_vertex.items()},
        "edge_to_face": {str(k): v for k, v in edge_to_face.items()},
        "vertex_to_edge": {str(k): v for k, v in vertex_to_edge.items()},
        "face_to_edge": {str(k): sorted(v) for k, v in face_to_edge.items()},
        "curve_adjacency": {str(k): v for k, v in adjacency.items()},
        "vertex_xyz": vertex_xyz.tolist(),
        "stats": stats,
        "topology_valid": bool(valid),
    }


def topology_arrays(topology: dict, curve_records: list[dict]) -> dict[str, np.ndarray]:
    """Flatten the variable-length incidence lists into npz-friendly arrays."""
    eids = [int(r["edge_id"]) for r in curve_records]
    e2v = np.array([topology["edge_to_vertex"][str(e)] for e in eids], dtype=np.int32) if eids else np.zeros((0, 2), np.int32)

    flat: list[int] = []
    offsets = [0]
    for e in eids:
        fs = topology["edge_to_face"][str(e)]
        flat.extend(int(x) for x in fs)
        offsets.append(len(flat))
    return {
        "edge_to_vertex": e2v,
        "edge_to_face_flat": np.array(flat, dtype=np.int32),
        "edge_to_face_offsets": np.array(offsets, dtype=np.int32),
        "vertex_xyz": np.asarray(topology["vertex_xyz"], dtype=np.float32).reshape(-1, 3),
    }
