#!/usr/bin/env python3
"""Convert existing Dora-SES feature edges to P1's frozen C2 token interface."""
from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path

import numpy as np
import torch
import trimesh

REPO = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = REPO / "ours3" / "toaster_p1_edge_condition_ablation_v1"
DORA = REPO / "ours3" / "toaster_p3_xpart_cadfit_routea_v1" / "dora_ses"
BASE_SCRIPT = OUT / "scripts" / "prepare_mesh_curves.py"
PARTS = [f"PART_{i:03d}" for i in range(39)]

spec = importlib.util.spec_from_file_location("mesh_curve_prepare", BASE_SCRIPT)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)


def main() -> int:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    encoder, ckpt = base.load_backbone(base.C2_CKPT, device)
    rows = []
    for part_id in PARTS:
        src_pack = OUT / "packs" / part_id
        dst = OUT / "packs_dora" / part_id
        dst.mkdir(parents=True, exist_ok=True)
        for name in ("surface_points.npy", "transform.json", "input_meta.json", "coordinate_transform.json"):
            if (src_pack / name).is_file():
                shutil.copy2(src_pack / name, dst / name)

        edge_npz = DORA / "threshold_15" / "parts" / part_id / "salient_edges.npz"
        mesh_path = DORA / "normalized" / f"{part_id}.obj"
        dora_tf = json.loads((DORA / "normalized" / part_id / "transform.json").read_text())
        p1_tf = json.loads((src_pack / "coordinate_transform.json").read_text())
        mesh = trimesh.load(str(mesh_path), force="mesh", process=False)
        vertices_dora = np.asarray(mesh.vertices, dtype=np.float64)
        vertices_xpart = vertices_dora / float(dora_tf["scale"]) + np.asarray(dora_tf["center"])
        vertices = vertices_xpart * float(p1_tf["scale"]) + np.asarray(p1_tf["translation"])
        data = np.load(edge_npz)
        pairs = np.asarray(data["edge_vertex_indices"], dtype=np.int64)
        valid = np.all((pairs >= 0) & (pairs < len(vertices)), axis=1)
        pairs = pairs[valid]
        v0, v1 = vertices[pairs[:, 0]], vertices[pairs[:, 1]]
        chains = base.chain_sharp_segments(pairs)
        feats, scales, lengths, meta = [], [], [], []
        for chain_index, chain in enumerate(chains):
            poly = base.ordered_polyline_from_chain(chain, v0, v1, pairs)
            if poly is None:
                continue
            length = float(np.linalg.norm(np.diff(poly, axis=0), axis=1).sum())
            if length < 1e-4:
                continue
            xyz = base.resample_polyline(poly, base.N_CURVE_PTS)
            tangent = base.tangents_from_points(xyz)
            curve_type, rms = base.classify_curve(xyz)
            if curve_type not in base.TYPE_TO_ID:
                curve_type = "BSPLINE"
            feature, scale_feature = base.curve_inputs(xyz, tangent.astype(np.float32))
            feats.append(feature)
            scales.append(scale_feature)
            lengths.append(length)
            meta.append({"curve_index": chain_index, "type": curve_type, "poly_len": length,
                         "rms_fit": rms, "n_segs": len(chain)})
        order = np.argsort([-x for x in lengths])[:base.MAX_CURVE_TOKENS] if lengths else []
        empty = len(order) == 0
        if empty:
            tokens = np.zeros((1, base.CURVE_TOKEN_DIM), dtype=np.float32)
            kept = []
        else:
            kept = [meta[int(i)] for i in order]
            feature_batch = np.stack([feats[int(i)] for i in order])
            scale_batch = np.stack([scales[int(i)] for i in order])
            with torch.no_grad():
                encoded = encoder(torch.from_numpy(feature_batch).to(device),
                                  torch.from_numpy(scale_batch).to(device))
            tokens = encoded["token"].float().cpu().numpy().astype(np.float32)
        np.save(dst / "curve_tokens.npy", tokens)
        summary = {
            "part_id": part_id, "source": "Dora-SES threshold_15 salient edges",
            "mesh_path": str(mesh_path), "edge_path": str(edge_npz),
            "n_sharp_segments": int(len(pairs)), "n_chains": int(len(chains)),
            "n_curve_tokens_written": int(len(tokens)),
            "empty_sharp_fallback": "zero_token" if empty else None,
            "c2_checkpoint": str(base.C2_CKPT), "gt_brep_used": False,
        }
        (dst / "curves_meta.json").write_text(json.dumps({**summary, "curves": kept}, indent=2) + "\n")
        (dst / "prepare_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        rows.append(summary)
        print(part_id, len(pairs), len(tokens), flush=True)
    (OUT / "manifest" / "dora_c2_manifest.json").write_text(
        json.dumps({"n": len(rows), "interface": "P1 C2 curve tokens (K,256)",
                    "threshold": 15, "parts": rows}, indent=2) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
