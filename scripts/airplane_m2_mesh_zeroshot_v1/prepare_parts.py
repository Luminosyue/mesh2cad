#!/usr/bin/env python3
"""Airplane X-Part mesh → SpatialLM B0/M2 zero-shot stress test (mesh-derived curves).

Uses existing X-Part 9/9 watertight meshes only — does NOT re-run P3/X-Part.

Domain note: M2 was trained mainly on B-Rep oracle curves; airplane inputs use
mesh sharp-edge → fitted curves. Report as mesh-derived curve zero-shot stress test.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
import trimesh

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(REPO / "scripts"),
    str(REPO / "SpatialLM"),
    str(REPO / "scripts" / "geometry_pack_v1"),
    str(REPO / "scripts" / "separate_edge_tokens_v1"),
    str(REPO / "scripts" / "geometry_pack_v1"),
]

from geometry_pack_v1.mesh_edges import detect_sharp_edges  # noqa: E402
from geometry_pack_v1.surface import sample_surface_uniform  # noqa: E402
from mesh_edge_to_curve_v1.grouping import (  # noqa: E402
    resample_polyline,
    tangents_from_points,
)
from curve_token_v1.fit_curves_from_points import (  # noqa: E402
    fit_circle,
    fit_ellipse,
    fit_line,
)
from spatiallm_curve_token_v1.config import (  # noqa: E402
    CURVE_TOKEN_DIM,
    DEFAULT_CKPT,
    MAX_CURVE_TOKENS,
)
from spatiallm_curve_token_v1.export_curve_tokens import (  # noqa: E402
    curve_inputs,
    load_backbone,
)
from curve_token_head_v1.config import TYPE_TO_ID  # noqa: E402

XPART_ROOT = REPO / "ours3" / "airplane_p3_xpart_cadfit_routea_v1" / "xpart"
OUT_ROOT = REPO / "ours3" / "airplane_m2_mesh_zeroshot_v1"
TARGET_DIAGONAL = 6.0
NUM_SURFACE = 4096
SHARP_DEG = 30.0
N_CURVE_PTS = 32
MIN_CHAIN_SEGS = 3
SEED = 0

PART_ROLES = {
    "PART_000": "vertical_tail",
    "PART_001": "left_wing",
    "PART_002": "left_propeller",
    "PART_003": "right_propeller",
    "PART_004": "right_wing",
    "PART_005": "fuselage",
    "PART_006": "right_tailplane",
    "PART_007": "left_tailplane",
    "PART_008": "dorsal_feature",
}


def load_mesh(part_id: str) -> trimesh.Trimesh:
    path = XPART_ROOT / part_id / f"complete_part_{part_id.split('_')[1]}.obj"
    if not path.is_file():
        raise FileNotFoundError(path)
    mesh = trimesh.load(path, force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh):
        mesh = trimesh.util.concatenate(tuple(mesh.geometry.values()))
    mesh.remove_unreferenced_vertices()
    return mesh


def planar_ratio(mesh: trimesh.Trimesh) -> float:
    """Fraction of area whose face normal is near a dominant plane cluster."""
    areas = mesh.area_faces
    normals = mesh.face_normals
    if areas.sum() <= 0:
        return 0.0
    # bin normals on a coarse sphere; take largest bin mass
    # (simple proxy for "how planar" the part is)
    n = normals / (np.linalg.norm(normals, axis=1, keepdims=True) + 1e-12)
    # fold antipodes so opposite faces of a thin plate count together
    n = np.where(n[:, 2:3] < 0, -n, n)
    keys = np.round(n, 1)
    # hash rows
    uniq, inv = np.unique(keys, axis=0, return_inverse=True)
    masses = np.bincount(inv, weights=areas)
    return float(masses.max() / areas.sum())


def canonical_transform(vertices: np.ndarray) -> dict:
    vmin = vertices.min(0)
    vmax = vertices.max(0)
    diag = float(np.linalg.norm(vmax - vmin))
    scale = TARGET_DIAGONAL / diag if diag > 0 else 1.0
    translation = (-scale * vmin).astype(np.float64)
    center = ((vmin + vmax) * 0.5).tolist()
    return {
        "schema": "airplane_m2_mesh_zeroshot_v1",
        "target_diagonal": TARGET_DIAGONAL,
        "source_bbox_min": vmin.tolist(),
        "source_bbox_max": vmax.tolist(),
        "source_bbox_diagonal": diag,
        "scale": scale,
        "translation": translation.tolist(),
        # assembly-friendly view (identity rotation; scale about bbox min via s,t)
        "center": center,
        "uniform_scale": scale,
        "rotation": [1, 0, 0, 0, 1, 0, 0, 0, 1],
        "note": "p_canonical = scale * p_source + translation; "
        "p_source = (p_canonical - translation) / scale",
    }


def apply_tf(pts: np.ndarray, tf: dict) -> np.ndarray:
    s = float(tf["scale"])
    t = np.asarray(tf["translation"], dtype=np.float64)
    return np.asarray(pts, dtype=np.float64) * s + t


def invert_tf(pts: np.ndarray, tf: dict) -> np.ndarray:
    s = float(tf["scale"])
    t = np.asarray(tf["translation"], dtype=np.float64)
    return (np.asarray(pts, dtype=np.float64) - t) / s


def chain_sharp_segments(vertex_indices: np.ndarray) -> list[list[int]]:
    """GT-free chains: split sharp-edge graph at junctions (degree != 2)."""
    if len(vertex_indices) == 0:
        return []
    from collections import defaultdict

    adj: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for i, (a, b) in enumerate(vertex_indices.tolist()):
        adj[a].append((b, i))
        adj[b].append((a, i))

    used = set()
    chains: list[list[int]] = []

    def walk(start_v: int, first_seg: int) -> list[int]:
        path = [first_seg]
        used.add(first_seg)
        a, b = vertex_indices[first_seg]
        prev, cur = (b, a) if start_v == a else (a, b)
        # cur is the far endpoint we just arrived at? start_v is start, we leave to other
        prev = start_v
        cur = b if start_v == a else a
        while True:
            if len(adj[cur]) != 2:
                break
            nxt = None
            for nb, si in adj[cur]:
                if si in used:
                    continue
                if nb == prev:
                    continue
                nxt = (nb, si)
                break
            if nxt is None:
                # closed loop continuation
                for nb, si in adj[cur]:
                    if si not in used:
                        nxt = (nb, si)
                        break
            if nxt is None:
                break
            nb, si = nxt
            used.add(si)
            path.append(si)
            prev, cur = cur, nb
            if cur == start_v:
                break
        return path

    # start from endpoints (degree 1) then leftover loops
    endpoints = [v for v, es in adj.items() if len(es) == 1]
    for v in endpoints:
        for nb, si in adj[v]:
            if si not in used:
                chains.append(walk(v, si))

    for i in range(len(vertex_indices)):
        if i in used:
            continue
        a, b = vertex_indices[i]
        chains.append(walk(a, i))

    return [c for c in chains if len(c) >= MIN_CHAIN_SEGS]


def ordered_polyline_from_chain(
    chain: list[int], v0: np.ndarray, v1: np.ndarray, vertex_indices: np.ndarray
) -> np.ndarray | None:
    """Walk segment indices into an ordered vertex polyline."""
    if not chain:
        return None
    # build local adjacency of segments
    pts = []
    a0, b0 = vertex_indices[chain[0]]
    # orient first segment arbitrarily
    cur_end = b0
    pts.extend([v0[chain[0]], v1[chain[0]]])
    # Actually use vertex coords from indices via v0/v1 mapping
    # Prefer reconstructing from shared vertices
    from collections import defaultdict

    seg_of = {}
    for si in chain:
        a, b = map(int, vertex_indices[si])
        seg_of.setdefault(frozenset((a, b)), si)

    # BFS-like along chain order already produced by walk — use chain order
    # Rebuild points by connecting segments
    a, b = map(int, vertex_indices[chain[0]])
    # map vertex id -> position from any segment endpoint
    pos = {}
    for si in chain:
        aa, bb = map(int, vertex_indices[si])
        # v0/v1 correspond to vertex_indices order (sorted in detect_sharp_edges)
        # so v0[si] is coords of idx[:,0], v1 of idx[:,1]
        pos[aa] = v0[si] if aa == int(vertex_indices[si, 0]) else v1[si]
        pos[bb] = v1[si] if bb == int(vertex_indices[si, 1]) else v0[si]
        # safer: always
        pos[int(vertex_indices[si, 0])] = v0[si]
        pos[int(vertex_indices[si, 1])] = v1[si]

    path_vids = [a, b]
    used = {chain[0]}
    cur = b
    for _ in range(len(chain) - 1):
        found = False
        for si in chain:
            if si in used:
                continue
            aa, bb = map(int, vertex_indices[si])
            if aa == cur:
                path_vids.append(bb)
                cur = bb
                used.add(si)
                found = True
                break
            if bb == cur:
                path_vids.append(aa)
                cur = aa
                used.add(si)
                found = True
                break
        if not found:
            break
    poly = np.stack([pos[v] for v in path_vids if v in pos], axis=0)
    if len(poly) < 2:
        return None
    # dedup consecutive
    keep = [0]
    for i in range(1, len(poly)):
        if np.linalg.norm(poly[i] - poly[keep[-1]]) > 1e-9:
            keep.append(i)
    poly = poly[keep]
    if float(np.linalg.norm(np.diff(poly, axis=0), axis=1).sum()) < 1e-8:
        return None
    return poly


def classify_curve(pts: np.ndarray, diag: float) -> tuple[str, float]:
    """Pick LINE/CIRCLE/ELLIPSE/BSPLINE by residual; fallback BSPLINE."""
    tol = 0.01 * diag
    candidates = []
    try:
        fl = fit_line(pts)
        candidates.append(("LINE", float(fl["rms_residual"])))
    except Exception:
        pass
    try:
        fc = fit_circle(pts)
        if fc.get("ok", True) and "rms_residual" in fc:
            candidates.append(("CIRCLE", float(fc["rms_residual"])))
    except Exception:
        pass
    try:
        fe = fit_ellipse(pts)
        if fe.get("ok", False):
            candidates.append(("ELLIPSE", float(fe["rms_residual"])))
    except Exception:
        pass
    if not candidates:
        return "BSPLINE", float("inf")
    ctype, rms = min(candidates, key=lambda x: x[1])
    if rms > tol * 3:
        return "BSPLINE", rms
    return ctype, rms


def prepare_part(part_id: str, out_dir: Path, encoder, device) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh = load_mesh(part_id)
    verts = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    tf = canonical_transform(verts)
    (out_dir / "transform.json").write_text(json.dumps(tf, indent=2) + "\n")

    verts_c = apply_tf(verts, tf)
    mesh_c = trimesh.Trimesh(vertices=verts_c, faces=faces, process=False)

    # surface
    pts, nrm, _ = sample_surface_uniform(verts_c, faces, NUM_SURFACE, SEED)
    surface = np.concatenate([pts, nrm], axis=1).astype(np.float32)
    np.save(out_dir / "surface_points.npy", surface)

    # sharp edges
    adj = np.asarray(mesh_c.face_adjacency, dtype=np.int64)
    adj_e = np.asarray(mesh_c.face_adjacency_edges, dtype=np.int64)
    sharp = detect_sharp_edges(verts_c, faces, adj, adj_e, SHARP_DEG)
    chains = chain_sharp_segments(sharp["vertex_indices"])

    curves_meta = []
    feats_list, scales_list, types, lengths = [], [], [], []
    for ci, chain in enumerate(chains):
        poly = ordered_polyline_from_chain(
            chain, sharp["v0"], sharp["v1"], sharp["vertex_indices"]
        )
        if poly is None or len(poly) < 2:
            continue
        plen = float(np.linalg.norm(np.diff(poly, axis=0), axis=1).sum())
        if plen < 1e-4:
            continue
        xyz = resample_polyline(poly, N_CURVE_PTS)
        tan = tangents_from_points(xyz)
        ctype, rms = classify_curve(xyz, TARGET_DIAGONAL)
        if ctype not in TYPE_TO_ID:
            ctype = "BSPLINE"
        f, sc = curve_inputs(xyz, tan.astype(np.float32))
        feats_list.append(f)
        scales_list.append(sc)
        types.append(ctype)
        lengths.append(plen)
        curves_meta.append(
            {
                "curve_index": ci,
                "type": ctype,
                "poly_len": plen,
                "rms_fit": rms,
                "n_segs": len(chain),
            }
        )

    # rank by length, cap
    order = np.argsort([-L for L in lengths])[:MAX_CURVE_TOKENS] if lengths else []
    kept_meta = [curves_meta[i] for i in order]
    if order.size == 0:
        tokens = np.zeros((0, CURVE_TOKEN_DIM), dtype=np.float32)
    else:
        feats = np.stack([feats_list[i] for i in order], 0)
        scales = np.stack([scales_list[i] for i in order], 0)
        with torch.no_grad():
            out = encoder(
                torch.from_numpy(feats).to(device),
                torch.from_numpy(scales).to(device),
            )
            tokens = out["token"].float().cpu().numpy().astype(np.float32)

    np.save(out_dir / "curve_tokens.npy", tokens)
    (out_dir / "curves_meta.json").write_text(
        json.dumps(
            {
                "part_id": part_id,
                "role": PART_ROLES.get(part_id),
                "n_sharp_segments": int(sharp["num_segments"]),
                "n_chains": len(chains),
                "n_curves_kept": int(len(tokens)),
                "truncated": bool(len(curves_meta) > len(tokens)),
                "type_counts": {
                    t: sum(1 for m in kept_meta if m["type"] == t) for t in TYPE_TO_ID
                },
                "curves": kept_meta,
                "planar_ratio": planar_ratio(mesh),
            },
            indent=2,
        )
        + "\n"
    )
    # also save mesh copy path + sharp for viz
    mesh_c.export(out_dir / "mesh_canonical.obj")
    np.savez_compressed(
        out_dir / "mesh_sharp_edges.npz",
        v0=sharp["v0"],
        v1=sharp["v1"],
        dihedral_deg=sharp["dihedral_deg"],
    )
    summary = {
        "part_id": part_id,
        "role": PART_ROLES.get(part_id),
        "planar_ratio": planar_ratio(mesh),
        "n_surface": int(surface.shape[0]),
        "n_curve_tokens": int(len(tokens)),
        "n_sharp_segments": int(sharp["num_segments"]),
        "watertight": bool(mesh.is_watertight),
    }
    (out_dir / "prepare_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", nargs="+", default=None)
    ap.add_argument("--canary", action="store_true")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    all_parts = [f"PART_{i:03d}" for i in range(9)]

    # planar ratios for auto canary pick
    ratios = {p: planar_ratio(load_mesh(p)) for p in all_parts}
    (OUT_ROOT / "planar_ratios.json").write_text(json.dumps(ratios, indent=2) + "\n")
    best_planar = max(ratios, key=ratios.get)
    print("planar_ratios:", json.dumps(ratios, indent=2))
    print("highest planar:", best_planar, ratios[best_planar])

    if args.canary:
        # user table + auto planar; use PART_008 as Route-B topology hard case
        parts = []
        for p in [best_planar, "PART_001", "PART_003", "PART_005", "PART_008"]:
            if p not in parts:
                parts.append(p)
        parts = parts[:5]
    elif args.parts:
        parts = args.parts
    else:
        parts = all_parts

    device = torch.device(args.device)
    encoder, ckpt = load_backbone(DEFAULT_CKPT, device)
    print(f"[prepare] encoder {DEFAULT_CKPT} exp={ckpt.get('exp')}")

    rows = []
    for p in parts:
        print(f"=== prepare {p} ===", flush=True)
        rows.append(prepare_part(p, OUT_ROOT / "parts" / p, encoder, device))
        print(json.dumps(rows[-1]), flush=True)

    (OUT_ROOT / "prepare_manifest.json").write_text(
        json.dumps({"parts": rows, "canary": bool(args.canary)}, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
