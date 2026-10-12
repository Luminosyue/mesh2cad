#!/usr/bin/env python3
"""Decode overfit10 checkpoints: generate DSL, execute to STEP, compare vs GT."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = ROOT / "SpatialLM"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(SPATIALLM_ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""


def _load_model(checkpoint: Path, use_edge: bool, dtype: torch.dtype, device: str):
    import spatiallm  # noqa: F401
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from spatiallm_cad_frontend import load_spatiallm_with_edge_channel, preprocess_cad_point_cloud

    if use_edge:
        model = load_spatiallm_with_edge_channel(checkpoint, device=device, dtype=dtype)
    else:
        model = AutoModelForCausalLM.from_pretrained(str(checkpoint), torch_dtype=dtype)
        model.to(device)
        model.set_point_backbone_dtype(torch.float32)
        model.eval()
    tokenizer = AutoTokenizer.from_pretrained(str(checkpoint))
    return model, tokenizer, preprocess_cad_point_cloud


def _build_tensor(features_path: Path, preprocess_fn, use_edge: bool):
    feats = np.load(features_path)
    points, normals = feats[:, :3], feats[:, 3:6]
    edge = feats[:, 6] if feats.shape[1] >= 7 else np.zeros(len(feats))
    if not use_edge:
        edge = np.zeros_like(edge)
    already_canonical = "canonical" in features_path.name
    part = preprocess_fn(points, normals, edge, already_canonical=already_canonical)
    tensor = part.tensor
    if not use_edge:
        tensor = tensor[..., :9]
    return tensor


def _generation_stop_reason(
    generated_ids,
    prompt_len: int,
    max_new_tokens: int,
    eos_token_id: int | None,
) -> tuple[int, str]:
    new_ids = generated_ids[prompt_len:]
    prediction_tokens = int(len(new_ids))
    if prediction_tokens >= max_new_tokens:
        return prediction_tokens, "MAX_LENGTH"
    if eos_token_id is not None and len(new_ids) > 0 and int(new_ids[-1]) == int(eos_token_id):
        return prediction_tokens, "EOS"
    return prediction_tokens, "EOS"


@torch.inference_mode()
def generate_dsl(
    model,
    tokenizer,
    point_tensor,
    temperature: float = 0.0,
    max_new_tokens: int = 2048,
    return_meta: bool = False,
) -> str | tuple[str, dict]:
    prompt = f"<|point_start|><|point_pad|><|point_end|>\n{CAD_INSTRUCTION.strip()}"
    conversation = [{"role": "user", "content": prompt}]
    input_ids = tokenizer.apply_chat_template(
        conversation, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)
    prompt_len = int(input_ids.shape[1])
    kwargs = dict(
        input_ids=input_ids,
        point_clouds=point_tensor.to(model.device),
        max_new_tokens=max_new_tokens,
        do_sample=temperature > 0,
        use_cache=True,
        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id,
    )
    if temperature > 0:
        kwargs.update(temperature=temperature, top_p=0.95, top_k=10)
    out = model.generate(**kwargs)
    pred_ids = out[0]
    text = tokenizer.decode(pred_ids[prompt_len:], skip_special_tokens=True)
    if not return_meta:
        return text
    n_tok, stop_reason = _generation_stop_reason(
        pred_ids.tolist(),
        prompt_len,
        max_new_tokens,
        tokenizer.eos_token_id,
    )
    return text, {
        "max_new_tokens": max_new_tokens,
        "prediction_tokens": n_tok,
        "stop_reason": stop_reason,
    }


def _normalize_dsl(text: str) -> str:
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code

    try:
        code = extract_dsl_code(text)
    except Exception:
        code = text
    lines = [ln.rstrip() for ln in code.strip().splitlines() if ln.strip() and not ln.strip().startswith("#")]
    return "\n".join(lines).strip() + "\n"


def _exec_dsl(raw_text: str, out_dir: Path) -> dict:
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code, parse_dsl

    rec = {"raw": raw_text}
    try:
        code = extract_dsl_code(raw_text)
        parse_dsl(code)
        rec["parsed"] = True
        rec["dsl"] = code
    except Exception as exc:
        rec["parsed"] = False
        rec["step_ok"] = False
        rec["error"] = f"parse_failed: {exc}"
        return rec

    step = out_dir / "pred.step"
    stl = out_dir / "pred.stl"
    dsl_path = out_dir / "pred.dsl"
    dsl_path.write_text(code if code.endswith("\n") else code + "\n", encoding="utf-8")

    # Prefer in-process execute; fall back to cadfit-env subprocess (has cadquery).
    try:
        from edge_aware_cad_planner_v1.cad_dsl import execute_dsl

        execute_dsl(code, step, stl)
    except Exception as exc:
        import subprocess

        py = Path("/data/miniconda3/envs/cadfit-env/bin/python")
        script = ROOT / "scripts" / "deepcad" / "dsl_to_occ.py"
        if py.exists() and script.exists():
            proc = subprocess.run(
                [str(py), str(script), "--dsl", str(dsl_path), "--step", str(step), "--stl", str(stl)],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                rec["step_ok"] = False
                rec["error"] = (proc.stderr or proc.stdout or str(exc)).strip()[-500:]
                return rec
        else:
            rec["step_ok"] = False
            rec["error"] = str(exc)
            return rec

    rec["step_ok"] = step.exists() and step.stat().st_size > 0
    rec["step"] = str(step)
    return rec


def _op_tokens(dsl_text: str) -> set[str]:
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code, parse_dsl

    try:
        prog = parse_dsl(extract_dsl_code(dsl_text))
        return {v["op"] for v in prog.assignments.values() if isinstance(v, dict) and "op" in v}
    except Exception:
        return set()


def main() -> int:
    parser = argparse.ArgumentParser(description="Decode overfit10 CAD DSL checkpoint")
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--train-json", type=Path, default=None)
    parser.add_argument("--media-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD")
    parser.add_argument("--use-edge", action="store_true")
    parser.add_argument("--variant", choices=("ours", "baseline"), default="ours")
    parser.add_argument("--out", type=Path, default=ROOT / "ours3/deepcad_overfit10_decode")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float32"])
    args = parser.parse_args()

    use_edge = args.use_edge or args.variant == "ours"
    if args.train_json is None:
        name = (
            "deepcad_cad_ours_overfit10_train.json"
            if args.variant == "ours"
            else "deepcad_cad_baseline_overfit10_train.json"
        )
        args.train_json = ROOT / "cad_spatial_dataset" / "DeepCAD" / name

    records = json.loads(args.train_json.read_text(encoding="utf-8"))
    out_root = args.out / args.variant / args.checkpoint.name
    out_root.mkdir(parents=True, exist_ok=True)

    model, tokenizer, preprocess_fn = _load_model(
        args.checkpoint, use_edge, getattr(torch, args.dtype), "cuda"
    )

    summary = []
    exact_n = 0
    for rec in records:
        sid = rec["id"]
        pc_rel = rec["point_clouds"][0]
        features_path = args.media_dir / pc_rel
        gt_dsl = rec["conversations"][1]["value"]
        sample_out = out_root / sid
        sample_out.mkdir(parents=True, exist_ok=True)

        tensor = _build_tensor(features_path, preprocess_fn, use_edge)
        pred_text = generate_dsl(model, tokenizer, tensor, temperature=args.temperature)
        (sample_out / "pred.txt").write_text(pred_text, encoding="utf-8")
        (sample_out / "gt.dsl").write_text(gt_dsl, encoding="utf-8")

        exec_rec = _exec_dsl(pred_text, sample_out)
        gt_ops = _op_tokens(gt_dsl)
        pred_ops = _op_tokens(pred_text)
        exact = _normalize_dsl(pred_text) == _normalize_dsl(gt_dsl)
        exact_n += int(exact)
        row = {
            "sample_id": sid,
            "gt_ops": sorted(gt_ops),
            "pred_ops": sorted(pred_ops),
            "op_recall": len(gt_ops & pred_ops) / len(gt_ops) if gt_ops else 0.0,
            "exact_match": exact,
            **exec_rec,
        }
        summary.append(row)
        print(
            f"{sid}: exact={exact} parsed={row.get('parsed')} step_ok={row.get('step_ok')} "
            f"op_recall={row['op_recall']:.2f} gt={gt_ops} pred={pred_ops}"
        )

    report = {
        "checkpoint": str(args.checkpoint),
        "variant": args.variant,
        "use_edge": use_edge,
        "n_samples": len(summary),
        "exact_match_rate": exact_n / max(len(summary), 1),
        "exact_match_n": exact_n,
        "step_valid_rate": sum(1 for r in summary if r.get("step_ok")) / max(len(summary), 1),
        "mean_op_recall": float(np.mean([r["op_recall"] for r in summary])) if summary else 0.0,
        "samples": summary,
    }
    (out_root / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
