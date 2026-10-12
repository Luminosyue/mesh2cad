#!/usr/bin/env python3
"""P2 test diagnostics: confusion matrix + arc-span buckets (no training).

Reads only curve_token_data_v1 + P2 checkpoint. Writes under
ours3/curve_encoder_baseline_v1/runs/P2_frozen_v1/diagnostics/.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_encoder_baseline_v1.config import (  # noqa: E402
    CURVE_DATA_ROOT,
    EXPERIMENTS,
    ID_TO_TYPE,
    PRIMARY_TYPES,
    RUNS_DIR,
    TYPE_TO_ID,
)
from curve_encoder_baseline_v1.dataset import (  # noqa: E402
    CACHE_DIR,
    CurveEncoderDataset,
    collate_curves,
)
from curve_encoder_baseline_v1.models import build_model  # noqa: E402

TWOPI = 2.0 * math.pi
# Half-open except the last open-arc bucket which includes 360°.
# 180° lands in 90°–180° (not >180°).
BUCKETS = [
    ("closed", None),
    ("<15°", (0.0, 15.0)),
    ("15°–45°", (15.0, 45.0)),
    ("45°–90°", (45.0, 90.0)),
    ("90°–180°", (90.0, 180.0)),  # includes 180°
    (">180°", (180.0, 360.0)),  # (180, 360]
]


def arc_span_deg(curve: dict) -> tuple[float, bool, str]:
    """Return (span_deg, is_closed, bucket_name).

    CIRCLE/ELLIPSE OCC parameter is angle-like (radians). Span = |u_end-u_start|.
    Closed curves are forced into the ``closed`` bucket.
    """
    u0 = float(curve["u_start"])
    u1 = float(curve["u_end"])
    span_rad = abs(u1 - u0)
    # wrap full turns into [0, 2π]
    span_rad = span_rad % TWOPI
    # floating near-full circle
    if span_rad < 1e-8 and abs(u1 - u0) > 1.0:
        span_rad = TWOPI
    span_deg = float(np.degrees(span_rad))
    closed = bool(curve.get("is_closed", False)) or span_deg >= 359.0
    if closed:
        return span_deg if span_deg > 1e-6 else 360.0, True, "closed"
    for name, rng in BUCKETS:
        if name == "closed":
            continue
        lo, hi = rng
        if name == "90°–180°":
            if lo <= span_deg <= hi:
                return span_deg, False, name
        elif name == ">180°":
            if hi >= span_deg > lo:
                return span_deg, False, name
        else:
            if lo <= span_deg < hi:
                return span_deg, False, name
    return span_deg, False, ">180°"


def f1_recall(y_true: np.ndarray, y_pred: np.ndarray, cls: int) -> dict:
    tp = int(((y_true == cls) & (y_pred == cls)).sum())
    fp = int(((y_true != cls) & (y_pred == cls)).sum())
    fn = int(((y_true == cls) & (y_pred != cls)).sum())
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "n_gt": int((y_true == cls).sum()),
        "n_pred": int((y_pred == cls).sum()),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": prec,
        "recall": rec,
        "f1": f1,
    }


@torch.no_grad()
def predict_test(ckpt_path: Path, device: torch.device) -> tuple[np.ndarray, np.ndarray, list]:
    spec = EXPERIMENTS["P2"]
    ds = CurveEncoderDataset("test", spec["features"], force_rebuild=False)
    meta = json.loads((CACHE_DIR / "frozen_v1_test_meta.json").read_text(encoding="utf-8"))
    refs = meta["refs"]
    assert len(refs) == len(ds)

    model = build_model(spec["encoder"], tuple(spec["features"])).to(device)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model"])
    model.eval()

    loader = DataLoader(
        ds,
        batch_size=512,
        shuffle=False,
        num_workers=4,
        collate_fn=collate_curves,
        pin_memory=device.type == "cuda",
    )
    preds, gts = [], []
    for batch in loader:
        feats = batch["feats"].to(device)
        out = model(feats)
        preds.append(out["type_logits"].argmax(-1).cpu().numpy())
        gts.append(batch["type_id"].numpy())
    y_pred = np.concatenate(preds)
    y_true = np.concatenate(gts)
    return y_true, y_pred, refs


def load_curve(ref: dict) -> dict:
    # cad_dir from joint: deepcad_train/<id> or fusion360_train/<id>
    ds = ref["dataset"]
    sub = "deepcad_train" if ds == "deepcad" else "fusion360_train"
    path = CURVE_DATA_ROOT / sub / ref["sample_id"] / "curves.json"
    curves = json.loads(path.read_text(encoding="utf-8"))["curves"]
    by_edge = {int(c["edge_id"]): c for c in curves}
    return by_edge[int(ref["edge_id"])]


def confusion(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    n = len(PRIMARY_TYPES)
    cm = np.zeros((n, n), dtype=np.int64)
    for t, p in zip(y_true.tolist(), y_pred.tolist()):
        cm[int(t), int(p)] += 1
    rows = {}
    for i, gt in enumerate(PRIMARY_TYPES):
        total = int(cm[i].sum())
        dist = {
            PRIMARY_TYPES[j]: {
                "count": int(cm[i, j]),
                "frac": float(cm[i, j] / total) if total else 0.0,
            }
            for j in range(n)
        }
        rows[gt] = {"n": total, "predicted": dist}
    # focused questions
    focus = {
        "ELLIPSE→CIRCLE": int(cm[TYPE_TO_ID["ELLIPSE"], TYPE_TO_ID["CIRCLE"]]),
        "ELLIPSE→LINE": int(cm[TYPE_TO_ID["ELLIPSE"], TYPE_TO_ID["LINE"]]),
        "ELLIPSE→BSPLINE": int(cm[TYPE_TO_ID["ELLIPSE"], TYPE_TO_ID["BSPLINE"]]),
        "ELLIPSE→ELLIPSE": int(cm[TYPE_TO_ID["ELLIPSE"], TYPE_TO_ID["ELLIPSE"]]),
        "CIRCLE→LINE": int(cm[TYPE_TO_ID["CIRCLE"], TYPE_TO_ID["LINE"]]),
        "CIRCLE→CIRCLE": int(cm[TYPE_TO_ID["CIRCLE"], TYPE_TO_ID["CIRCLE"]]),
        "CIRCLE→ELLIPSE": int(cm[TYPE_TO_ID["CIRCLE"], TYPE_TO_ID["ELLIPSE"]]),
        "CIRCLE→BSPLINE": int(cm[TYPE_TO_ID["CIRCLE"], TYPE_TO_ID["BSPLINE"]]),
        "BSPLINE→LINE": int(cm[TYPE_TO_ID["BSPLINE"], TYPE_TO_ID["LINE"]]),
        "BSPLINE→BSPLINE": int(cm[TYPE_TO_ID["BSPLINE"], TYPE_TO_ID["BSPLINE"]]),
        "BSPLINE→CIRCLE": int(cm[TYPE_TO_ID["BSPLINE"], TYPE_TO_ID["CIRCLE"]]),
        "BSPLINE→ELLIPSE": int(cm[TYPE_TO_ID["BSPLINE"], TYPE_TO_ID["ELLIPSE"]]),
    }
    return {
        "labels": list(PRIMARY_TYPES),
        "matrix": cm.tolist(),
        "by_gt": rows,
        "focus": focus,
    }


def span_bucket_analysis(y_true, y_pred, refs, target_types=("CIRCLE", "ELLIPSE")) -> dict:
    # attach span for every CIRCLE/ELLIPSE GT
    records = []
    for i, ref in enumerate(refs):
        gt = ID_TO_TYPE[int(y_true[i])]
        if gt not in target_types:
            continue
        curve = load_curve(ref)
        assert curve["curve_type"] == gt
        span_deg, closed, bucket = arc_span_deg(curve)
        ecc = None
        axis_ratio = None
        if gt == "ELLIPSE":
            p = curve["world_parameters"]
            a = float(p["major_radius"])
            b = float(p["minor_radius"])
            axis_ratio = b / a if a > 1e-12 else None  # 1 = circle-like
            if a > 1e-12 and a >= b:
                ecc = math.sqrt(max(0.0, 1.0 - (b / a) ** 2))
        elif gt == "CIRCLE":
            axis_ratio = 1.0
            ecc = 0.0
        records.append(
            {
                "idx": i,
                "gt": gt,
                "pred": ID_TO_TYPE[int(y_pred[i])],
                "span_deg": span_deg,
                "closed": closed,
                "bucket": bucket,
                "correct": int(y_true[i]) == int(y_pred[i]),
                "axis_ratio": axis_ratio,
                "eccentricity": ecc,
            }
        )

    out = {"n_records": len(records), "by_type": {}}
    for tname in target_types:
        tid = TYPE_TO_ID[tname]
        out["by_type"][tname] = {"buckets": {}, "span_hist_all": {}}
        # overall type metrics already known; per-bucket recall among GT of this type
        for bname, _ in BUCKETS:
            idxs = [r["idx"] for r in records if r["gt"] == tname and r["bucket"] == bname]
            if not idxs:
                out["by_type"][tname]["buckets"][bname] = {
                    "n_gt": 0,
                    "recall": None,
                    "pred_dist": {},
                    "span_deg_mean": None,
                }
                continue
            yt = y_true[idxs]
            yp = y_pred[idxs]
            # recall within bucket = fraction correctly predicted as tname
            recall = float((yp == tid).mean())
            # also local F1 treating only this subset as positives of interest:
            # among these GT, precision isn't well-defined globally; report recall + pred mix
            pred_dist = {
                PRIMARY_TYPES[j]: int((yp == j).sum()) for j in range(len(PRIMARY_TYPES))
            }
            spans = [r["span_deg"] for r in records if r["idx"] in set(idxs)]
            out["by_type"][tname]["buckets"][bname] = {
                "n_gt": len(idxs),
                "recall": recall,
                "n_correct": int((yp == tid).sum()),
                "pred_dist": pred_dist,
                "span_deg_mean": float(np.mean(spans)),
                "span_deg_median": float(np.median(spans)),
            }
        # for reporting F1-like within bucket we need FP from same bucket predicted as type
        # but FP would require all preds in bucket — only CIRCLE/ELLIPSE have buckets.
        # Report GT-conditioned recall (primary) + confusion within bucket.
    out["records_sample_errors"] = {
        tname: [
            {
                "bucket": r["bucket"],
                "span_deg": round(r["span_deg"], 2),
                "pred": r["pred"],
                "axis_ratio": None if r["axis_ratio"] is None else round(r["axis_ratio"], 4),
                "eccentricity": None if r["eccentricity"] is None else round(r["eccentricity"], 4),
                "sample_id": refs[r["idx"]]["sample_id"],
                "edge_id": refs[r["idx"]]["edge_id"],
            }
            for r in records
            if r["gt"] == tname and not r["correct"]
        ][:40]
        for tname in target_types
    }
    # ELLIPSE → CIRCLE: are they near-circular?
    e2c = [r for r in records if r["gt"] == "ELLIPSE" and r["pred"] == "CIRCLE"]
    e_ok = [r for r in records if r["gt"] == "ELLIPSE" and r["correct"]]
    def _stat(xs):
        if not xs:
            return None
        a = np.asarray(xs, dtype=np.float64)
        return {
            "n": int(a.size),
            "mean": float(a.mean()),
            "median": float(np.median(a)),
            "min": float(a.min()),
            "max": float(a.max()),
        }

    out["ellipse_to_circle_geometry"] = {
        "n": len(e2c),
        "span_deg": _stat([r["span_deg"] for r in e2c]),
        "axis_ratio": _stat([r["axis_ratio"] for r in e2c if r["axis_ratio"] is not None]),
        "eccentricity": _stat([r["eccentricity"] for r in e2c if r["eccentricity"] is not None]),
        "bucket_counts": {
            b: sum(1 for r in e2c if r["bucket"] == b) for b, _ in BUCKETS
        },
    }
    out["ellipse_correct_geometry"] = {
        "n": len(e_ok),
        "span_deg": _stat([r["span_deg"] for r in e_ok]),
        "axis_ratio": _stat([r["axis_ratio"] for r in e_ok if r["axis_ratio"] is not None]),
        "eccentricity": _stat([r["eccentricity"] for r in e_ok if r["eccentricity"] is not None]),
    }
    return out


def to_markdown(cm: dict, buckets: dict) -> str:
    labels = cm["labels"]
    mat = cm["matrix"]
    lines = ["# P2 test diagnostics", "", "## A. Confusion matrix (rows=GT, cols=Pred)", ""]
    header = "| GT \\ Pred | " + " | ".join(labels) + " | n |"
    sep = "| --- | " + " | ".join(["---:"] * len(labels)) + " | ---: |"
    lines += [header, sep]
    for i, gt in enumerate(labels):
        row = [gt] + [str(mat[i][j]) for j in range(len(labels))] + [str(sum(mat[i]))]
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "### Focus counts", ""]
    for k, v in cm["focus"].items():
        gt = k.split("→")[0]
        n = cm["by_gt"][gt]["n"]
        frac = v / n if n else 0.0
        lines.append(f"- **{k}**: {v} / {n} ({frac:.1%})")

    lines += ["", "## B. Arc-span buckets (GT-conditioned recall)", ""]
    lines.append(
        "Span = `|u_end − u_start|` in degrees (OCC angle parameter). "
        "`closed` overrides span buckets."
    )
    lines.append("")
    for tname in ("ELLIPSE", "CIRCLE"):
        lines.append(f"### {tname}")
        lines.append("")
        lines.append(
            "| bucket | n_gt | recall | →LINE | →CIRCLE | →ELLIPSE | →BSPLINE | span° mean |"
        )
        lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
        for bname, _ in BUCKETS:
            b = buckets["by_type"][tname]["buckets"][bname]
            if b["n_gt"] == 0:
                lines.append(f"| {bname} | 0 | — | — | — | — | — | — |")
                continue
            pd = b["pred_dist"]
            lines.append(
                f"| {bname} | {b['n_gt']} | {b['recall']:.3f} | "
                f"{pd.get('LINE',0)} | {pd.get('CIRCLE',0)} | {pd.get('ELLIPSE',0)} | "
                f"{pd.get('BSPLINE',0)} | {b['span_deg_mean']:.1f} |"
            )
        lines.append("")

    e2c = buckets.get("ellipse_to_circle_geometry", {})
    eok = buckets.get("ellipse_correct_geometry", {})
    lines += ["## ELLIPSE→CIRCLE geometry (near-circular?)", ""]
    if e2c.get("n"):
        ar = e2c.get("axis_ratio") or {}
        ec = e2c.get("eccentricity") or {}
        sp = e2c.get("span_deg") or {}
        lines.append(
            f"- misclassified as CIRCLE: n={e2c['n']}, "
            f"span° median={sp.get('median')}, "
            f"axis_ratio(minor/major) median={ar.get('median')}, "
            f"eccentricity median={ec.get('median')}"
        )
        lines.append(f"- bucket mix: {e2c.get('bucket_counts')}")
    if eok.get("n"):
        ar = eok.get("axis_ratio") or {}
        ec = eok.get("eccentricity") or {}
        sp = eok.get("span_deg") or {}
        lines.append(
            f"- correctly classified: n={eok['n']}, "
            f"span° median={sp.get('median')}, "
            f"axis_ratio median={ar.get('median')}, "
            f"eccentricity median={ec.get('median')}"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--ckpt",
        type=Path,
        default=RUNS_DIR / "P2_frozen_v1" / "best.pt",
    )
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = ap.parse_args()

    out_dir = RUNS_DIR / "P2_frozen_v1" / "diagnostics"
    out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(args.device)

    print(f"[diag] loading {args.ckpt} on {device}")
    y_true, y_pred, refs = predict_test(args.ckpt, device)
    cm = confusion(y_true, y_pred)
    print("[diag] confusion done; computing arc spans…")
    buckets = span_bucket_analysis(y_true, y_pred, refs)

    payload = {
        "exp": "P2",
        "split": "test",
        "n": int(len(y_true)),
        "confusion": cm,
        "arc_span_buckets": buckets,
        "span_definition": (
            "abs(u_end-u_start) in degrees from curves.json; "
            "CIRCLE/ELLIPSE OCC parameter; closed flag or span>=359° → closed bucket"
        ),
    }
    (out_dir / "p2_test_diagnostics.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    md = to_markdown(cm, buckets)
    (out_dir / "p2_test_diagnostics.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"wrote {out_dir / 'p2_test_diagnostics.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
