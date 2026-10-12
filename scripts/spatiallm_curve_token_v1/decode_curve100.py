#!/usr/bin/env python3
"""Decode + evaluate curve100 overfit probe: B0 / B1 / M2.

Same 100 CADs the arms overfit on. Metrics match joint J0/J2 decode:
exact match, op F1/recall, pred/gt op ratio, STEP valid, Chamfer.

M2 reuses B1's second-stream slot; runtime patches from
``curve_token_injector`` swap the payload to frozen Curve Tokens.
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
SPATIALLM_ROOT = REPO_ROOT / "SpatialLM"
for p in (
    str(SPATIALLM_ROOT),
    str(REPO_ROOT / "scripts"),
    str(REPO_ROOT / "scripts" / "deepcad"),
    str(REPO_ROOT / "scripts" / "geometry_pack_v1"),
    str(REPO_ROOT / "scripts" / "separate_edge_tokens_v1"),
):
    if p not in sys.path:
        sys.path.insert(0, p)

from decode_joint_j0_j2 import (  # noqa: E402
    _evaluate_one,
    _generation_stop_reason,
    _load_sepedge,
    _load_surface_only,
    _summarize,
)
from separate_edge_tokens_v1.common import (  # noqa: E402
    build_prompt,
    load_model,
    make_plugin,
    set_deterministic_serialization,
)

from spatiallm_curve_token_v1.config import (  # noqa: E402
    CURVE_TOKEN_DIM,
    OUTPUT_ROOT,
    SUBSET_DIR,
)
from spatiallm_curve_token_v1.curve_projector import build_curve_projector  # noqa: E402

ARM_CKPT = {
    "B0": SPATIALLM_ROOT / "saves" / "curve100_b0_surface",
    "B1": SPATIALLM_ROOT / "saves" / "curve100_b1_edgepoints",
    "M2": SPATIALLM_ROOT / "saves" / "curve100_m2_curvetoken",
}
MEDIA_DEFAULT = REPO_ROOT / "cad_spatial_dataset"


def _configure_env(arm: str) -> None:
    os.environ.pop("CAD_USE_EDGE_SCORE", None)
    if arm == "B0":
        os.environ.pop("CAD_USE_SEPARATE_EDGE_TOKENS", None)
        os.environ.pop("CAD_SECOND_STREAM", None)
        os.environ.pop("CAD_EDGE_SOURCE", None)
    elif arm == "B1":
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
        os.environ["CAD_SECOND_STREAM"] = "edge_points"
        os.environ["CAD_EDGE_SOURCE"] = "gt_sharp"
    elif arm == "M2":
        os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
        os.environ["CAD_SECOND_STREAM"] = "curve_tokens"
        os.environ.pop("CAD_EDGE_SOURCE", None)
    else:
        raise ValueError(arm)


def _load_m2_checkpoint(checkpoint: Path, device: str, dtype: torch.dtype):
    """Load M2: CurveProjector occupies ``edge_proj``; patch forward_geometry."""
    from spatiallm_curve_token_v1 import curve_token_injector

    curve_token_injector.install()
    import spatiallm  # noqa: F401
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from spatiallm.tuner.framework import patcher as sp_patcher

    # Build skeleton with CurveProjector BEFORE weight load so key names match
    # ``edge_proj.net.*`` (Sequential B1 uses ``edge_proj.0.*``).
    model = AutoModelForCausalLM.from_pretrained(
        str(SPATIALLM_ROOT / "models" / "SpatialLM1.1-Llama-1B"),
        torch_dtype=dtype,
    )
    sp_patcher._attach_edge_projector(model)
    # Load finetuned weights (LLM + point_proj + CurveProjector)
    state = {}
    index = checkpoint / "model.safetensors.index.json"
    if index.is_file():
        from safetensors.torch import load_file

        meta = json.loads(index.read_text(encoding="utf-8"))
        for shard in sorted(set(meta["weight_map"].values())):
            state.update(load_file(str(checkpoint / shard)))
    else:
        from safetensors.torch import load_file

        state = load_file(str(checkpoint / "model.safetensors"))
    missing, unexpected = model.load_state_dict(state, strict=False)
    # Tolerate tokenizer / unused buffers; fail hard if edge_proj absent.
    bad_missing = [k for k in missing if k.startswith("edge_proj.")]
    if bad_missing:
        raise RuntimeError(f"M2 checkpoint missing CurveProjector weights: {bad_missing[:8]}")
    type(model).forward_geometry = curve_token_injector._forward_geometry_with_curve_tokens
    model.config.curve_token_stream = True
    model.config.curve_token_dim = CURVE_TOKEN_DIM
    model.config.separate_edge_tokens = True
    model.separate_edge_tokens = True
    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    for p in model.point_backbone.parameters():
        p.requires_grad_(False)
    tokenizer = AutoTokenizer.from_pretrained(str(checkpoint))
    print(
        f"[decode] M2 loaded: edge_proj={type(model.edge_proj).__name__} "
        f"unexpected={len(unexpected)} missing_non_edge={len(missing)-len(bad_missing)}",
        flush=True,
    )
    return model, tokenizer


@torch.inference_mode()
def generate_dsl(model, tokenizer, surface, edge, separate_edge: bool, max_new_tokens: int):
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arm", choices=("B0", "B1", "M2"), required=True)
    ap.add_argument("--checkpoint", type=Path, default=None)
    ap.add_argument(
        "--split-json",
        type=Path,
        default=SUBSET_DIR / "curve100_train.json",
        help="Overfit probe: train == eval == these 100 CADs",
    )
    ap.add_argument("--media-dir", type=Path, default=MEDIA_DEFAULT)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dtype", default="bfloat16", choices=("bfloat16", "float32"))
    ap.add_argument(
        "--max-new-tokens",
        type=int,
        default=4096,
        help="Generation budget (main eval uses 4096; 2048 kept as appendix).",
    )
    ap.add_argument(
        "--gt-len-exclude-above",
        type=int,
        default=2048,
        help="Also write report excluding samples with GT CAD tokens > this "
        "(separates length-cap failures from content failures). 0 disables.",
    )
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    _configure_env(args.arm)
    ckpt = args.checkpoint or ARM_CKPT[args.arm]
    out = args.out or (OUTPUT_ROOT / "decode" / args.arm.lower())
    out.mkdir(parents=True, exist_ok=True)

    separate_edge = args.arm in ("B1", "M2")
    if args.arm == "M2":
        from spatiallm_curve_token_v1 import curve_token_injector

        curve_token_injector.install()

    records = json.loads(args.split_json.read_text(encoding="utf-8"))
    records = records[args.offset :]
    if args.limit is not None:
        records = records[: args.limit]

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
            print(f"[resume] {sid}", flush=True)
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
        gt_cad_tokens = int(
            len(tokenizer(gt_text, add_special_tokens=False)["input_ids"])
        )
        row["gt_cad_tokens"] = gt_cad_tokens
        row["gt_fits_in_2048"] = gt_cad_tokens <= 2048
        row["arm"] = args.arm
        row["edge_condition"] = {"B0": "none", "B1": "edge_points", "M2": "curve_tokens"}[
            args.arm
        ]
        row_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        rows.append(row)

        ratio = row.get("predicted_op_count_over_gt_op_count")
        ratio_s = f"{ratio:.2f}" if ratio is not None else "n/a"
        print(
            f"[{args.arm}] {sid}: exact={row['exact_match']} "
            f"parsed={row.get('parsed')} step={row.get('step_ok')} "
            f"op_f1={row['op_f1']:.2f} pred/gt={row['predicted_op_count']}/"
            f"{row['gt_op_count']}={ratio_s} stop={row.get('stop_reason')} "
            f"gt_tok={gt_cad_tokens} "
            f"chamfer={row.get('geometry', {}).get('chamfer_norm')}",
            flush=True,
        )

        if (i + 1) % 10 == 0 or (i + 1) == len(records):
            _write_reports(
                out,
                rows,
                {
                    "arm": args.arm,
                    "checkpoint": str(ckpt),
                    "split": str(args.split_json),
                    "max_new_tokens": args.max_new_tokens,
                    "n_done": len(rows),
                },
                args.gt_len_exclude_above,
            )

    report, report_filt = _write_reports(
        out,
        rows,
        {
            "arm": args.arm,
            "checkpoint": str(ckpt),
            "split": str(args.split_json),
            "max_new_tokens": args.max_new_tokens,
        },
        args.gt_len_exclude_above,
    )
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    if report_filt is not None:
        print(
            json.dumps(
                {k: v for k, v in report_filt.items() if k != "samples"},
                indent=2,
            )
        )
    return 0


def _write_reports(
    out: Path,
    rows: list[dict],
    meta: dict,
    gt_len_exclude_above: int,
) -> tuple[dict, dict | None]:
    report = _summarize(rows, meta)
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    report_filt = None
    if gt_len_exclude_above and gt_len_exclude_above > 0:
        kept = [
            r
            for r in rows
            if int(r.get("gt_cad_tokens", 0)) <= gt_len_exclude_above
        ]
        report_filt = _summarize(
            kept,
            {
                **meta,
                "subset": f"gt_cad_tokens<={gt_len_exclude_above}",
                "excluded_gt_above": gt_len_exclude_above,
                "n_excluded": len(rows) - len(kept),
            },
        )
        (out / f"report_gt_le{gt_len_exclude_above}.json").write_text(
            json.dumps(report_filt, indent=2) + "\n", encoding="utf-8"
        )
    return report, report_filt


if __name__ == "__main__":
    raise SystemExit(main())
