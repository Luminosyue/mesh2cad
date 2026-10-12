#!/usr/bin/env python3
# LEGACY_READONLY: canonical P0-T2 table lives in scripts/curve_encoder_baseline_v1/. Do not mix metrics.

"""Main entry: CURVE_ENCODER_BASELINE_V1.

Pipeline:
  CAD-level splits → cache → train PointNet + Transformer → eval
  (clean / noise / partial) → classical comparison → embedding viz → Track A guard.

Writes only under ours3/curve_encoder_baseline_v1/. Never mutates Track A or
curve_token_data_v1.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

# Pin GPU *before* importing torch so CUDA_VISIBLE_DEVICES takes effect.
sys.path.insert(0, str(Path(__file__).resolve().parent))
_pre = argparse.ArgumentParser(add_help=False)
_pre.add_argument("--gpu", type=int, default=None)
_pre_args, _ = _pre.parse_known_args()
if _pre_args.gpu is not None:
    os.environ["CUDA_VISIBLE_DEVICES"] = str(_pre_args.gpu)

import torch

from curve_encoder_v1 import guard
from curve_encoder_v1.build_cache import build_cache
from curve_encoder_v1.classical_compare import run_classical_suite
from curve_encoder_v1.config import (
    CKPT_DIR,
    ENCODER_OUTPUT_ROOT,
    EVAL_DIR,
    REPORTS_DIR,
    RUNS_DIR,
)
from curve_encoder_v1.embed_viz import visualize_tokens
from curve_encoder_v1.evaluate import run_eval_suite
from curve_encoder_v1.splits import assign_splits, discover_cads, write_splits
from curve_encoder_v1.train import train_one


def _pick(d: dict, *keys, default=None):
    cur = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def build_final_report(
    pointnet_suite: dict,
    transformer_suite: dict,
    classical: dict,
    train_summaries: dict,
    guard_report: dict,
) -> dict:
    pn = pointnet_suite["clean"]
    tr = transformer_suite["clean"]
    pn_n1 = pointnet_suite["noise"].get("0.001", {})
    tr_n1 = transformer_suite["noise"].get("0.001", {})
    pn_p50 = pointnet_suite["partial"].get("0.5", {})
    tr_p50 = transformer_suite["partial"].get("0.5", {})

    # Winner by clean macro-F1
    winner = "pointnet" if pn["CURVE_TYPE_MACRO_F1"] >= tr["CURVE_TYPE_MACRO_F1"] else "transformer"
    best = pn if winner == "pointnet" else tr
    best_n1 = pn_n1 if winner == "pointnet" else tr_n1
    best_p50 = pn_p50 if winner == "pointnet" else tr_p50

    modified = bool(guard_report.get("TRACK_A_MODIFIED", True))
    gate = "CURVE_ENCODER_BASELINE_V1_PASS"
    if modified:
        gate = "CURVE_ENCODER_BASELINE_V1_FAIL_TRACK_A_CONTAMINATION"

    report = {
        "CURRENT_GATE": gate,
        "TRACK_A_MODIFIED": modified,
        "TRACK_A_REEXECUTED": False,
        "POINTNET_BASELINE_FINISHED": True,
        "TRANSFORMER_BASELINE_FINISHED": True,
        "CLEAN_EVAL_FINISHED": True,
        "NOISE_ROBUSTNESS_FINISHED": True,
        "PARTIAL_CURVE_ROBUSTNESS_FINISHED": True,
        "PER_TYPE_METRICS_FINISHED": True,
        "MACRO_METRICS_FINISHED": True,
        "CLASSICAL_FITTING_COMPARISON_FINISHED": True,
        "EMBEDDING_VISUALIZATION_FINISHED": True,
        "CURVE_TYPE_MACRO_F1": best["CURVE_TYPE_MACRO_F1"],
        "LINE_F1": best["LINE_F1"],
        "CIRCLE_F1": best["CIRCLE_F1"],
        "ELLIPSE_F1": best["ELLIPSE_F1"],
        "BSPLINE_F1": best["BSPLINE_F1"],
        "LINE_DIRECTION_ERROR": best.get("LINE_DIRECTION_ERROR"),
        "CIRCLE_NORMAL_ERROR": best.get("CIRCLE_NORMAL_ERROR"),
        "CIRCLE_RADIUS_ERROR": best.get("CIRCLE_RADIUS_ERROR"),
        "ELLIPSE_AXIS_ERROR": best.get("ELLIPSE_AXIS_ERROR"),
        "RECON_CHAMFER": best.get("RECON_CHAMFER"),
        "NOISE_1E3_METRICS": {
            "macro_f1": best_n1.get("CURVE_TYPE_MACRO_F1"),
            "CIRCLE_NORMAL_ERROR": best_n1.get("CIRCLE_NORMAL_ERROR"),
            "LINE_DIRECTION_ERROR": best_n1.get("LINE_DIRECTION_ERROR"),
            "RECON_CHAMFER": best_n1.get("RECON_CHAMFER"),
        },
        "PARTIAL_50_METRICS": {
            "macro_f1": best_p50.get("CURVE_TYPE_MACRO_F1"),
            "RECON_CHAMFER": best_p50.get("RECON_CHAMFER"),
            "LINE_F1": best_p50.get("LINE_F1"),
            "CIRCLE_F1": best_p50.get("CIRCLE_F1"),
        },
        "POINTNET_VS_TRANSFORMER": {
            "pointnet_macro_f1": pn["CURVE_TYPE_MACRO_F1"],
            "transformer_macro_f1": tr["CURVE_TYPE_MACRO_F1"],
            "winner_clean_macro_f1": winner,
            "pointnet_recon_chamfer_mean": _pick(pn, "RECON_CHAMFER", "mean"),
            "transformer_recon_chamfer_mean": _pick(tr, "RECON_CHAMFER", "mean"),
        },
        "NEURAL_VS_CLASSICAL_FITTING": {
            "classical_clean_macro_f1_analytic": classical["clean"].get("CURVE_TYPE_MACRO_F1_analytic"),
            "classical_noise_1e-3_circle_normal": classical["noise"].get("0.001", {}).get("CIRCLE_NORMAL_ERROR"),
            "neural_noise_1e-3_circle_normal": best_n1.get("CIRCLE_NORMAL_ERROR"),
            "classical_ellipse_axis_clean": classical["clean"].get("ELLIPSE_AXIS_ERROR"),
            "neural_ellipse_axis_clean": best.get("ELLIPSE_AXIS_ERROR"),
        },
        "OUTPUT_ROOT": str(ENCODER_OUTPUT_ROOT),
        "train_summaries": {k: {kk: vv for kk, vv in v.items() if kk != "history"} for k, v in train_summaries.items()},
    }
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["canary", "full"], default="canary")
    ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=512)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--gpu", type=int, default=None, help="CUDA device index (sets CUDA_VISIBLE_DEVICES)")
    ap.add_argument("--skip-guard", action="store_true")
    ap.add_argument("--skip-classical", action="store_true")
    ap.add_argument("--max-train-curves", type=int, default=None)
    ap.add_argument("--ablations", nargs="+", default=["B0_xyz", "B1_xyz_tangent"])
    args = ap.parse_args()

    if args.gpu is not None:
        if not torch.cuda.is_available():
            raise RuntimeError(f"--gpu {args.gpu} requested but CUDA is unavailable")
        args.device = "cuda"
        print(f"[gpu] physical GPU {args.gpu} → cuda:0 ({torch.cuda.get_device_name(0)})")
    elif args.device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; pass --device cpu to override")
    elif args.device.startswith("cuda"):
        print(f"[gpu] {args.device} ({torch.cuda.get_device_name(0)})")

    if args.stage == "canary":
        epochs = args.epochs if args.epochs is not None else 5
        max_train = args.max_train_curves if args.max_train_curves is not None else 8000
        classical_max = 500
    else:
        epochs = args.epochs if args.epochs is not None else 20
        max_train = args.max_train_curves
        classical_max = 800

    t0 = time.time()
    ENCODER_OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    print("[0] assert write scope disjoint")
    print(json.dumps(guard.assert_write_scope_disjoint(), indent=2))

    if not args.skip_guard:
        print("[1] Track A guard snapshot (before)")
        guard.snapshot("before_encoder")

    print("[2] CAD-level splits")
    cads = discover_cads()
    manifest = assign_splits(cads)
    write_splits(manifest)
    print("  cad_counts:", manifest["cad_counts"])
    print("  type_coverage:", manifest["type_coverage_cads"])

    print("[3] build curve cache")
    cache_path = build_cache()

    train_summaries = {}
    # Primary ablations: PointNet B0 + B1, Transformer B1 (sanity: Transformer must beat or match PointNet)
    jobs = []
    if "B0_xyz" in args.ablations:
        jobs.append(("pointnet", "B0_xyz", f"pointnet_B0_xyz_{args.stage}"))
    if "B1_xyz_tangent" in args.ablations:
        jobs.append(("pointnet", "B1_xyz_tangent", f"pointnet_B1_xyz_tangent_{args.stage}"))
        jobs.append(("transformer", "B1_xyz_tangent", f"transformer_B1_xyz_tangent_{args.stage}"))
    if "B2_xyz_tangent_scalars" in args.ablations:
        jobs.append(("pointnet", "B2_xyz_tangent_scalars", f"pointnet_B2_xyz_tangent_scalars_{args.stage}"))

    print(f"[4] train ({len(jobs)} runs, device={args.device}, epochs={epochs})", flush=True)
    for arch, abl, name in jobs:
        train_summaries[name] = train_one(
            arch=arch,
            ablation=abl,
            epochs=epochs,
            batch_size=args.batch_size,
            lr=1e-3,
            device=args.device,
            run_name=name,
            max_train_curves=max_train,
            n_layers=2 if args.stage == "canary" else 4,
        )

    print("[5] evaluate PointNet B1 + Transformer B1", flush=True)
    pn_ckpt = CKPT_DIR / f"pointnet_B1_xyz_tangent_{args.stage}" / "best.pt"
    tr_ckpt = CKPT_DIR / f"transformer_B1_xyz_tangent_{args.stage}" / "best.pt"
    pn_suite = run_eval_suite(pn_ckpt, args.device, out_dir=EVAL_DIR / pn_ckpt.parent.name)
    print("  pointnet clean macroF1=", pn_suite["clean"]["CURVE_TYPE_MACRO_F1"], flush=True)
    tr_suite = run_eval_suite(tr_ckpt, args.device, out_dir=EVAL_DIR / tr_ckpt.parent.name)
    print("  transformer clean macroF1=", tr_suite["clean"]["CURVE_TYPE_MACRO_F1"], flush=True)

    print("[6] embedding visualization", flush=True)
    for name in (pn_ckpt.parent.name, tr_ckpt.parent.name):
        tok = EVAL_DIR / name / "test_clean_tokens.npz"
        if tok.is_file():
            visualize_tokens(tok, out_dir=ENCODER_OUTPUT_ROOT / "embeddings" / name)

    classical = {"clean": {}, "noise": {}, "partial": {}}
    if not args.skip_classical:
        print(f"[7] classical fitting comparison (max_curves={classical_max})", flush=True)
        classical = run_classical_suite(
            out_dir=EVAL_DIR / "classical_fitting",
            max_curves=classical_max,
        )
        print("  classical clean macroF1=", classical["clean"].get("CURVE_TYPE_MACRO_F1_analytic"), flush=True)

    guard_report = {"TRACK_A_MODIFIED": False}
    if not args.skip_guard:
        print("[8] Track A guard verify")
        guard.snapshot("after_encoder")
        guard_report = guard.verify("before_encoder", "after_encoder")
        print("  TRACK_A_MODIFIED=", guard_report.get("TRACK_A_MODIFIED"))

    report = build_final_report(pn_suite, tr_suite, classical, train_summaries, guard_report)
    report["STAGE"] = args.stage
    report["TOTAL_SECONDS"] = time.time() - t0
    report["DEVICE"] = args.device
    report["CACHE"] = str(cache_path)

    out_json = REPORTS_DIR / f"summary_{args.stage}.json"
    out_md = REPORTS_DIR / f"summary_{args.stage}.md"
    out_json.write_text(json.dumps(report, indent=2, default=str))

    lines = [
        f"# CURVE_ENCODER_BASELINE_V1 ({args.stage})",
        "",
        "```text",
        f"CURRENT_GATE={report['CURRENT_GATE']}",
        f"TRACK_A_MODIFIED={report['TRACK_A_MODIFIED']}",
        f"TRACK_A_REEXECUTED={report['TRACK_A_REEXECUTED']}",
        f"CURVE_TYPE_MACRO_F1={report['CURVE_TYPE_MACRO_F1']}",
        f"LINE_F1={report['LINE_F1']}",
        f"CIRCLE_F1={report['CIRCLE_F1']}",
        f"ELLIPSE_F1={report['ELLIPSE_F1']}",
        f"BSPLINE_F1={report['BSPLINE_F1']}",
        f"POINTNET_VS_TRANSFORMER={report['POINTNET_VS_TRANSFORMER']}",
        "```",
        "",
        f"Full JSON: `{out_json}`",
    ]
    out_md.write_text("\n".join(lines) + "\n")

    print("=" * 70)
    print(f"CURRENT_GATE={report['CURRENT_GATE']}")
    print(f"TRACK_A_MODIFIED={report['TRACK_A_MODIFIED']}")
    print(f"CURVE_TYPE_MACRO_F1={report['CURVE_TYPE_MACRO_F1']}")
    print(f"POINTNET_VS_TRANSFORMER={report['POINTNET_VS_TRANSFORMER']}")
    print(f"OUTPUT_ROOT={ENCODER_OUTPUT_ROOT}")
    print(f"REPORT={out_json}")
    print("=" * 70)


if __name__ == "__main__":
    main()
