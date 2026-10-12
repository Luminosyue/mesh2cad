#!/usr/bin/env python3
"""Build mesh-dihedral C2 curve tokens for toaster X-Parts.

Reuses frozen toaster P1 surface_points.npy + transform.json.
Detects dihedral sharp edges on the X-Part mesh in that same canonical frame.
Encodes with official C2_frozen_v1. No GT CAD / BRep.
"""
from __future__ import annotations

import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
import trimesh

REPO = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [
    str(REPO / "scripts"),
    str(REPO / "scripts" / "geometry_pack_v1"),
]

from geometry_pack_v1.mesh_edges import detect_sharp_edges  # noqa: E402
from mesh_edge_to_curve_v1.grouping import resample_polyline, tangents_from_points  # noqa: E402
from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import (  # noqa: E402
    curve_inputs,
    load_backbone,
)
from spatiallm_curve_token_v1.config import CURVE_TOKEN_DIM, MAX_CURVE_TOKENS  # noqa: E402
from curve_encoder_scale_curvature_v1.config import TYPE_TO_ID  # noqa: E402
from curve_token_v1.fit_curves_from_points import fit_circle, fit_ellipse, fit_line  # noqa: E402

OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/tire_part006_p1_inference_20260919")
TOASTER_P1 = OUT
XPART = REPO / "ours3" / "toaster_p3_xpart_cadfit_routea_v1" / "xpart"
C2_CKPT = REPO / "ours3" / "curve_encoder_scale_curvature_v1" / "runs" / "C2_frozen_v1" / "best.pt"
SHARP_DEG = 30.0
N_CURVE_PTS = 32
MIN_CHAIN_SEGS = 3
TARGET_DIAGONAL = 6.0
PARTS = ["PART_006"]


def _load_mesh(part_id: str) -> trimesh.Trimesh:
    path = OUT / "source.stl"
    mesh = trimesh.load(str(path), force="mesh", process=True)
    mesh.remove_unreferenced_vertices()
    return mesh, path


def _tf_from_toaster(raw: dict) -> dict:
    t = raw["transform"]
    return {
        "source_bbox_min": t["source_bbox_min"],
        "source_bbox_max": t["source_bbox_max"],
        "source_diagonal": t["source_diagonal"],
        "target_diagonal": t["target_diagonal"],
        "scale": t["scale"],
        "translation": t["translation"],
    }


def _apply_tf(pts: np.ndarray, tf: dict) -> np.ndarray:
    s = float(tf["scale"])
    tr = np.asarray(tf["translation"], dtype=np.float64)
    return np.asarray(pts, dtype=np.float64) * s + tr


def chain_sharp_segments(vertex_indices: np.ndarray) -> list[list[int]]:
    if len(vertex_indices) == 0:
        return []
    adj: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for i, (a, b) in enumerate(vertex_indices.tolist()):
        adj[a].append((b, i))
        adj[b].append((a, i))
    used: set[int] = set()
    chains: list[list[int]] = []

    def walk(start_v: int, first_seg: int) -> list[int]:
        path = [first_seg]
        used.add(first_seg)
        a, b = vertex_indices[first_seg]
        prev = start_v
        cur = int(b if start_v == a else a)
        while True:
            if len(adj[cur]) != 2:
                break
            nxt = None
            for nb, si in adj[cur]:
                if si in used or nb == prev:
                    continue
                nxt = (nb, si)
                break
            if nxt is None:
                for nb, si in adj[cur]:
                    if si not in used:
                        nxt = (nb, si)
                        break
            if nxt is None:
                break
            nb, si = nxt
            used.add(si)
            path.append(si)
            prev, cur = cur, int(nb)
            if cur == start_v:
                break
        return path

    for v, es in adj.items():
        if len(es) == 1:
            for nb, si in es:
                if si not in used:
                    chains.append(walk(v, si))
    for i in range(len(vertex_indices)):
        if i not in used:
            a, b = vertex_indices[i]
            chains.append(walk(int(a), i))
    return [c for c in chains if len(c) >= MIN_CHAIN_SEGS]


def ordered_polyline_from_chain(
    chain: list[int], v0: np.ndarray, v1: np.ndarray, vertex_indices: np.ndarray
) -> np.ndarray | None:
    if not chain:
        return None
    pos = {}
    for si in chain:
        pos[int(vertex_indices[si, 0])] = v0[si]
        pos[int(vertex_indices[si, 1])] = v1[si]
    a, b = map(int, vertex_indices[chain[0]])
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
    keep = [0]
    for i in range(1, len(poly)):
        if np.linalg.norm(poly[i] - poly[keep[-1]]) > 1e-9:
            keep.append(i)
    poly = poly[keep]
    if len(poly) < 2:
        return None
    if float(np.linalg.norm(np.diff(poly, axis=0), axis=1).sum()) < 1e-8:
        return None
    return poly


def classify_curve(pts: np.ndarray) -> tuple[str, float]:
    tol = 0.01 * TARGET_DIAGONAL
    candidates = []
    try:
        candidates.append(("LINE", float(fit_line(pts)["rms_residual"])))
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


def prepare_part(part_id: str, encoder, device) -> dict:
    src_in = TOASTER_P1 / "inputs" / part_id
    out_dir = OUT / "packs" / part_id
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_in / "surface_points.npy", out_dir / "surface_points.npy")
    shutil.copy2(src_in / "transform.json", out_dir / "transform.json")
    if (src_in / "input_meta.json").is_file():
        shutil.copy2(src_in / "input_meta.json", out_dir / "input_meta.json")

    raw_tf = json.loads((src_in / "transform.json").read_text())
    tf = _tf_from_toaster(raw_tf)
    (out_dir / "coordinate_transform.json").write_text(json.dumps(tf, indent=2) + "\n")

    mesh, mesh_path = _load_mesh(part_id)
    verts_c = _apply_tf(np.asarray(mesh.vertices, dtype=np.float64), tf)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    mesh_c = trimesh.Trimesh(vertices=verts_c, faces=faces, process=False)
    adj = np.asarray(mesh_c.face_adjacency, dtype=np.int64)
    adj_e = np.asarray(mesh_c.face_adjacency_edges, dtype=np.int64)
    if len(adj) == 0:
        sharp = {
            "v0": np.zeros((0, 3)),
            "v1": np.zeros((0, 3)),
            "vertex_indices": np.zeros((0, 2), dtype=np.int64),
            "dihedral_deg": np.zeros((0,)),
            "num_segments": 0,
        }
    else:
        sharp = detect_sharp_edges(verts_c, faces, adj, adj_e, SHARP_DEG)
    chains = chain_sharp_segments(sharp["vertex_indices"])

    feats_list, scales_list, lengths, meta = [], [], [], []
    diagnostic = []
    for ci, chain in enumerate(chains):
        poly = ordered_polyline_from_chain(
            chain, sharp["v0"], sharp["v1"], sharp["vertex_indices"]
        )
        if poly is None:
            continue
        plen = float(np.linalg.norm(np.diff(poly, axis=0), axis=1).sum())
        if plen < 1e-4:
            continue
        xyz = resample_polyline(poly, N_CURVE_PTS)
        tan = tangents_from_points(xyz)
        ctype, rms = classify_curve(xyz)
        if ctype not in TYPE_TO_ID:
            ctype = "BSPLINE"
        f, sc = curve_inputs(xyz, tan.astype(np.float32))
        diagnostic.append({"polyline":poly.tolist(),"encoder_xyz":xyz.tolist(),"type":ctype,"rms_fit":rms})
        feats_list.append(f)
        scales_list.append(sc)
        lengths.append(plen)
        meta.append(
            {
                "curve_index": ci,
                "type": ctype,
                "poly_len": plen,
                "rms_fit": rms,
                "n_segs": len(chain),
            }
        )

    order = np.argsort([-L for L in lengths])[:MAX_CURVE_TOKENS] if lengths else np.array([], dtype=int)
    kept = [meta[i] for i in order]
    (out_dir / "curve_diagnostics.json").write_text(json.dumps([diagnostic[i] for i in order],indent=2))
    empty_fallback = False
    if order.size == 0:
        tokens = np.zeros((1, CURVE_TOKEN_DIM), dtype=np.float32)
        empty_fallback = True
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
    np.savez_compressed(
        out_dir / "mesh_sharp_edges.npz",
        v0=sharp["v0"],
        v1=sharp["v1"],
        dihedral_deg=sharp["dihedral_deg"],
    )
    summary = {
        "part_id": part_id,
        "mesh_path": str(mesh_path),
        "n_surface": int(np.load(out_dir / "surface_points.npy").shape[0]),
        "n_sharp_segments": int(sharp["num_segments"]),
        "n_chains": len(chains),
        "n_curves_kept": int(0 if empty_fallback else len(tokens)),
        "n_curve_tokens_written": int(len(tokens)),
        "empty_sharp_fallback": "zero_token" if empty_fallback else None,
        "type_counts": {t: sum(1 for m in kept if m["type"] == t) for t in TYPE_TO_ID},
        "source": "XPART_MESH_DIHEDRAL_30DEG",
        "c2_checkpoint": str(C2_CKPT),
        "gt_brep_used": False,
    }
    (out_dir / "curves_meta.json").write_text(
        json.dumps({**summary, "curves": kept}, indent=2) + "\n"
    )
    (out_dir / "prepare_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main() -> int:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoder, ckpt = load_backbone(C2_CKPT, device)
    print(f"[prepare] C2 {C2_CKPT} exp={ckpt.get('exp')} device={device}", flush=True)
    rows = []
    for p in PARTS:
        print(f"=== prepare {p} ===", flush=True)
        row = prepare_part(p, encoder, device)
        rows.append(row)
        print(json.dumps(row), flush=True)
    man = {
        "n": len(rows),
        "sharp_angle_deg": SHARP_DEG,
        "c2_checkpoint": str(C2_CKPT),
        "surface_source": str(TOASTER_P1 / "inputs"),
        "mesh_source": str(XPART),
        "gt_brep_used": False,
        "parts": rows,
    }
    (OUT / "manifest" / "prepare_manifest.json").parent.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest" / "prepare_manifest.json").write_text(json.dumps(man, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
