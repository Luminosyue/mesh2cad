#!/usr/bin/env python3
"""Held-out test decode + report for B0 / B1-native / B1-budget / M2.

Reports (test=280): exact, op F1, STEP valid, under-generation, Chamfer,
length strata, curve-token-count strata, and per-sample pairwise wins.

Causal correct vs shuffle/zero on M2 is a separate follow-up once M2>B0 and
M2>B1-budget on the main table.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
for p in (
    str(REPO_ROOT / "SpatialLM"),
    str(REPO_ROOT / "scripts"),
    str(REPO_ROOT / "scripts" / "deepcad"),
    str(REPO_ROOT / "scripts" / "geometry_pack_v1"),
    str(REPO_ROOT / "scripts" / "separate_edge_tokens_v1"),
):
    if p not in sys.path:
        sys.path.insert(0, p)

from decode_joint_j0_j2 import (  # noqa: E402
    _evaluate_one,
    _load_sepedge,
    _load_surface_only,
    _summarize,
)
from separate_edge_tokens_v1.common import (  # noqa: E402
    load_model,
    make_plugin,
    set_deterministic_serialization,
)

from spatiallm_curve_token_v1.config import (  # noqa: E402
    HELDOUT_BEST_V2,
    JOINT_DATASET_DIR,
    OUTPUT_ROOT,
    SURFACE_IDX_CACHE,
    TOKEN_ROOT,
)
from spatiallm_curve_token_v1.decode_curve100 import (  # noqa: E402
    MEDIA_DEFAULT,
    _load_m2_checkpoint,
    generate_dsl,
)

ARM_CKPT = {
    "B0": REPO_ROOT / "SpatialLM" / "saves" / "heldout_curve_b0_s0",
    "B1n": REPO_ROOT / "SpatialLM" / "saves" / "heldout_curve_b1_native_s0",
    "B1b": REPO_ROOT / "SpatialLM" / "saves" / "heldout_curve_b1_budget_s0",
    "M2": REPO_ROOT / "SpatialLM" / "saves" / "heldout_curve_m2_s0",
}
V2_ARM_DIR = {
    "B0": HELDOUT_BEST_V2 / "b0",
    "B1n": HELDOUT_BEST_V2 / "b1_native",
    "B1b": HELDOUT_BEST_V2 / "b1_budget_match",
    "M2": HELDOUT_BEST_V2 / "m2",
}


def _require_best_val(ckpt: Path) -> dict:
    sel_path = ckpt / "selection.json"
    if ckpt.name != "best_model" or not sel_path.is_file():
        raise SystemExit(
            f"best_v2 decode requires <run>/best_model/ with selection.json, got {ckpt}. "
            "Do not decode last-ckpt or pick a checkpoint by test metrics."
        )
    sel = json.loads(sel_path.read_text(encoding="utf-8"))
    if sel.get("test_used_for_selection"):
        raise SystemExit(f"selection.json marks test leakage: {sel_path}")
    if sel.get("selection_metric") != "eval_loss":
        raise SystemExit(f"selection_metric must be eval_loss, got {sel}")
    return sel


def _configure_env(arm: str, protocol: str) -> None:
    os.environ["CAD_SURFACE_POINTS"] = os.environ.get("CAD_SURFACE_POINTS", "4096")
    os.environ.pop("CAD_USE_EDGE_SCORE", None)
    os.environ.pop("CAD_EDGE_BUDGET_MATCH", None)
    os.environ.pop("CAD_SECOND_STREAM", None)
    if protocol == "best_v2":
        os.environ["CAD_HELDOUT_PROTOCOL"] = "best_v2"
        os.environ.setdefault("CAD_SURFACE_CACHE", str(SURFACE_IDX_CACHE))
    else:
        os.environ.pop("CAD_HELDOUT_PROTOCOL", None)
    if arm == "B0":
        os.environ.pop("CAD_USE_SEPARATE_EDGE_TOKENS", None)
        os.environ.pop("CAD_EDGE_SOURCE", None)
    elif arm == "B1n":
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
        os.environ["CAD_EDGE_SOURCE"] = "gt_sharp"
        os.environ["CAD_SECOND_STREAM"] = "edge_points"
    elif arm == "B1b":
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
        os.environ["CAD_EDGE_SOURCE"] = "gt_sharp"
        os.environ["CAD_SECOND_STREAM"] = "edge_points"
        os.environ["CAD_EDGE_BUDGET_MATCH"] = "1"
    elif arm == "M2":
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
        os.environ["CAD_SECOND_STREAM"] = "curve_tokens"
    else:
        raise ValueError(arm)


def _curve_K(rec: dict) -> int:
    ds = rec["dataset"]
    sid = rec["sample_id"]
    p = TOKEN_ROOT / ds / sid / "curve_tokens.npy"
    if not p.is_file():
        return 0
    return int(np.load(p).shape[0])


def _gt_len_bucket(n: int) -> str:
    if n <= 500:
        return "gt<=500"
    if n <= 1500:
        return "gt<=1500"
    if n <= 2048:
        return "gt<=2048"
    if n <= 4096:
        return "gt<=4096"
    return "gt>4096"


def _K_bucket(k: int) -> str:
    if k <= 8:
        return "K<=8"
    if k <= 24:
        return "K<=24"
    if k <= 64:
        return "K<=64"
    return "K<=128"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arm", choices=tuple(ARM_CKPT), required=True)
    ap.add_argument(
        "--protocol",
        choices=("legacy", "best_v2"),
        default="legacy",
        help="legacy=old last-ckpt diagnostic; best_v2=formal Gate best-val only",
    )
    ap.add_argument("--checkpoint", type=Path, default=None)
    ap.add_argument(
        "--allow-last-checkpoint",
        action="store_true",
        help="legacy diagnostic only; forbidden for best_v2 paper decode",
    )
    ap.add_argument(
        "--split-json",
        type=Path,
        default=JOINT_DATASET_DIR / "joint_j0j2_v1_test.json",
    )
    ap.add_argument("--media-dir", type=Path, default=MEDIA_DEFAULT)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dtype", default="bfloat16", choices=("bfloat16", "float32"))
    ap.add_argument("--max-new-tokens", type=int, default=4096)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    _configure_env(args.arm, args.protocol)
    from spatiallm_curve_token_v1 import heldout_geometry

    if args.arm == "M2":
        from spatiallm_curve_token_v1 import curve_token_injector

        curve_token_injector.install()
    heldout_geometry.install()

    if args.protocol == "best_v2":
        ckpt = args.checkpoint or (V2_ARM_DIR[args.arm] / "best_model")
        if not args.allow_last_checkpoint:
            _require_best_val(ckpt)
        out = args.out or (HELDOUT_BEST_V2 / "decode" / args.arm.lower())
    else:
        ckpt = args.checkpoint or ARM_CKPT[args.arm]
        out = args.out or (OUTPUT_ROOT / "heldout_decode" / f"{args.arm.lower()}_s0")
    out.mkdir(parents=True, exist_ok=True)

    records = json.loads(args.split_json.read_text(encoding="utf-8"))
    records = records[args.offset :]
    if args.limit is not None:
        records = records[: args.limit]

    separate_edge = args.arm != "B0"
    plugin = make_plugin(separate_edge=separate_edge)
    dtype = getattr(torch, args.dtype)
    if args.arm == "M2":
        model, tokenizer = _load_m2_checkpoint(ckpt, "cuda", dtype)
    else:
        model, tokenizer = load_model(
            ckpt,
            separate_edge=separate_edge,
            device="cuda",
            dtype=dtype,
            freeze_sonata=True,
        )
    set_deterministic_serialization(model.point_backbone)
    model.eval()

    rows: list[dict] = []
    for i, rec in enumerate(records):
        sid = rec["id"]
        sample_out = out / sid
        row_path = sample_out / "row.json"
        if args.resume and row_path.exists():
            rows.append(json.loads(row_path.read_text(encoding="utf-8")))
            continue
        npy = args.media_dir / rec["point_clouds"][0]
        if separate_edge:
            surface, edge = _load_sepedge(plugin, npy)
        else:
            surface = _load_surface_only(plugin, npy)
            edge = None
        pred, gen_meta = generate_dsl(
            model,
            tokenizer,
            surface,
            edge,
            separate_edge=separate_edge,
            max_new_tokens=args.max_new_tokens,
        )
        row = _evaluate_one(rec, pred, gen_meta, sample_out, args.media_dir)
        gt_text = rec["conversations"][1]["value"]
        gt_tok = int(len(tokenizer(gt_text, add_special_tokens=False)["input_ids"]))
        k = _curve_K(rec)
        row["over_generation"] = (
            row["predicted_op_count"] > row["gt_op_count"]
            if row.get("gt_op_count", 0) > 0
            else False
        )
        row.update(
            {
                "arm": args.arm,
                "protocol": args.protocol,
                "gt_cad_tokens": gt_tok,
                "curve_token_K": k,
                "surface_voxels": int(surface.shape[1]),
                "second_stream_tokens": 0 if edge is None else int(edge.shape[1]),
                "gt_len_bucket": _gt_len_bucket(gt_tok),
                "K_bucket": _K_bucket(k),
            }
        )
        row_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        rows.append(row)
        print(
            f"[{args.arm}] {sid}: exact={row['exact_match']} op_f1={row['op_f1']:.2f} "
            f"step={row.get('step_ok')} stop={row.get('stop_reason')} "
            f"gt={gt_tok} K={k}",
            flush=True,
        )
        if (i + 1) % 10 == 0 or (i + 1) == len(records):
            report = _summarize(
                rows,
                {
                    "arm": args.arm,
                    "checkpoint": str(ckpt),
                    "max_new_tokens": args.max_new_tokens,
                },
            )
            (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")

    report = _summarize(
        rows,
        {
            "arm": args.arm,
            "protocol": args.protocol,
            "checkpoint": str(ckpt),
            "max_new_tokens": args.max_new_tokens,
            "do_sample": False,
            "num_beams": 1,
            "split": str(args.split_json),
            "test_used_for_selection": False,
        },
    )
    report["over_generation_rate"] = (
        sum(1 for r in rows if r.get("over_generation")) / max(len(rows), 1)
    )
    chamfers = [
        r["geometry"]["chamfer_norm"]
        for r in rows
        if "chamfer_norm" in r.get("geometry", {})
    ]
    if chamfers:
        report["median_chamfer_norm"] = float(np.median(chamfers))
        report["p90_chamfer_norm"] = float(np.percentile(chamfers, 90))
    report["mean_surface_voxels"] = float(np.mean([r.get("surface_voxels", 0) for r in rows]))
    report["mean_second_stream_tokens"] = float(
        np.mean([r.get("second_stream_tokens", 0) for r in rows])
    )
    report["mean_pred_tokens"] = float(
        np.mean([r.get("prediction_tokens", 0) for r in rows])
    )
    # strata
    for key in ("gt_len_bucket", "K_bucket"):
        buckets = sorted({r.get(key) for r in rows if r.get(key)})
        report[f"by_{key}"] = {
            b: {
                "n": sum(1 for r in rows if r.get(key) == b),
                "exact": float(
                    np.mean([r["exact_match"] for r in rows if r.get(key) == b])
                ),
                "op_f1": float(np.mean([r["op_f1"] for r in rows if r.get(key) == b])),
                "step": float(
                    np.mean([bool(r.get("step_ok")) for r in rows if r.get(key) == b])
                ),
            }
            for b in buckets
        }
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
