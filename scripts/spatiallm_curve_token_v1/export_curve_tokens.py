#!/usr/bin/env python3
"""Precompute frozen Curve Tokens per CAD.

The Curve Encoder is frozen by construction: tokens are computed offline here with
the C2 backbone from a `curve_token_head_v1` checkpoint and stored as
`[K, 256]` float32. Nothing in the LLM training loop can update it.

Curves are restricted to B-Rep *sharp* edges so the payload carries the same
geometry as B1's `edge_points_gt_sharp.npy`, keeping the comparison controlled.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_encoder_baseline_v1.dataset import _normalized_s  # noqa: E402
from curve_encoder_scale_curvature_v1.dataset import curve_local_frame  # noqa: E402
from curve_token_head_v1.config import EXPERIMENTS, TYPE_TO_ID  # noqa: E402
from curve_token_head_v1.models import build_model  # noqa: E402
from spatiallm_curve_token_v1.config import (  # noqa: E402
    CURVE_DATA_ROOT,
    CURVE_TOKEN_DIM,
    DEFAULT_CKPT,
    MAX_CURVE_TOKENS,
    PACK_ROOT,
    SCHEMA_VERSION,
    TOKEN_ROOT,
)

OCC_ID_TO_TYPE = {0: "LINE", 1: "CIRCLE", 2: "ELLIPSE", 3: "BSPLINE"}


def load_backbone(ckpt_path: Path, device: torch.device):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    model = build_model(EXPERIMENTS[ckpt["exp"]])
    model.load_state_dict(ckpt["model"])
    model.eval().to(device)
    for p in model.parameters():
        p.requires_grad_(False)
    return model, ckpt


def curve_inputs(xyz: np.ndarray, tangent: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """The frozen C2 input recipe: curve-local xyz + tangent + s, and log length."""
    local, _, _ = curve_local_frame(xyz)
    s = _normalized_s(xyz.astype(np.float32), "uniform_abscissa")
    feats = np.concatenate([local, tangent, s], axis=-1).astype(np.float32)
    poly = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
    return feats, np.array([np.log(poly + 1e-6)], dtype=np.float32)


def process_cad(
    dataset: str, sample_id: str, cad_dir: Path, model, device, sharp_only: bool
) -> dict | None:
    z = np.load(cad_dir / "curve_samples.npz")
    n = int(z["num_curves"][0])
    if n == 0:
        return None

    is_sharp = {}
    if sharp_only:
        brep_path = PACK_ROOT[dataset] / sample_id / "brep_edges.json"
        if not brep_path.is_file():
            return None
        brep = json.loads(brep_path.read_text(encoding="utf-8"))
        is_sharp = {int(e["edge_index"]): bool(e.get("is_sharp", False))
                    for e in brep["edges"]}

    feats, scales, kept = [], [], []
    for i in range(n):
        ctype = OCC_ID_TO_TYPE.get(int(z["curve_type_id"][i]))
        if ctype not in TYPE_TO_ID:
            continue
        edge_id = int(z["curve_edge_id"][i])
        if sharp_only and not is_sharp.get(edge_id, False):
            continue
        xyz = np.asarray(z["curve_xyz_normalized"][i], dtype=np.float64)
        tan = np.asarray(z["curve_tangent"][i], dtype=np.float32)
        f, sc = curve_inputs(xyz, tan)
        feats.append(f)
        scales.append(sc)
        kept.append(
            {
                "edge_id": edge_id,
                "type": ctype,
                "poly_len": float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()),
            }
        )
    if not feats:
        return None

    # rank by length so truncation drops the least significant curves
    order = np.argsort([-k["poly_len"] for k in kept])
    n_total = len(order)
    order = order[:MAX_CURVE_TOKENS]
    feats = np.stack([feats[i] for i in order], 0)
    scales = np.stack([scales[i] for i in order], 0)
    kept = [kept[i] for i in order]

    with torch.no_grad():
        out = model(
            torch.from_numpy(feats).to(device), torch.from_numpy(scales).to(device)
        )
        tokens = out["token"].float().cpu().numpy().astype(np.float32)
        pred_type = out["type_logits"].argmax(-1).cpu().numpy()
    assert tokens.shape == (len(kept), CURVE_TOKEN_DIM), tokens.shape

    return {
        "tokens": tokens,
        "meta": {
            "dataset": dataset,
            "sample_id": sample_id,
            "n_curves_total": n_total,
            "n_curves_kept": len(kept),
            "truncated": bool(n_total > len(kept)),
            "type_counts": {
                t: sum(1 for k in kept if k["type"] == t) for t in TYPE_TO_ID
            },
            "predicted_type_counts": {
                t: int((pred_type == i).sum()) for t, i in TYPE_TO_ID.items()
            },
            "curves": kept,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ckpt", type=Path, default=DEFAULT_CKPT)
    ap.add_argument("--ids", type=Path, default=None,
                    help="JSON list of {dataset, sample_id, cad_dir}; default = all CADs")
    ap.add_argument("--sharp-only", action="store_true", default=True)
    ap.add_argument("--all-curves", dest="sharp_only", action="store_false")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    device = torch.device(args.device)
    model, ckpt = load_backbone(args.ckpt, device)
    print(f"[export] backbone {args.ckpt} (exp={ckpt['exp']}, epoch={ckpt['epoch']})",
          flush=True)

    if args.ids:
        rows = json.loads(args.ids.read_text(encoding="utf-8"))
    else:
        rows = []
        for split_dir, dataset in (("deepcad_train", "deepcad"),
                                   ("fusion360_train", "fusion360")):
            for d in sorted((CURVE_DATA_ROOT / split_dir).iterdir()):
                if d.is_dir():
                    rows.append({"dataset": dataset, "sample_id": d.name,
                                 "cad_dir": f"{split_dir}/{d.name}"})

    stats = {"n": 0, "skipped": 0, "truncated": 0, "n_tokens": []}
    for i, r in enumerate(rows, 1):
        res = process_cad(
            r["dataset"], r["sample_id"], CURVE_DATA_ROOT / r["cad_dir"],
            model, device, args.sharp_only,
        )
        if res is None:
            stats["skipped"] += 1
            continue
        out_dir = TOKEN_ROOT / r["dataset"] / r["sample_id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        np.save(out_dir / "curve_tokens.npy", res["tokens"])
        (out_dir / "curve_tokens_meta.json").write_text(
            json.dumps(res["meta"], indent=2) + "\n", encoding="utf-8"
        )
        stats["n"] += 1
        stats["truncated"] += int(res["meta"]["truncated"])
        stats["n_tokens"].append(res["meta"]["n_curves_kept"])
        if i % 200 == 0 or i == len(rows):
            print(f"[export] {i}/{len(rows)} written={stats['n']}", flush=True)

    nt = np.asarray(stats["n_tokens"])
    summary = {
        "schema_version": SCHEMA_VERSION,
        "checkpoint": str(args.ckpt.relative_to(ROOT)),
        "backbone_exp": ckpt["exp"],
        "sharp_only": bool(args.sharp_only),
        "max_curve_tokens": MAX_CURVE_TOKENS,
        "token_dim": CURVE_TOKEN_DIM,
        "n_cad_written": stats["n"],
        "n_cad_skipped": stats["skipped"],
        "n_cad_truncated": stats["truncated"],
        "tokens_per_cad": {
            "min": int(nt.min()), "median": float(np.median(nt)),
            "p90": float(np.percentile(nt, 90)), "max": int(nt.max()),
        },
    }
    TOKEN_ROOT.mkdir(parents=True, exist_ok=True)
    (TOKEN_ROOT / "export_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
