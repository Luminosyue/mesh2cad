#!/usr/bin/env python3
"""Decode one ablation arm (A/B/C/D) into the new toaster tree only."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

REPO = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = REPO / "ours3" / "toaster_p1_edge_condition_ablation_v1"
P1_ROOT = REPO / "ours3" / "p1_operation_aware_structure_loss_v1" / "runs" / "p1"
CKPT = {
    "A": P1_ROOT / "checkpoint-8000",
    "B": P1_ROOT / "checkpoint-8000",
    "C": P1_ROOT / "checkpoint-39980",
    "D": P1_ROOT / "checkpoint-39980",
    "E": P1_ROOT / "checkpoint-39980",
}
EDGE_NONE = {"A", "C"}
PARTS = [f"PART_{i:03d}" for i in range(39)]


def _setup_paths() -> None:
    for p in (
        str(REPO / "SpatialLM"),
        str(REPO / "scripts"),
        str(REPO / "scripts" / "deepcad"),
        str(REPO / "scripts" / "geometry_pack_v1"),
        str(REPO / "scripts" / "separate_edge_tokens_v1"),
    ):
        if p not in sys.path:
            sys.path.insert(0, p)


def _load_j0(checkpoint: Path, dtype: torch.dtype):
    from separate_edge_tokens_v1.common import load_model, set_deterministic_serialization

    model, tokenizer = load_model(
        checkpoint, separate_edge=False, device="cuda", dtype=dtype, freeze_sonata=True
    )
    set_deterministic_serialization(model.point_backbone)
    model.eval()
    return model, tokenizer


def _load_j2_curve(checkpoint: Path, dtype: torch.dtype):
    os.environ["CAD_USE_SEPARATE_EDGE_TOKENS"] = "1"
    os.environ["CAD_SECOND_STREAM"] = "curve_tokens"
    os.environ.pop("CAD_EDGE_SOURCE", None)
    from spatiallm_curve_token_v1 import curve_token_injector
    curve_token_injector.install()
    import spatiallm  # noqa: F401
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer
    from transformers.modeling_utils import load_sharded_checkpoint
    from spatiallm.tuner.framework.patcher import _attach_edge_projector
    from separate_edge_tokens_v1.common import set_deterministic_serialization
    model = AutoModelForCausalLM.from_config(
        AutoConfig.from_pretrained(str(checkpoint)), torch_dtype=dtype
    )
    _attach_edge_projector(model)
    incompatible = load_sharded_checkpoint(model, str(checkpoint), strict=False, prefer_safe=True)
    alias = (list(incompatible.missing_keys) == ["lm_head.weight"]
             and model.config.tie_word_embeddings
             and model.lm_head.weight.data_ptr() == model.model.embed_tokens.weight.data_ptr())
    if (incompatible.missing_keys and not alias) or incompatible.unexpected_keys:
        raise RuntimeError(f"checkpoint/interface mismatch: {incompatible}")
    model.to("cuda")
    model.set_point_backbone_dtype(torch.float32)
    for parameter in model.point_backbone.parameters():
        parameter.requires_grad_(False)
    set_deterministic_serialization(model.point_backbone)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(str(checkpoint))
    return model, tokenizer


def _surface_j0(plugin, npy: Path) -> torch.Tensor:
    feats = plugin._load_cad_npy(str(npy))
    return torch.as_tensor(feats[None, ...], dtype=torch.float32)


def _surface_and_curves(plugin, npy: Path, tokens: np.ndarray) -> tuple[torch.Tensor, torch.Tensor]:
    surface = np.load(npy).astype(np.float64)
    grid, xyz, normal, _ = plugin._voxelize_6ch(surface)
    surface_features = np.concatenate([grid.astype(np.float32), xyz, normal], axis=1)
    if tokens.ndim != 2 or tokens.shape[1] != 256:
        raise ValueError(f"curve tokens must be (K,256), got {tokens.shape}")
    tokens = tokens[:128] if len(tokens) else np.zeros((1, 256), dtype=np.float32)
    return (torch.as_tensor(surface_features[None], dtype=torch.float32),
            torch.as_tensor(tokens[None], dtype=torch.float32))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=("A", "B", "C", "D", "E"))
    ap.add_argument("--max-new-tokens", type=int, default=4096)
    ap.add_argument("--dtype", default="bfloat16")
    args = ap.parse_args()
    _setup_paths()

    arm = args.arm
    ckpt = CKPT[arm]
    edge_none = arm in EDGE_NONE
    dtype = getattr(torch, args.dtype)
    out_arm = OUT / "predictions" / arm
    out_arm.mkdir(parents=True, exist_ok=True)

    if edge_none:
        os.environ.pop("CAD_USE_SEPARATE_EDGE_TOKENS", None)
        os.environ.pop("CAD_SECOND_STREAM", None)
        model, tokenizer = _load_j0(ckpt, dtype)
        from separate_edge_tokens_v1.common import make_plugin

        plugin = make_plugin(separate_edge=False)
    else:
        model, tokenizer = _load_j2_curve(ckpt, dtype)
        from separate_edge_tokens_v1.common import make_plugin

        plugin = make_plugin(separate_edge=True)

    from geometry_pack_v1.decode_joint_j0_j2 import generate_dsl
    from decode_eval_split import _exec_step, _solid_op_count, _op_multiset
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code
    from cad_canonical import CoordinateTransform, transform_dsl

    rows = []
    for part_id in PARTS:
        pack = OUT / ("packs_dora" if arm == "E" else "packs") / part_id
        sample_out = out_arm / part_id
        sample_out.mkdir(parents=True, exist_ok=True)
        row_path = sample_out / "row.json"
        if row_path.is_file():
            row = json.loads(row_path.read_text())
            rows.append(row)
            print(f"[{arm}] {part_id} resume", flush=True)
            continue
        npy = pack / "surface_points.npy"
        tokens_path = pack / "curve_tokens.npy"
        n_curve_in = int(np.load(tokens_path).shape[0]) if tokens_path.is_file() else 0
        empty_fb = json.loads((pack / "prepare_summary.json").read_text()).get("empty_sharp_fallback")

        if edge_none:
            surface = _surface_j0(plugin, npy)
            edge = None
            separate = False
            edge_condition = "none"
        else:
            tokens = np.load(tokens_path).astype(np.float32)
            surface, edge = _surface_and_curves(plugin, npy, tokens)
            separate = True
            edge_condition = "Dora-SES-C2" if arm == "E" else "mesh-dihedral-C2"

        pred, gen_meta = generate_dsl(
            model,
            tokenizer,
            surface,
            edge,
            separate_edge=separate,
            max_new_tokens=args.max_new_tokens,
        )
        (sample_out / "pred.txt").write_text(pred if pred.endswith("\n") else pred + "\n")
        (sample_out / "generation_meta.json").write_text(json.dumps(gen_meta, indent=2) + "\n")
        try:
            code = extract_dsl_code(pred)
        except Exception:
            code = pred
        (sample_out / "pred_canonical.dsl").write_text(
            code if code.endswith("\n") else code + "\n"
        )
        local_exec = _exec_step(code, sample_out)

        tf = CoordinateTransform.from_json(
            json.loads((pack / "coordinate_transform.json").read_text())
        )
        inv_ok = False
        global_exec = {"parsed": False, "step_ok": False}
        try:
            src_dsl = transform_dsl(code, tf, inverse=True)
            (sample_out / "pred_global.dsl").write_text(
                src_dsl if src_dsl.endswith("\n") else src_dsl + "\n"
            )
            glob_dir = sample_out / "global"
            global_exec = _exec_step(src_dsl, glob_dir)
            inv_ok = True
        except Exception as exc:
            (sample_out / "inverse_transform_error.txt").write_text(str(exc))

        ops = _op_multiset(pred)
        row = {
            "part_id": part_id,
            "arm": arm,
            "checkpoint": str(ckpt),
            "edge_condition": edge_condition,
            "n_curve_tokens": n_curve_in if not edge_none else 0,
            "empty_sharp_fallback": empty_fb if not edge_none else None,
            "pred_ops": ops,
            "predicted_op_count": _solid_op_count(pred),
            "prediction_tokens": gen_meta.get("prediction_tokens"),
            "stop_reason": gen_meta.get("stop_reason"),
            "program_length": len(pred),
            "parsed": bool(local_exec.get("parsed")),
            "step_ok_local": bool(local_exec.get("step_ok")),
            "step_ok_global": bool(global_exec.get("step_ok")),
            "inverse_transform_pass": inv_ok,
            "local_step": local_exec.get("step"),
            "local_stl": local_exec.get("stl"),
            "global_step": global_exec.get("step"),
            "global_stl": global_exec.get("stl"),
            "error": local_exec.get("error") or global_exec.get("error"),
        }
        (sample_out / "row.json").write_text(json.dumps(row, indent=2) + "\n")
        rows.append(row)
        print(
            f"[{arm}] {part_id} parsed={row['parsed']} local={row['step_ok_local']} "
            f"global={row['step_ok_global']} ops={row['predicted_op_count']} "
            f"tok={row['prediction_tokens']} stop={row['stop_reason']} "
            f"K={row['n_curve_tokens']}",
            flush=True,
        )

    report = {
        "arm": arm,
        "checkpoint": str(ckpt),
        "edge_none": edge_none,
        "n": len(rows),
        "samples": rows,
    }
    (out_arm / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
