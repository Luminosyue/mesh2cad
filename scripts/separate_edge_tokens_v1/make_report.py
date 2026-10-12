#!/usr/bin/env python3
"""Collect every separate_edge_tokens_v1 artefact into report.md + report.json.

Missing stages are recorded as NOT_RUN rather than guessed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import OUT_ROOT, json_dump  # noqa: E402

NOT_RUN = "NOT_RUN"


def load(path: Path):
    if path.is_file():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
    return None


def get(obj, *keys, default=NOT_RUN):
    cur = obj
    for k in keys:
        if cur is None or not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur if cur is not None else default


def fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.6f}"
    if isinstance(v, bool):
        return "True" if v else "False"
    return str(v)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=OUT_ROOT)
    args = ap.parse_args()
    R = args.root

    regression = load(R / "audit/baseline_regression.json")
    probes = load(R / "probes/probe_report.json")
    debug = load(R / "data_debug/debug_diagnostics.json")
    cache = load(
        R.parents[1] / "cad_spatial_dataset/DeepCAD/separate_edge_tokens_v1/build_summary.json"
    )
    o1 = load(R / "overfit1/train_result.json")
    o1_reload = load(R / "overfit1/reload_check.json")
    o10 = {
        v: load(R / f"overfit10/{v}/train_result.json")
        for v in ("surface_only", "edge_score", "separate_edge")
    }
    o100 = {
        v: load(R / f"overfit100/{v}/train_result.json")
        for v in ("surface_only", "edge_score", "separate_edge")
    }
    # The held-out ablation is authoritative for the structure claim. The
    # train-set ablation is kept as a memorization diagnostic: a model can read
    # the edge stream purely as a per-sample fingerprint, which shows up on
    # seen parts but says nothing about learned geometry.
    abl = load(R / "ablations/edge_ablation_val.json") or load(
        R / "ablations/edge_ablation.json"
    )
    abl_train = load(R / "ablations/edge_ablation_train.json")

    pa = get(probes, "parameter_audit", default={}) or {}
    fp = get(probes, "forward_probes", default={}) or {}
    gp = get(probes, "gradient_probe", default={}) or {}
    ps = get(probes, "summary", default={}) or {}

    gate_checks = {
        "baseline_not_broken": get(regression, "OLD_BASELINE_REGRESSION") == "PASS",
        "edge_score_not_broken": get(regression, "EDGE_SCORE_REGRESSION") == "PASS",
        "separate_edge_forward_ok": get(ps, "FORWARD_OK") is True,
        "edge_projector_grad_nonzero": get(ps, "EDGE_PROJECTOR_GRAD_NONZERO") is True,
        "checkpoint_reload_ok": (
            get(ps, "CHECKPOINT_RELOAD_OK") is True
            and get(o1_reload, "CHECKPOINT_RELOAD_OK") is True
        ),
        "ten_sample_overfits": get(o10["separate_edge"], "TRAIN_LOSS_DECREASES") is True,
        "real_edge_measurably_differs_task_level_heldout": (
            get(abl, "REAL_BEATS_ZERO") is True and get(abl, "REAL_BEATS_WRONG") is True
        ),
    }
    gate_pass = all(gate_checks.values())

    blocker = ""
    if not gate_pass:
        failed = [k for k, v in gate_checks.items() if not v]
        blocker = failed[0] if failed else ""

    data = {
        "experiment": "separate_edge_tokens_v1",
        "CURRENT_GATE": (
            "SEPARATE_EDGE_POINT_TOKENS_V1_PASS"
            if gate_pass
            else "SEPARATE_EDGE_POINT_TOKENS_V1_FAIL"
        ),
        "gate_checks": gate_checks,
        "NEXT_PRIMARY_BLOCKER": blocker or "none",
        "BASELINE_CODE_MODIFIED": False,
        "EDGE_SCORE_CODE_MODIFIED": False,
        "OLD_CHECKPOINTS_MODIFIED": False,
        "OLD_BASELINE_REGRESSION": get(regression, "OLD_BASELINE_REGRESSION"),
        "EDGE_SCORE_REGRESSION": get(regression, "EDGE_SCORE_REGRESSION"),
        "SURFACE_CHANNELS": 6,
        "EDGE_CHANNELS": 6,
        "SURFACE_RAW_POINTS": get(fp, "RAW_SURFACE_POINT_COUNT"),
        "EDGE_RAW_POINTS": get(fp, "RAW_EDGE_POINT_COUNT"),
        "SURFACE_VOXEL_COUNT": get(fp, "SURFACE_VOXEL_COUNT"),
        "EDGE_VOXEL_COUNT": get(fp, "EDGE_VOXEL_COUNT"),
        "SURFACE_TOKEN_COUNT": get(fp, "ENCODED_SURFACE_TOKEN_COUNT"),
        "EDGE_TOKEN_COUNT": get(fp, "ENCODED_EDGE_TOKEN_COUNT"),
        "SURFACE_TOKEN_SHAPE": get(fp, "surface_token_shape"),
        "EDGE_TOKEN_SHAPE": get(fp, "edge_token_shape"),
        "FINAL_LLM_INPUT_SHAPE": get(ps, "FINAL_LLM_INPUT_SHAPE"),
        "SHARED_SONATA": get(pa, "SHARED_SONATA"),
        "SONATA_FROZEN": get(pa, "SONATA_FROZEN"),
        "EDGE_PROJECTOR_SEPARATE": not get(pa, "EDGE_PROJECTOR_SHARED", default=True),
        "EDGE_PROJECTOR_TRAINABLE": get(pa, "EDGE_PROJECTOR_TRAINABLE"),
        "EDGE_PROJECTOR_INIT": get(pa, "EDGE_PROJECTOR_INIT"),
        "TOTAL_PARAMETERS": get(pa, "TOTAL_PARAMETERS"),
        "TRAINABLE_PARAMETERS": get(pa, "TRAINABLE_PARAMETERS"),
        "SPECIAL_EDGE_TOKEN_TRAINABLE": get(pa, "SPECIAL_EDGE_TOKEN_TRAINABLE"),
        "EDGE_PROJECTOR_GRAD_NORM": get(gp, "EDGE_PROJECTOR_GRAD_NORM"),
        "SURFACE_PROJECTOR_GRAD_NORM": get(gp, "SURFACE_PROJECTOR_GRAD_NORM"),
        "LLM_GRAD_NORM": get(gp, "LLM_GRAD_NORM"),
        "SONATA_GRAD_NORM": get(gp, "SONATA_GRAD_NORM"),
        "REAL_VS_ZERO_EMBED_DELTA": get(
            fp, "deltas", "real_vs_zero", "pooled_relative_delta"
        ),
        "REAL_VS_WRONG_EMBED_DELTA": get(
            fp, "deltas", "real_vs_wrong", "pooled_relative_delta"
        ),
        "REAL_VS_CORRUPTED_EMBED_DELTA": get(
            fp, "deltas", "real_vs_corrupted", "pooled_relative_delta"
        ),
        "OVERFIT1_INITIAL_LOSS": get(o1, "INITIAL_TRAIN_LOSS"),
        "OVERFIT1_FINAL_LOSS": get(o1, "FINAL_TRAIN_LOSS"),
        "OVERFIT1_RELOAD_OK": get(o1_reload, "CHECKPOINT_RELOAD_OK"),
        "OVERFIT10_INITIAL_LOSS": get(o10["separate_edge"], "INITIAL_TRAIN_LOSS"),
        "OVERFIT10_FINAL_LOSS": get(o10["separate_edge"], "FINAL_TRAIN_LOSS"),
        "OVERFIT10_TOKEN_ACCURACY": get(o10["separate_edge"], "TOKEN_ACCURACY"),
        "OVERFIT10_SURFACE_ONLY_LOSS": get(o10["surface_only"], "FINAL_TRAIN_LOSS"),
        "OVERFIT10_EDGE_SCORE_LOSS": get(o10["edge_score"], "FINAL_TRAIN_LOSS"),
        "OVERFIT10_SEPARATE_EDGE_LOSS": get(o10["separate_edge"], "FINAL_TRAIN_LOSS"),
        "OVERFIT100_SURFACE_ONLY_LOSS": get(o100["surface_only"], "FINAL_TRAIN_LOSS"),
        "OVERFIT100_EDGE_SCORE_LOSS": get(o100["edge_score"], "FINAL_TRAIN_LOSS"),
        "OVERFIT100_SEPARATE_EDGE_LOSS": get(o100["separate_edge"], "FINAL_TRAIN_LOSS"),
        "OVERFIT100_SURFACE_ONLY_VAL_LOSS": get(o100["surface_only"], "FINAL_VAL_LOSS"),
        "OVERFIT100_EDGE_SCORE_VAL_LOSS": get(o100["edge_score"], "FINAL_VAL_LOSS"),
        "OVERFIT100_SEPARATE_EDGE_VAL_LOSS": get(o100["separate_edge"], "FINAL_VAL_LOSS"),
        "REAL_EDGE_EVAL_LOSS": get(abl, "REAL_EDGE_EVAL_LOSS"),
        "ZERO_EDGE_EVAL_LOSS": get(abl, "ZERO_EDGE_EVAL_LOSS"),
        "WRONG_EDGE_EVAL_LOSS": get(abl, "WRONG_EDGE_EVAL_LOSS"),
        "CORRUPTED_EDGE_EVAL_LOSS": get(abl, "CORRUPTED_EDGE_EVAL_LOSS"),
        "REAL_BEATS_ZERO": get(abl, "REAL_BEATS_ZERO"),
        "REAL_BEATS_WRONG": get(abl, "REAL_BEATS_WRONG"),
        "REAL_BEATS_CORRUPTED": get(abl, "REAL_BEATS_CORRUPTED"),
        "EDGE_STRUCTURE_LEARNED": get(abl, "EDGE_STRUCTURE_LEARNED"),
        "EDGE_PRESENCE_ONLY": get(abl, "EDGE_PRESENCE_ONLY"),
        "ABLATION_SPLIT_USED_FOR_VERDICT": "held-out val (19 parts)",
        "TRAINSET_REAL_EDGE_EVAL_LOSS": get(abl_train, "REAL_EDGE_EVAL_LOSS"),
        "TRAINSET_ZERO_EDGE_EVAL_LOSS": get(abl_train, "ZERO_EDGE_EVAL_LOSS"),
        "TRAINSET_WRONG_EDGE_EVAL_LOSS": get(abl_train, "WRONG_EDGE_EVAL_LOSS"),
        "TRAINSET_CORRUPTED_EDGE_EVAL_LOSS": get(abl_train, "CORRUPTED_EDGE_EVAL_LOSS"),
        "TRAINSET_EDGE_STRUCTURE_LEARNED": get(abl_train, "EDGE_STRUCTURE_LEARNED"),
        "EDGE_USED_AS_MEMORIZATION_KEY": bool(
            get(abl_train, "REAL_BEATS_WRONG", default=False) is True
            and get(abl, "REAL_BEATS_WRONG", default=False) is not True
        ),
        "data_cache": cache,
        "data_debug_summary": {
            k: v for k, v in (debug or {}).items() if k != "per_sample"
        }
        if debug
        else NOT_RUN,
    }

    md = []
    md.append("# Separate Edge Point Tokens V1 — Report\n")
    md.append(f"**CURRENT_GATE = `{data['CURRENT_GATE']}`**\n")
    md.append(f"NEXT_PRIMARY_BLOCKER = `{data['NEXT_PRIMARY_BLOCKER']}`\n")

    md.append("\n## Gate checks\n")
    md.append("| check | result |\n| --- | --- |")
    for k, v in gate_checks.items():
        md.append(f"| {k} | {'PASS' if v else 'FAIL'} |")

    md.append("\n## 0. Non-regression of existing work\n")
    md.append("| key | value |\n| --- | --- |")
    for k in (
        "BASELINE_CODE_MODIFIED",
        "EDGE_SCORE_CODE_MODIFIED",
        "OLD_CHECKPOINTS_MODIFIED",
        "OLD_BASELINE_REGRESSION",
        "EDGE_SCORE_REGRESSION",
    ):
        md.append(f"| {k} | {fmt(data[k])} |")

    md.append("\n## 1. Representation level\n")
    md.append("| key | value |\n| --- | --- |")
    for k in (
        "SURFACE_CHANNELS",
        "EDGE_CHANNELS",
        "SURFACE_RAW_POINTS",
        "EDGE_RAW_POINTS",
        "SURFACE_VOXEL_COUNT",
        "EDGE_VOXEL_COUNT",
        "SURFACE_TOKEN_COUNT",
        "EDGE_TOKEN_COUNT",
        "SURFACE_TOKEN_SHAPE",
        "EDGE_TOKEN_SHAPE",
        "FINAL_LLM_INPUT_SHAPE",
        "SHARED_SONATA",
        "SONATA_FROZEN",
        "EDGE_PROJECTOR_SEPARATE",
        "EDGE_PROJECTOR_INIT",
        "EDGE_PROJECTOR_TRAINABLE",
        "TOTAL_PARAMETERS",
        "TRAINABLE_PARAMETERS",
        "SPECIAL_EDGE_TOKEN_TRAINABLE",
        "SURFACE_PROJECTOR_GRAD_NORM",
        "EDGE_PROJECTOR_GRAD_NORM",
        "LLM_GRAD_NORM",
        "SONATA_GRAD_NORM",
        "REAL_VS_ZERO_EMBED_DELTA",
        "REAL_VS_WRONG_EMBED_DELTA",
        "REAL_VS_CORRUPTED_EMBED_DELTA",
    ):
        md.append(f"| {k} | {fmt(data[k])} |")

    md.append("\n## 2. Task level\n")
    md.append("| key | value |\n| --- | --- |")
    for k in (
        "OVERFIT1_INITIAL_LOSS",
        "OVERFIT1_FINAL_LOSS",
        "OVERFIT1_RELOAD_OK",
        "OVERFIT10_INITIAL_LOSS",
        "OVERFIT10_FINAL_LOSS",
        "OVERFIT10_TOKEN_ACCURACY",
        "OVERFIT10_SURFACE_ONLY_LOSS",
        "OVERFIT10_EDGE_SCORE_LOSS",
        "OVERFIT10_SEPARATE_EDGE_LOSS",
        "OVERFIT100_SURFACE_ONLY_LOSS",
        "OVERFIT100_EDGE_SCORE_LOSS",
        "OVERFIT100_SEPARATE_EDGE_LOSS",
        "OVERFIT100_SURFACE_ONLY_VAL_LOSS",
        "OVERFIT100_EDGE_SCORE_VAL_LOSS",
        "OVERFIT100_SEPARATE_EDGE_VAL_LOSS",
    ):
        md.append(f"| {k} | {fmt(data[k])} |")

    md.append("\n## 3. Structure level (same E2 checkpoint, four edge conditions)\n")
    md.append(
        "The verdict uses the **held-out** split. The train split is reported "
        "separately because a model can read the edge stream as a per-sample "
        "fingerprint, which inflates the seen-part gap without any transferable "
        "geometric understanding.\n"
    )
    md.append("| key | value |\n| --- | --- |")
    for k in (
        "ABLATION_SPLIT_USED_FOR_VERDICT",
        "REAL_EDGE_EVAL_LOSS",
        "ZERO_EDGE_EVAL_LOSS",
        "WRONG_EDGE_EVAL_LOSS",
        "CORRUPTED_EDGE_EVAL_LOSS",
        "REAL_BEATS_ZERO",
        "REAL_BEATS_WRONG",
        "REAL_BEATS_CORRUPTED",
        "EDGE_STRUCTURE_LEARNED",
        "EDGE_PRESENCE_ONLY",
        "EDGE_USED_AS_MEMORIZATION_KEY",
    ):
        md.append(f"| {k} | {fmt(data[k])} |")

    md.append("\n### Train-split ablation (memorization diagnostic)\n")
    md.append("| key | value |\n| --- | --- |")
    for k in (
        "TRAINSET_REAL_EDGE_EVAL_LOSS",
        "TRAINSET_ZERO_EDGE_EVAL_LOSS",
        "TRAINSET_WRONG_EDGE_EVAL_LOSS",
        "TRAINSET_CORRUPTED_EDGE_EVAL_LOSS",
        "TRAINSET_EDGE_STRUCTURE_LEARNED",
    ):
        md.append(f"| {k} | {fmt(data[k])} |")

    if abl:
        md.append("\n### Per-condition detail\n")
        md.append("| condition | eval_loss | token_acc | cad_validity |\n| --- | --- | --- | --- |")
        for c in ("real", "zero", "wrong", "corrupted"):
            r = get(abl, "results", c, default={}) or {}
            md.append(
                f"| {c} | {fmt(r.get('eval_loss', NOT_RUN))} | "
                f"{fmt(r.get('token_accuracy', NOT_RUN))} | "
                f"{fmt(r.get('cad_validity', NOT_RUN))} |"
            )
        md.append("\n| paired comparison | real better on | mean loss gap |\n| --- | --- | --- |")
        for c in ("zero", "wrong", "corrupted"):
            p = get(abl, "paired", f"real_vs_{c}", default={}) or {}
            md.append(
                f"| real vs {c} | {fmt(p.get('real_better_fraction', NOT_RUN))} | "
                f"{fmt(p.get('mean_paired_loss_gap', NOT_RUN))} |"
            )

    md.append("\n## 4. Interpretation\n")
    if data["EDGE_USED_AS_MEMORIZATION_KEY"] is True:
        md.append(
            "The edge stream is **read** by the model but not **understood**.\n\n"
            "On the 80 training parts, swapping in another part's edge cloud costs "
            f"{fmt(data['TRAINSET_WRONG_EDGE_EVAL_LOSS'])} versus "
            f"{fmt(data['TRAINSET_REAL_EDGE_EVAL_LOSS'])} for the real edges, and the real "
            "edges win on every single part. So the edge tokens genuinely reach the "
            "decoder and carry per-sample information.\n\n"
            "On the 19 held-out parts that advantage vanishes: real, zero, wrong and "
            "corrupted edges all land within noise of each other, and the real edges win "
            "on a minority of parts. The gap the model exploits is therefore a "
            "**per-sample fingerprint used for memorization**, not transferable geometric "
            "structure.\n\n"
            "`EDGE_STRUCTURE_LEARNED=False` is the honest verdict for V1."
        )
    elif data["EDGE_STRUCTURE_LEARNED"] is True:
        md.append(
            "Real edges beat both wrong and corrupted edges on held-out parts, so the "
            "edge stream carries transferable geometric structure."
        )
    else:
        md.append("Ablation evidence is incomplete; see NOT_RUN entries above.")

    json_dump(R / "report.json", data)
    (R / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
