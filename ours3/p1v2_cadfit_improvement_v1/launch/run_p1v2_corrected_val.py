#!/usr/bin/env python3
"""Run P1v2 on the frozen VAL1000 manifest with corrected Fusion coordinates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS = ROOT / "ours3"
MANIFEST = (
    OURS
    / "m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl"
)
DECODER = OURS / "toaster_p1_edge_condition_ablation_v1/scripts/decode_arm_c2_val.py"
EXECUTOR = ROOT / "scripts/deepcad/dsl_to_occ.py"
CADFIT_PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")


def load_decoder():
    import importlib.util

    spec = importlib.util.spec_from_file_location("p1_decode", DECODER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module._setup_paths()
    return module


def fusion_surface(row: dict) -> tuple[np.ndarray, object, Path]:
    from cad_canonical import canonicalize_features, compute_transform

    old_surface = Path(row["surface_path"])
    source_path = old_surface.parent / "surface_points_source.npy"
    source_xyz = np.load(source_path).astype(np.float32)[:, :3]
    old_features = np.load(old_surface).astype(np.float32)
    features = np.concatenate([source_xyz, old_features[:, 3:6]], axis=1)
    transform = compute_transform(source_xyz, target_diagonal=6.0)
    corrected = canonicalize_features(features, transform).astype(np.float32)
    diagonal = float(np.linalg.norm(np.ptp(corrected[:, :3], axis=0)))
    if corrected.shape != (8192, 6) or not np.isfinite(corrected).all():
        raise ValueError(f"invalid corrected Fusion features: {corrected.shape}")
    if not 5.999 < diagonal < 6.001:
        raise ValueError(f"corrected Fusion diagonal is {diagonal}")
    return corrected, transform, source_path


def op_f1(gt: list[str], pred: list[str]) -> float:
    if not gt and not pred:
        return 1.0
    common = sum((Counter(gt) & Counter(pred)).values())
    if not common:
        return 0.0
    precision = common / max(len(pred), 1)
    recall = common / max(len(gt), 1)
    return 2 * precision * recall / (precision + recall)


def execute_step(code: str, out_dir: Path, timeout: int = 120) -> dict:
    from edge_aware_cad_planner_v1.cad_dsl import parse_dsl

    dsl = out_dir / "pred.dsl"
    step = out_dir / "pred.step"
    stl = out_dir / "pred.stl"
    dsl.write_text(code if code.endswith("\n") else code + "\n")
    try:
        parse_dsl(code)
    except Exception as exc:
        return {"parsed": False, "step_ok": False, "error": f"parse: {exc}"}
    try:
        proc = subprocess.run(
            [
                str(CADFIT_PYTHON),
                str(EXECUTOR),
                "--dsl",
                str(dsl),
                "--step",
                str(step),
                "--stl",
                str(stl),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"parsed": True, "step_ok": False, "error": f"step_timeout_{timeout}s"}
    ok = proc.returncode == 0 and step.is_file() and step.stat().st_size > 0
    return {
        "parsed": True,
        "step_ok": ok,
        "step": str(step) if ok else None,
        "stl": str(stl) if stl.is_file() else None,
        "error": None if ok else (proc.stderr or proc.stdout)[-1000:],
    }


def summarize(rows: list[dict], checkpoint: Path) -> dict:
    def block(part: list[dict]) -> dict:
        n = len(part)
        return {
            "N": n,
            "parse_valid_N": sum(x["parsed"] for x in part),
            "step_valid_N": sum(x["step_ok"] for x in part),
            "step_valid_rate": sum(x["step_ok"] for x in part) / n if n else None,
            "max_length_N": sum(x["stop_reason"] == "MAX_LENGTH" for x in part),
            "max_length_rate": sum(x["stop_reason"] == "MAX_LENGTH" for x in part) / n if n else None,
            "mean_op_f1": (
                float(np.mean([x["op_f1"] for x in part if x["op_f1"] is not None]))
                if any(x["op_f1"] is not None for x in part)
                else None
            ),
        }

    return {
        "schema_version": "P1V2_CORRECTED_VAL_GENERATION_V1",
        "checkpoint": str(checkpoint),
        "selection_rule": "lowest training-time dev eval_loss only",
        "fusion_coordinate_fix": "source_points bbox -> diagonal 6 input; same transform inverse for output",
        "all": block(rows),
        "by_dataset": {
            name: block([x for x in rows if x["dataset"] == name])
            for name in ("deepcad", "fusion360")
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--ids-json", type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--num-shards", type=int)
    parser.add_argument("--subshard-index", type=int)
    parser.add_argument("--num-subshards", type=int)
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    all_rows = [json.loads(line) for line in MANIFEST.read_text().splitlines() if line.strip()]
    if args.ids_json:
        selected = json.loads(args.ids_json.read_text())
        wanted = {x["id"] if isinstance(x, dict) else x for x in selected}
        all_rows = [x for x in all_rows if x["cad_id"] in wanted]
    if args.limit is not None:
        all_rows = all_rows[: args.limit]
    if (args.shard_index is None) != (args.num_shards is None):
        parser.error("--shard-index and --num-shards must be used together")
    if args.num_shards is not None:
        if not 0 <= args.shard_index < args.num_shards:
            parser.error("shard index is out of range")
        all_rows = [
            row for index, row in enumerate(all_rows)
            if index % args.num_shards == args.shard_index
        ]
    if (args.subshard_index is None) != (args.num_subshards is None):
        parser.error("--subshard-index and --num-subshards must be used together")
    if args.num_subshards is not None:
        if not 0 <= args.subshard_index < args.num_subshards:
            parser.error("subshard index is out of range")
        all_rows = [
            row for index, row in enumerate(all_rows)
            if index % args.num_subshards == args.subshard_index
        ]
    args.out.mkdir(parents=True, exist_ok=True)

    decoder = load_decoder()
    model, tokenizer = decoder._load_j2_curve(args.checkpoint, torch.bfloat16)
    from separate_edge_tokens_v1.common import make_plugin
    from geometry_pack_v1.decode_joint_j0_j2 import generate_dsl
    from decode_eval_split import _op_multiset, _solid_op_count
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code
    from cad_canonical import transform_dsl

    plugin = make_plugin(separate_edge=True)
    results = []
    for index, row in enumerate(all_rows, 1):
        case_id = row["cad_id"]
        dataset = row["source"].lower()
        case_out = args.out / case_id
        result_path = case_out / "row.json"
        if args.resume and result_path.is_file():
            results.append(json.loads(result_path.read_text()))
            print(f"[{index}/{len(all_rows)}] {case_id} resume", flush=True)
            continue
        case_out.mkdir(parents=True, exist_ok=True)

        transform = None
        source_points = None
        if dataset == "fusion360":
            raw_surface, transform, source_points = fusion_surface(row)
            (case_out / "coordinate_transform_recomputed.json").write_text(
                json.dumps(transform.to_json(), indent=2) + "\n"
            )
        else:
            raw_surface = np.load(row["surface_path"]).astype(np.float32)
        grid, xyz, normal, _ = plugin._voxelize_6ch(raw_surface.astype(np.float64))
        surface = np.concatenate([grid.astype(np.float32), xyz, normal], axis=1)
        curves = np.load(row["curve_token_path"]).astype(np.float32)
        if not len(curves):
            curves = np.zeros((1, 256), dtype=np.float32)
        curves = curves[:128]

        pred, meta = generate_dsl(
            model,
            tokenizer,
            torch.as_tensor(surface[None], dtype=torch.float32),
            torch.as_tensor(curves[None], dtype=torch.float32),
            separate_edge=True,
            max_new_tokens=args.max_new_tokens,
        )
        (case_out / "pred.txt").write_text(pred if pred.endswith("\n") else pred + "\n")
        (case_out / "generation_meta.json").write_text(json.dumps(meta, indent=2) + "\n")
        try:
            canonical = extract_dsl_code(pred)
        except Exception:
            canonical = pred
        (case_out / "pred_canonical.dsl").write_text(
            canonical if canonical.endswith("\n") else canonical + "\n"
        )

        execution_code = canonical
        transform_error = ""
        if transform is not None:
            try:
                execution_code = transform_dsl(canonical, transform, inverse=True)
                (case_out / "pred_source.dsl").write_text(
                    execution_code if execution_code.endswith("\n") else execution_code + "\n"
                )
            except Exception as exc:
                transform_error = f"{type(exc).__name__}: {exc}"
        execution = (
            execute_step(execution_code, case_out)
            if not transform_error
            else {"parsed": False, "step_ok": False, "error": transform_error}
        )

        gt_program = Path(row["gt_program_path"])
        gt_available = gt_program.is_file()
        gt_text = gt_program.read_text(errors="replace") if gt_available else ""
        gt_ops = _op_multiset(gt_text) if gt_available else []
        pred_ops = _op_multiset(canonical)
        result = {
            "id": case_id,
            "dataset": dataset,
            "checkpoint": str(args.checkpoint),
            "surface_path_manifest": row["surface_path"],
            "surface_input_policy": "corrected_from_source_points" if transform else "manifest_canonical",
            "source_points": str(source_points) if source_points else None,
            "curve_token_path": row["curve_token_path"],
            "prediction_tokens": meta.get("prediction_tokens", meta.get("num_generated_tokens")),
            "stop_reason": meta.get("stop_reason"),
            "gt_ops": gt_ops,
            "gt_program_available": gt_available,
            "pred_ops": pred_ops,
            "gt_op_count": _solid_op_count(gt_text) if gt_available else None,
            "predicted_op_count": _solid_op_count(canonical),
            "op_f1": op_f1(gt_ops, pred_ops) if gt_available else None,
            "parsed": bool(execution.get("parsed")),
            "step_ok": bool(execution.get("step_ok")),
            "step": execution.get("step"),
            "stl": execution.get("stl"),
            "error": execution.get("error"),
        }
        result_path.write_text(json.dumps(result, indent=2) + "\n")
        results.append(result)
        print(
            f"[{index}/{len(all_rows)}] {case_id} step={result['step_ok']} "
            f"stop={result['stop_reason']} op_f1={result['op_f1']}",
            flush=True,
        )

    report = summarize(results, args.checkpoint)
    suffix = f"_shard{args.shard_index}" if args.shard_index is not None else ""
    if args.subshard_index is not None:
        suffix += f"_subshard{args.subshard_index}"
    (args.out / f"report{suffix}.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.out / f"rows{suffix}.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
