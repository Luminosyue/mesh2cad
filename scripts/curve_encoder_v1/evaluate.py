"""Full evaluation suite for a trained Curve Encoder checkpoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from .config import EVAL_DIR, NOISE_LEVELS, PARTIAL_FRACS, TOKEN_DIM
from .dataset import CurveCacheDataset, input_dim, make_loader
from .metrics import (
    attach_type_preds_to_buckets,
    confusion_and_f1,
    geometry_metrics,
)
from .models import PointNetCurveEncoder, TransformerCurveEncoder


def load_model(ckpt_path: Path, device: str) -> tuple[torch.nn.Module, dict]:
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    arch = ckpt["arch"]
    ablation = ckpt["ablation"]
    in_dim = ckpt.get("in_dim") or input_dim(ablation)
    n_layers = ckpt.get("n_layers", 4)
    if arch == "pointnet":
        model = PointNetCurveEncoder(in_dim=in_dim, token_dim=TOKEN_DIM)
    else:
        model = TransformerCurveEncoder(in_dim=in_dim, token_dim=TOKEN_DIM, n_layers=n_layers)
    model.load_state_dict(ckpt["model"])
    model.to(device).eval()
    return model, ckpt


@torch.no_grad()
def collect_predictions(model, loader, device) -> dict[str, np.ndarray]:
    type_ids, type_preds = [], []
    xyz_gts, xyz_preds = [], []
    params_gts, params_preds = [], []
    arc_degs, closeds, tokens = [], [], []
    for batch in loader:
        batch = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
        out = model(batch["feat"], batch["point_mask"])
        type_ids.append(batch["type_id"].cpu().numpy())
        type_preds.append(out["type_logits"].argmax(-1).cpu().numpy())
        xyz_gts.append(batch["xyz_gt"].cpu().numpy())
        xyz_preds.append(out["xyz_recon"].cpu().numpy())
        params_gts.append(batch["params"].cpu().numpy())
        params_preds.append(out["params"].cpu().numpy())
        arc_degs.append(batch["arc_deg"].cpu().numpy())
        closeds.append(batch["is_closed"].cpu().numpy())
        tokens.append(out["token"].cpu().numpy())
    return {
        "type_id": np.concatenate(type_ids),
        "type_pred": np.concatenate(type_preds),
        "xyz_gt": np.concatenate(xyz_gts),
        "xyz_pred": np.concatenate(xyz_preds),
        "params_gt": np.concatenate(params_gts),
        "params_pred": np.concatenate(params_preds),
        "arc_deg": np.concatenate(arc_degs),
        "is_closed": np.concatenate(closeds),
        "token": np.concatenate(tokens),
    }


def evaluate_condition(
    model,
    ablation: str,
    split: str,
    noise_rel: float,
    partial_frac: float,
    device: str,
    batch_size: int = 512,
    seed: int = 0,
) -> dict:
    ds = CurveCacheDataset(
        split=split,
        ablation=ablation,
        noise_rel=noise_rel,
        partial_frac=partial_frac,
        seed=seed,
    )
    loader = make_loader(ds, batch_size, shuffle=False)
    pred = collect_predictions(model, loader, device)
    clf = confusion_and_f1(pred["type_id"], pred["type_pred"])
    geom = geometry_metrics(
        pred["type_id"],
        pred["xyz_gt"],
        pred["xyz_pred"],
        pred["params_gt"],
        pred["params_pred"],
        pred["arc_deg"],
        pred["is_closed"],
    )
    geom = attach_type_preds_to_buckets(
        geom, pred["type_id"], pred["type_pred"], pred["arc_deg"], pred["is_closed"]
    )
    # Enrich arc buckets with param errors for short arcs
    return {
        "n": int(pred["type_id"].shape[0]),
        "noise_rel": noise_rel,
        "partial_frac": partial_frac,
        "classification": clf,
        "geometry": geom,
        "CURVE_TYPE_MACRO_F1": clf["macro_f1"],
        "LINE_F1": clf["per_type"]["LINE"]["f1"],
        "CIRCLE_F1": clf["per_type"]["CIRCLE"]["f1"],
        "ELLIPSE_F1": clf["per_type"]["ELLIPSE"]["f1"],
        "BSPLINE_F1": clf["per_type"]["BSPLINE"]["f1"],
        "LINE_DIRECTION_ERROR": geom.get("LINE_DIRECTION_ERROR"),
        "CIRCLE_NORMAL_ERROR": geom.get("CIRCLE_NORMAL_ERROR"),
        "CIRCLE_RADIUS_ERROR": geom.get("CIRCLE_RADIUS_ERROR"),
        "ELLIPSE_AXIS_ERROR": geom.get("ELLIPSE_AXIS_ERROR"),
        "RECON_CHAMFER": geom.get("RECON_CHAMFER"),
        "_pred": pred,  # caller may drop
    }


def run_eval_suite(
    ckpt_path: Path,
    device: str,
    out_dir: Path | None = None,
    split: str = "test",
    noise_levels: tuple[float, ...] = NOISE_LEVELS,
    partial_fracs: tuple[float, ...] = PARTIAL_FRACS,
) -> dict:
    model, ckpt = load_model(ckpt_path, device)
    ablation = ckpt["ablation"]
    arch = ckpt["arch"]
    run_name = ckpt_path.parent.name
    out_dir = out_dir or (EVAL_DIR / run_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    suite = {
        "ckpt": str(ckpt_path),
        "arch": arch,
        "ablation": ablation,
        "split": split,
        "clean": None,
        "noise": {},
        "partial": {},
    }

    # Clean
    clean = evaluate_condition(model, ablation, split, 0.0, 1.0, device)
    pred_clean = clean.pop("_pred")
    suite["clean"] = clean
    np.savez_compressed(out_dir / "test_clean_preds.npz", **{k: pred_clean[k] for k in pred_clean if k != "token"})
    np.savez_compressed(out_dir / "test_clean_tokens.npz", token=pred_clean["token"], type_id=pred_clean["type_id"])

    # Noise sweep (full observation)
    for noise in noise_levels:
        key = f"{noise:g}"
        r = evaluate_condition(model, ablation, split, noise, 1.0, device, seed=100)
        r.pop("_pred", None)
        suite["noise"][key] = r

    # Partial sweep (clean points)
    for frac in partial_fracs:
        key = f"{frac:g}"
        r = evaluate_condition(model, ablation, split, 0.0, frac, device, seed=200)
        r.pop("_pred", None)
        suite["partial"][key] = r

    (out_dir / "eval_suite.json").write_text(json.dumps(suite, indent=2))
    _write_md(suite, out_dir / "eval_suite.md")
    return suite


def _fmt_err(d) -> str:
    if not d or d.get("n", 0) == 0:
        return "n/a"
    return f"mean={d['mean']:.4g}  med={d['median']:.4g}  p95={d['p95']:.4g}  (n={d['n']})"


def _write_md(suite: dict, path: Path) -> None:
    c = suite["clean"]
    lines = [
        f"# Eval suite — {suite['arch']} / {suite['ablation']}",
        "",
        f"- ckpt: `{suite['ckpt']}`",
        f"- split: {suite['split']}",
        f"- n: {c['n']}",
        "",
        "## Clean",
        "",
        f"- CURVE_TYPE_MACRO_F1 = {c['CURVE_TYPE_MACRO_F1']:.4f}",
        f"- LINE_F1 = {c['LINE_F1']:.4f}",
        f"- CIRCLE_F1 = {c['CIRCLE_F1']:.4f}",
        f"- ELLIPSE_F1 = {c['ELLIPSE_F1']:.4f}",
        f"- BSPLINE_F1 = {c['BSPLINE_F1']:.4f}",
        f"- LINE_DIRECTION_ERROR: {_fmt_err(c.get('LINE_DIRECTION_ERROR'))}",
        f"- CIRCLE_NORMAL_ERROR: {_fmt_err(c.get('CIRCLE_NORMAL_ERROR'))}",
        f"- CIRCLE_RADIUS_ERROR: {_fmt_err(c.get('CIRCLE_RADIUS_ERROR'))}",
        f"- ELLIPSE_AXIS_ERROR: {_fmt_err(c.get('ELLIPSE_AXIS_ERROR'))}",
        f"- RECON_CHAMFER: {_fmt_err(c.get('RECON_CHAMFER'))}",
        "",
        "## Noise robustness (partial=1.0)",
        "",
        "| noise_rel | macro_F1 | CIRCLE_F1 | ELLIPSE_F1 | CIRCLE_NORMAL mean° | RECON_CHAMFER mean |",
        "|---|---|---|---|---|---|",
    ]
    for k, r in suite["noise"].items():
        cn = r.get("CIRCLE_NORMAL_ERROR") or {}
        rc = r.get("RECON_CHAMFER") or {}
        lines.append(
            f"| {k} | {r['CURVE_TYPE_MACRO_F1']:.4f} | {r['CIRCLE_F1']:.4f} | {r['ELLIPSE_F1']:.4f} | "
            f"{(cn.get('mean') if cn else float('nan'))} | {(rc.get('mean') if rc else float('nan'))} |"
        )
    lines += [
        "",
        "## Partial-curve robustness (noise=0)",
        "",
        "| frac | macro_F1 | LINE_F1 | CIRCLE_F1 | RECON_CHAMFER mean |",
        "|---|---|---|---|---|",
    ]
    for k, r in suite["partial"].items():
        rc = r.get("RECON_CHAMFER") or {}
        lines.append(
            f"| {k} | {r['CURVE_TYPE_MACRO_F1']:.4f} | {r['LINE_F1']:.4f} | {r['CIRCLE_F1']:.4f} | "
            f"{(rc.get('mean') if rc else float('nan'))} |"
        )
    buckets = c["geometry"].get("arc_buckets", {})
    lines += ["", "## Arc-coverage buckets (CIRCLE+ELLIPSE, clean)", ""]
    lines.append("| bucket | n | type_acc | recon_chamfer_mean |")
    lines.append("|---|---|---|---|")
    for name, b in buckets.items():
        lines.append(
            f"| {name} | {b.get('n', 0)} | {b.get('type_acc', 'n/a')} | {b.get('recon_chamfer_mean', 'n/a')} |"
        )
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", type=Path, required=True)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--split", default="test")
    args = ap.parse_args()
    suite = run_eval_suite(args.ckpt, args.device, split=args.split)
    print(json.dumps({
        "CURVE_TYPE_MACRO_F1": suite["clean"]["CURVE_TYPE_MACRO_F1"],
        "NOISE_1E3_METRICS": {
            "macro_f1": suite["noise"].get("0.001", {}).get("CURVE_TYPE_MACRO_F1"),
            "CIRCLE_NORMAL_ERROR": suite["noise"].get("0.001", {}).get("CIRCLE_NORMAL_ERROR"),
        },
        "PARTIAL_50_METRICS": suite["partial"].get("0.5", {}),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
