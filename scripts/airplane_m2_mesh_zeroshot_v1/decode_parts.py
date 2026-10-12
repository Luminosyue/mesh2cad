#!/usr/bin/env python3
"""Decode B0 / M2 on prepared airplane X-Part packs (mesh-derived curves)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [
    str(REPO / "SpatialLM"),
    str(REPO / "scripts"),
    str(REPO / "scripts" / "deepcad"),
    str(REPO / "scripts" / "geometry_pack_v1"),
    str(REPO / "scripts" / "separate_edge_tokens_v1"),
]

from separate_edge_tokens_v1.common import (  # noqa: E402
    load_model,
    make_plugin,
    set_deterministic_serialization,
)
from spatiallm_curve_token_v1.decode_curve100 import (  # noqa: E402
    _load_m2_checkpoint,
    generate_dsl,
)

OUT_ROOT = REPO / "ours3" / "airplane_m2_mesh_zeroshot_v1"
CKPT = {
    "B0": REPO / "SpatialLM" / "saves" / "heldout_curve_b0_s0",
    "M2": REPO / "SpatialLM" / "saves" / "heldout_curve_m2_s0",
}


def _exec_dsl(pred: str, sample_out: Path) -> dict:
    from decode_joint_j0_j2 import _exec_step
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code

    try:
        code = extract_dsl_code(pred)
    except Exception:
        code = pred
    (sample_out / "pred.dsl").write_text(pred if pred.endswith("\n") else pred + "\n")
    (sample_out / "pred_canonical.dsl").write_text(
        code if code.endswith("\n") else code + "\n"
    )
    return _exec_step(code, sample_out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("B0", "M2"), required=True)
    ap.add_argument("--parts", nargs="+", default=None)
    ap.add_argument("--max-new-tokens", type=int, default=4096)
    ap.add_argument("--dtype", default="bfloat16")
    args = ap.parse_args()

    parts_root = OUT_ROOT / "parts"
    if args.parts:
        parts = args.parts
    else:
        parts = sorted(p.name for p in parts_root.iterdir() if p.is_dir())

    os.environ["CAD_SURFACE_POINTS"] = "4096"
    os.environ.pop("CAD_USE_EDGE_SCORE", None)
    if args.arm == "B0":
        os.environ.pop("CAD_USE_SEPARATE_EDGE_TOKENS", None)
        os.environ.pop("CAD_SECOND_STREAM", None)
        separate = False
    else:
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
        os.environ["CAD_SECOND_STREAM"] = "curve_tokens"
        separate = True
        from spatiallm_curve_token_v1 import curve_token_injector

        curve_token_injector.install()

    # Point CURVE_TOKEN_ROOT at airplane packs via symlink layout:
    # we load tokens manually into edge_clouds for M2 by patching npy beside a fake surface path.
    from spatiallm_curve_token_v1 import heldout_geometry

    heldout_geometry.install()

    dtype = getattr(torch, args.dtype)
    if args.arm == "M2":
        model, tokenizer = _load_m2_checkpoint(CKPT[args.arm], "cuda", dtype)
    else:
        model, tokenizer = load_model(
            CKPT[args.arm], separate_edge=False, device="cuda", dtype=dtype, freeze_sonata=True
        )
    set_deterministic_serialization(model.point_backbone)
    model.eval()
    plugin = make_plugin(separate_edge=separate)

    out_arm = OUT_ROOT / "decode" / args.arm.lower()
    out_arm.mkdir(parents=True, exist_ok=True)
    rows = []

    for part_id in parts:
        pdir = parts_root / part_id
        sample_out = out_arm / part_id
        sample_out.mkdir(parents=True, exist_ok=True)
        surf = np.load(pdir / "surface_points.npy").astype(np.float64)
        # voxelize via plugin helpers
        if separate:
            # write temp surface path and point CURVE_TOKEN_ROOT
            tmp_surf = sample_out / "surface_points.npy"
            np.save(tmp_surf, surf)
            # injector resolves .../DeepCAD/geometry_pack_v1/<sid>/ — bypass by
            # directly building tensors
            s_grid, s_xyz, s_normal, _ = plugin._voxelize_6ch(surf)
            surface_t = np.concatenate(
                [s_grid.astype(np.float32), s_xyz, s_normal], axis=1
            )
            tokens = np.load(pdir / "curve_tokens.npy").astype(np.float32)
            if len(tokens) == 0:
                # empty curve stream → drop to surface-only markers would mismatch
                # training; inject a single zero token so markers stay valid
                tokens = np.zeros((1, 256), dtype=np.float32)
            surface = torch.as_tensor(surface_t[None], dtype=torch.float32)
            edge = torch.as_tensor(tokens[None], dtype=torch.float32)
        else:
            s_grid, s_xyz, s_normal, _ = plugin._voxelize_6ch(surf)
            surface_t = np.concatenate(
                [s_grid.astype(np.float32), s_xyz, s_normal], axis=1
            )
            surface = torch.as_tensor(surface_t[None], dtype=torch.float32)
            edge = None

        pred, gen_meta = generate_dsl(
            model,
            tokenizer,
            surface,
            edge,
            separate_edge=separate,
            max_new_tokens=args.max_new_tokens,
        )
        exec_rec = _exec_dsl(pred, sample_out)
        row = {
            "part_id": part_id,
            "arm": args.arm,
            "parsed": exec_rec.get("parsed"),
            "step_ok": exec_rec.get("step_ok"),
            "step": exec_rec.get("step"),
            "stl": exec_rec.get("stl"),
            "n_curve_tokens": int(np.load(pdir / "curve_tokens.npy").shape[0]),
            **gen_meta,
            "pred_chars": len(pred),
        }
        # crude op count
        for name, pat in [
            ("n_extrude", "Extrude"),
            ("n_cut", "Cut"),
            ("n_union", "Union"),
            ("n_sketch", "Sketch"),
            ("n_circle", "Circle"),
            ("n_rectangle", "Rectangle"),
        ]:
            row[name] = pred.count(pat)
        (sample_out / "row.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append(row)
        print(
            f"[{args.arm}] {part_id}: step={row.get('step_ok')} parsed={row.get('parsed')} "
            f"stop={row.get('stop_reason')} K={row['n_curve_tokens']} "
            f"extrude={row['n_extrude']}",
            flush=True,
        )

    (out_arm / "report.json").write_text(json.dumps({"arm": args.arm, "samples": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
