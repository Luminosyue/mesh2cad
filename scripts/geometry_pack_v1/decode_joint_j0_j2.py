#!/usr/bin/env python3
"""Decode + evaluate joint J0 (surface) vs J2 (separate edge) on the test split.

Metrics mirror scripts/deepcad/decode_eval_split.py:
  exact match, op recall/F1, pred/gt solid-op ratio, under-generation,
  EOS/MAX_LENGTH, STEP valid, Chamfer vs GT mesh.

Optional sep-edge fingerprint: real vs zero vs wrong on a subset.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "SpatialLM"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))
sys.path.insert(0, str(ROOT / "scripts" / "separate_edge_tokens_v1"))

from separate_edge_tokens_v1.common import (  # noqa: E402
    build_prompt,
    load_model,
    make_plugin,
    set_deterministic_serialization,
    zero_edge_like,
)
from decode_eval_split import (  # noqa: E402
    _exec_step,
    _f1_multiset,
    _geom,
    _op_bucket,
    _op_multiset,
    _solid_op_count,
    _stratified_metrics,
)
from decode_overfit10 import _normalize_dsl, _op_tokens  # noqa: E402

MEDIA_DEFAULT = ROOT / "cad_spatial_dataset"
DATASET_TRAIN = {
    "deepcad": ROOT / "cad_spatial_dataset/DeepCAD/train",
    "fusion360": ROOT / "cad_spatial_dataset/Fusion360/train",
}


def _generation_stop_reason(
    generated_ids, prompt_len: int, max_new_tokens: int, eos_token_id
) -> tuple[int, str]:
    new_ids = generated_ids[prompt_len:]
    n = int(len(new_ids))
    if n >= max_new_tokens:
        return n, "MAX_LENGTH"
    if eos_token_id is not None and n > 0 and int(new_ids[-1]) == int(eos_token_id):
        return n, "EOS"
    return n, "EOS"


def _train_dir(rec: dict) -> Path:
    ds = str(rec.get("dataset", "deepcad")).lower()
    if ds not in DATASET_TRAIN:
        raise KeyError(f"unknown dataset={ds!r} for {rec.get('id')}")
    return DATASET_TRAIN[ds]


def _load_surface_only(plugin, surface_npy: Path) -> torch.Tensor:
    feats = plugin._load_cad_npy(str(surface_npy))
    return torch.as_tensor(feats[None, ...], dtype=torch.float32)


def _load_sepedge(plugin, surface_npy: Path) -> tuple[torch.Tensor, torch.Tensor]:
    surface, edge = plugin._load_cad_separate_edge(str(surface_npy))
    return (
        torch.as_tensor(surface[None, ...], dtype=torch.float32),
        torch.as_tensor(edge[None, ...], dtype=torch.float32),
    )


@torch.inference_mode()
def generate_dsl(
    model,
    tokenizer,
    surface: torch.Tensor,
    edge: torch.Tensor | None,
    separate_edge: bool,
    max_new_tokens: int,
) -> tuple[str, dict]:
    prompt = build_prompt(separate_edge=separate_edge)
    conversation = [{"role": "user", "content": prompt}]
    input_ids = tokenizer.apply_chat_template(
        conversation, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)
    prompt_len = int(input_ids.shape[1])
    kwargs = dict(
        input_ids=input_ids,
        attention_mask=torch.ones_like(input_ids),
        point_clouds=surface.to(model.device),
        max_new_tokens=max_new_tokens,
        do_sample=False,
        num_beams=1,
        use_cache=True,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
    )
    if separate_edge and edge is not None:
        kwargs["edge_clouds"] = edge.to(model.device)
    out = model.generate(**kwargs)
    pred_ids = out[0]
    text = tokenizer.decode(pred_ids[prompt_len:], skip_special_tokens=True)
    n_tok, stop_reason = _generation_stop_reason(
        pred_ids.tolist(), prompt_len, max_new_tokens, tokenizer.eos_token_id
    )
    return text, {
        "max_new_tokens": max_new_tokens,
        "prediction_tokens": n_tok,
        "stop_reason": stop_reason,
    }


def _evaluate_one(
    rec: dict,
    pred: str,
    gen_meta: dict,
    sample_out: Path,
    media_dir: Path,
) -> dict:
    from cad_canonical import load_transform_json, transform_dsl
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code

    sid = rec["id"]
    sample_id = rec.get("sample_id") or sid
    gt = rec["conversations"][1]["value"]
    sample_out.mkdir(parents=True, exist_ok=True)
    (sample_out / "pred.txt").write_text(pred, encoding="utf-8")
    (sample_out / "generation_meta.json").write_text(
        json.dumps(gen_meta, indent=2) + "\n", encoding="utf-8"
    )
    (sample_out / "gt.dsl").write_text(gt, encoding="utf-8")

    exact = _normalize_dsl(pred) == _normalize_dsl(gt)
    gt_ops, pred_ops = _op_tokens(gt), _op_tokens(pred)
    op_recall = len(gt_ops & pred_ops) / len(gt_ops) if gt_ops else 0.0
    gt_ms, pred_ms = _op_multiset(gt), _op_multiset(pred)
    op_f1 = _f1_multiset(gt_ms, pred_ms)
    gt_op_count = _solid_op_count(gt)
    predicted_op_count = _solid_op_count(pred)
    op_count_ratio = predicted_op_count / gt_op_count if gt_op_count > 0 else None

    try:
        code = extract_dsl_code(pred)
    except Exception:
        code = pred
    (sample_out / "pred_canonical.dsl").write_text(
        code if code.endswith("\n") else code + "\n", encoding="utf-8"
    )

    train_dir = _train_dir(rec)
    tf_path = train_dir / sample_id / "coordinate_transform.json"
    code_source = code
    if tf_path.exists():
        try:
            tf = load_transform_json(tf_path)
            code_source = transform_dsl(code, tf, inverse=True)
            (sample_out / "pred_source.dsl").write_text(code_source, encoding="utf-8")
        except Exception as exc:
            (sample_out / "inverse_transform_error.txt").write_text(str(exc), encoding="utf-8")

    exec_rec = _exec_step(code_source, sample_out)
    geom: dict[str, Any] = {}
    gt_mesh = train_dir / sample_id / "model.obj"
    if exec_rec.get("step_ok") and exec_rec.get("stl") and gt_mesh.exists():
        try:
            geom = _geom(gt_mesh, Path(exec_rec["stl"]))
        except Exception as exc:
            geom = {"error": str(exc)}

    return {
        "id": sid,
        "sample_id": sample_id,
        "dataset": rec.get("dataset"),
        "exact_match": exact,
        "gt_ops": sorted(gt_ops),
        "pred_ops": sorted(pred_ops),
        "op_recall": op_recall,
        "op_f1": op_f1,
        "gt_op_count": gt_op_count,
        "predicted_op_count": predicted_op_count,
        "predicted_op_count_over_gt_op_count": op_count_ratio,
        "under_generation": (
            predicted_op_count < gt_op_count if gt_op_count > 0 else False
        ),
        **gen_meta,
        **exec_rec,
        "geometry": geom,
        "surface_npy": str(media_dir / rec["point_clouds"][0]),
    }


def _summarize(rows: list[dict], meta: dict) -> dict:
    chamfers = [
        r["geometry"]["chamfer_norm"]
        for r in rows
        if "chamfer_norm" in r.get("geometry", {})
    ]
    haus = [
        r["geometry"]["hausdorff_95_norm"]
        for r in rows
        if "hausdorff_95_norm" in r.get("geometry", {})
    ]
    vols = [
        r["geometry"]["volume_error"]
        for r in rows
        if r.get("geometry", {}).get("volume_error") is not None
    ]
    ratios = [
        r["predicted_op_count_over_gt_op_count"]
        for r in rows
        if r.get("predicted_op_count_over_gt_op_count") is not None
    ]
    stop_counts = Counter(r.get("stop_reason") for r in rows if r.get("stop_reason"))
    exact_n = sum(1 for r in rows if r.get("exact_match"))
    return {
        **meta,
        "n_samples": len(rows),
        "exact_match_n": exact_n,
        "exact_match_rate": exact_n / max(len(rows), 1),
        "mean_op_recall": float(np.mean([r["op_recall"] for r in rows])) if rows else 0.0,
        "mean_op_f1": float(np.mean([r["op_f1"] for r in rows])) if rows else 0.0,
        "mean_gt_op_count": float(np.mean([r["gt_op_count"] for r in rows])) if rows else 0.0,
        "mean_predicted_op_count": float(np.mean([r["predicted_op_count"] for r in rows]))
        if rows
        else 0.0,
        "mean_predicted_op_count_over_gt_op_count": float(np.mean(ratios)) if ratios else None,
        "under_generation_rate": sum(1 for r in rows if r.get("under_generation"))
        / max(len(rows), 1),
        "stop_reason_counts": dict(stop_counts),
        "eos_rate": stop_counts.get("EOS", 0) / max(len(rows), 1),
        "max_length_rate": stop_counts.get("MAX_LENGTH", 0) / max(len(rows), 1),
        "stratified": _stratified_metrics(rows),
        "dsl_parse_valid_rate": sum(1 for r in rows if r.get("parsed")) / max(len(rows), 1),
        "step_valid_rate": sum(1 for r in rows if r.get("step_ok")) / max(len(rows), 1),
        "mean_chamfer_norm": float(np.mean(chamfers)) if chamfers else None,
        "mean_hausdorff_95_norm": float(np.mean(haus)) if haus else None,
        "mean_volume_error": float(np.mean(vols)) if vols else None,
        "by_dataset": {
            ds: _stratified_metrics([r for r in rows if r.get("dataset") == ds]).get("all", {})
            for ds in sorted({r.get("dataset") for r in rows if r.get("dataset")})
        },
        "samples": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument(
        "--split-json",
        type=Path,
        default=MEDIA_DEFAULT / "joint_deepcad_fusion360_v1/joint_j0j2_v1_test.json",
    )
    ap.add_argument(
        "--variant",
        choices=("j0", "j2", "j2o", "j2p"),
        required=True,
        help="j0=surface; j2/j2o=oracle sharp; j2p=detected sharp",
    )
    ap.add_argument("--media-dir", type=Path, default=MEDIA_DEFAULT)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dtype", default="bfloat16", choices=("bfloat16", "float32"))
    ap.add_argument("--max-new-tokens", type=int, default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument(
        "--edge-source",
        choices=("gt_sharp", "detected", "legacy"),
        default=None,
        help="Override CAD_EDGE_SOURCE (default: gt_sharp for j2/j2o, detected for j2p)",
    )
    ap.add_argument(
        "--fingerprint-n",
        type=int,
        default=0,
        help="For sep-edge variants: also decode first N with zero+wrong edge",
    )
    ap.add_argument(
        "--fingerprint-conds",
        default="zero,wrong",
        help="Comma list of fingerprint conditions besides real (default: zero,wrong)",
    )
    args = ap.parse_args()

    separate_edge = args.variant in ("j2", "j2o", "j2p")
    if args.max_new_tokens is None:
        args.max_new_tokens = 4096

    if args.edge_source is None:
        args.edge_source = "detected" if args.variant == "j2p" else "gt_sharp"
    os.environ["CAD_EDGE_SOURCE"] = args.edge_source
    if separate_edge:
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
    else:
        os.environ.pop("CAD_USE_SEPARATE_EDGE_TOKENS", None)

    fp_conds = [
        c.strip()
        for c in args.fingerprint_conds.split(",")
        if c.strip() and c.strip() != "real"
    ]
    for c in fp_conds:
        if c not in ("zero", "wrong"):
            raise SystemExit(f"unsupported fingerprint cond {c!r}; use zero,wrong")

    records = json.loads(args.split_json.read_text(encoding="utf-8"))
    records = records[args.offset :]
    if args.limit is not None:
        records = records[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)

    plugin = make_plugin(separate_edge=separate_edge)
    model, tokenizer = load_model(
        args.checkpoint,
        separate_edge=separate_edge,
        device="cuda",
        dtype=getattr(torch, args.dtype),
        freeze_sonata=True,
    )
    set_deterministic_serialization(model.point_backbone)
    model.eval()

    edge_cache: dict[str, torch.Tensor] = {}
    if separate_edge and args.fingerprint_n > 0 and "wrong" in fp_conds:
        for rec in records[: args.fingerprint_n]:
            npy = args.media_dir / rec["point_clouds"][0]
            _, e = _load_sepedge(plugin, npy)
            edge_cache[rec["id"]] = e

    def _fingerprint_edge(cond: str, edge, i: int):
        if cond == "zero":
            return zero_edge_like(edge), "zero", {}
        all_recs = json.loads(args.split_json.read_text(encoding="utf-8"))
        other = all_recs[(args.offset + i + 1) % len(all_recs)]
        edge_alt = edge_cache.get(other["id"])
        if edge_alt is None:
            _, edge_alt = _load_sepedge(
                plugin, args.media_dir / other["point_clouds"][0]
            )
        return edge_alt, "wrong", {"wrong_edge_from": other["id"]}

    rows: list[dict] = []
    fp_by_cond: dict[str, list[dict]] = {c: [] for c in fp_conds}
    for i, rec in enumerate(records):
        sid = rec["id"]
        sample_out = args.out / sid
        row_path = sample_out / "row.json"

        if args.resume and row_path.exists():
            row = json.loads(row_path.read_text(encoding="utf-8"))
            rows.append(row)
            print(f"[resume] {sid}")
            if separate_edge and i < args.fingerprint_n:
                npy = args.media_dir / rec["point_clouds"][0]
                surface, edge = _load_sepedge(plugin, npy)
                for cond in fp_conds:
                    fp_path = args.out / f"fingerprint_{cond}" / sid / "row.json"
                    if fp_path.exists():
                        fp_by_cond[cond].append(json.loads(fp_path.read_text(encoding="utf-8")))
                        continue
                    edge_alt, tag, extra = _fingerprint_edge(cond, edge, i)
                    fp_out = args.out / f"fingerprint_{tag}" / sid
                    pred_a, meta_a = generate_dsl(
                        model, tokenizer, surface, edge_alt,
                        separate_edge=True, max_new_tokens=args.max_new_tokens,
                    )
                    fp_row = _evaluate_one(rec, pred_a, meta_a, fp_out, args.media_dir)
                    fp_row["edge_condition"] = tag
                    fp_row.update(extra)
                    (fp_out / "row.json").write_text(
                        json.dumps(fp_row, indent=2) + "\n", encoding="utf-8"
                    )
                    fp_by_cond[tag].append(fp_row)
                    print(
                        f"  [{tag}] exact={fp_row['exact_match']} "
                        f"step={fp_row.get('step_ok')} op_f1={fp_row['op_f1']:.2f}"
                    )
            continue

        npy = args.media_dir / rec["point_clouds"][0]
        if separate_edge:
            surface, edge = _load_sepedge(plugin, npy)
        else:
            surface = _load_surface_only(plugin, npy)
            edge = None

        pred, gen_meta = generate_dsl(
            model, tokenizer, surface, edge,
            separate_edge=separate_edge, max_new_tokens=args.max_new_tokens,
        )
        row = _evaluate_one(rec, pred, gen_meta, sample_out, args.media_dir)
        row["edge_condition"] = "real" if separate_edge else "none"
        row_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        rows.append(row)

        ratio_s = (
            f"{row['predicted_op_count_over_gt_op_count']:.2f}"
            if row.get("predicted_op_count_over_gt_op_count") is not None
            else "n/a"
        )
        print(
            f"[{args.variant}] {sid}: exact={row['exact_match']} "
            f"parsed={row.get('parsed')} step={row.get('step_ok')} "
            f"op_f1={row['op_f1']:.2f} pred/gt={row['predicted_op_count']}/"
            f"{row['gt_op_count']}={ratio_s} stop={row.get('stop_reason')} "
            f"chamfer={row.get('geometry', {}).get('chamfer_norm')}"
        )

        if separate_edge and i < args.fingerprint_n:
            for cond in fp_conds:
                edge_alt, tag, extra = _fingerprint_edge(cond, edge, i)
                fp_out = args.out / f"fingerprint_{tag}" / sid
                pred_a, meta_a = generate_dsl(
                    model, tokenizer, surface, edge_alt,
                    separate_edge=True, max_new_tokens=args.max_new_tokens,
                )
                fp_row = _evaluate_one(rec, pred_a, meta_a, fp_out, args.media_dir)
                fp_row["edge_condition"] = tag
                fp_row.update(extra)
                (fp_out / "row.json").write_text(
                    json.dumps(fp_row, indent=2) + "\n", encoding="utf-8"
                )
                fp_by_cond[tag].append(fp_row)
                print(
                    f"  [{tag}] exact={fp_row['exact_match']} "
                    f"step={fp_row.get('step_ok')} op_f1={fp_row['op_f1']:.2f}"
                )

        if (i + 1) % 20 == 0 or (i + 1) == len(records):
            report = _summarize(
                rows,
                {
                    "checkpoint": str(args.checkpoint),
                    "variant": args.variant,
                    "split": str(args.split_json),
                    "max_new_tokens": args.max_new_tokens,
                    "edge_source": args.edge_source,
                },
            )
            (args.out / "report.json").write_text(
                json.dumps(report, indent=2) + "\n", encoding="utf-8"
            )

    report = _summarize(
        rows,
        {
            "checkpoint": str(args.checkpoint),
            "variant": args.variant,
            "split": str(args.split_json),
            "max_new_tokens": args.max_new_tokens,
            "edge_source": args.edge_source,
        },
    )
    if any(fp_by_cond.values()):
        n_fp = max(len(v) for v in fp_by_cond.values())
        real_sub = rows[:n_fp]
        report["fingerprint"] = {
            "n": n_fp,
            "real": {k: v for k, v in _summarize(real_sub, {}).items() if k != "samples"},
        }
        for cond, fp_rows in fp_by_cond.items():
            report["fingerprint"][cond] = {
                k: v for k, v in _summarize(fp_rows, {}).items() if k != "samples"
            }
        (args.out / "fingerprint_report.json").write_text(
            json.dumps(report["fingerprint"], indent=2) + "\n", encoding="utf-8"
        )

    (args.out / "report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
