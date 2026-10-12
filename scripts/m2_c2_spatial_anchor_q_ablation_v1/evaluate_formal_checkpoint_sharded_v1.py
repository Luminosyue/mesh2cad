#!/usr/bin/env python3
"""Evaluate one frozen formal checkpoint on decode-dev50 only."""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import math
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [
    str(ROOT / "scripts/m2_c2_spatial_anchor_q_ablation_v1"),
    str(ROOT / "scripts/spatiallm_geometry_prefix_v3"),
    str(ROOT / "scripts/spatiallm_m2_spatial_anchor_v1"),
    str(ROOT / "scripts"),
    str(ROOT / "SpatialLM"),
    str(ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code"),
]

from geometry_prefix_adapter import GeometryPrefixAdapter
from spatiallm_m2_spatial_anchor_v1.m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1
from run_four_arm_100step_impl import ARMS, encode, install_geometry, load_anchor, load_raw, v3

DEV = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_decode_dev_50.json"
EXECUTOR = ROOT / "scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py"
EXECUTOR_SHA256 = "53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de"
EOS_IDS = (128001, 128008, 128009)
OPS = ("Box", "Cylinder", "ExtrudePolygon", "Extrude", "Revolve", "Union", "Cut", "Intersect", "Circle", "Rectangle", "Polygon")


def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_executor():
    if sha256(EXECUTOR) != EXECUTOR_SHA256:
        raise RuntimeError("frozen executor SHA256 mismatch")
    spec = importlib.util.spec_from_file_location("formal_eval_cad_dsl", EXECUTOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def operation_f1(target: str, prediction: str) -> float:
    pattern = r"\b(" + "|".join(OPS) + r")\s*\("
    a, b = Counter(re.findall(pattern, target)), Counter(re.findall(pattern, prediction))
    true_positive = sum((a & b).values())
    if not a and not b:
        return 1.0
    if true_positive == 0:
        return 0.0
    precision = true_positive / max(sum(b.values()), 1)
    recall = true_positive / max(sum(a.values()), 1)
    return 2 * precision * recall / (precision + recall)


def literal(node):
    try:
        return ast.literal_eval(node)
    except Exception:
        return None


def calls(text: str, name: str):
    try:
        tree = ast.parse(text)
    except Exception:
        return []
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name:
            keywords = {kw.arg: literal(kw.value) for kw in node.keywords if kw.arg}
            positional = [literal(value) for value in node.args]
            found.append((getattr(node, "lineno", 0), positional, keywords))
    return sorted(found)


def vector_error(a, b, scale: float):
    try:
        aa, bb = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
        if aa.shape != (3,) or bb.shape != (3,):
            return None
        return float(np.linalg.norm(aa - bb) / max(scale, 1e-12))
    except Exception:
        return None


def scalar_error(a, b, scale: float):
    try:
        return float(abs(float(a) - float(b)) / max(scale, 1e-12))
    except Exception:
        return None


def parameter_errors(target: str, prediction: str, scale: float) -> dict:
    result = {}
    specs = {
        "box_origin_error": ("Box", "origin", None, vector_error),
        "extrude_origin_error": ("Extrude", "origin", None, vector_error),
        "extrude_depth_error": ("Extrude", "height", 1, scalar_error),
        "circle_radius_error": ("Circle", "radius", 0, scalar_error),
    }
    for metric, (op, keyword, positional_index, function) in specs.items():
        target_calls, pred_calls = calls(target, op), calls(prediction, op)
        values = []
        for (_, target_pos, target_kw), (_, pred_pos, pred_kw) in zip(target_calls, pred_calls):
            target_value = target_kw.get(keyword)
            pred_value = pred_kw.get(keyword)
            if target_value is None and positional_index is not None and len(target_pos) > positional_index:
                target_value = target_pos[positional_index]
            if pred_value is None and positional_index is not None and len(pred_pos) > positional_index:
                pred_value = pred_pos[positional_index]
            error = function(target_value, pred_value, scale)
            if error is not None and math.isfinite(error):
                values.append(error)
        result[metric] = float(np.mean(values)) if values else None
        result[metric + "_matched_count"] = len(values)
        result[metric + "_gt_count"] = len(target_calls)
        result[metric + "_pred_count"] = len(pred_calls)
    return result


def staged_geometry_metrics(text: str, row: dict, work: Path, executor) -> dict:
    record = {
        "dsl_parse_success": False,
        "dsl_execute_success": False,
        "occ_shape_non_null": False,
        "brep_valid": False,
        "step_write_success": False,
        "step_reload_success": False,
        "failure_reason": None,
        "chamfer_norm": None,
        "hausdorff95_norm": None,
        "bbox_center_error_norm": None,
        "bbox_extent_error_norm": None,
    }
    try:
        clean = executor.extract_dsl_code(text)
        ast.parse(clean)
        program = executor.parse_dsl(clean)
        record["dsl_parse_success"] = True
    except Exception as error:
        record["failure_reason"] = "PARSE_ERROR"
        record["error"] = f"{type(error).__name__}: {error}"[-500:]
        return record
    try:
        shapes = {}
        for name, node in program.assignments.items():
            if name != "result":
                shapes[name] = executor._build_shape(node, shapes) if isinstance(node, dict) and "op" in node else node
        node = program.assignments["result"]
        result = shapes[node] if isinstance(node, str) else executor._build_shape(node, shapes)
        record["dsl_execute_success"] = True
        shape = result.val().wrapped if hasattr(result, "val") else result
        if shape.IsNull():
            record["failure_reason"] = "NULL_SHAPE"
            return record
        record["occ_shape_non_null"] = True
        from OCP.BRepCheck import BRepCheck_Analyzer
        if not BRepCheck_Analyzer(shape).IsValid():
            record["failure_reason"] = "BREP_INVALID"
            return record
        record["brep_valid"] = True
    except Exception as error:
        record["failure_reason"] = "EXECUTE_FAILURE"
        record["error"] = f"{type(error).__name__}: {error}"[-500:]
        return record
    try:
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
        step = work / "pred.step"
        writer = STEPControl_Writer()
        writer.Transfer(shape, STEPControl_AsIs)
        if writer.Write(str(step)) != IFSelect_RetDone or not step.exists() or step.stat().st_size == 0:
            record["failure_reason"] = "STEP_WRITE_FAILURE"
            return record
        record["step_write_success"] = True
        import cadquery as cq
        reloaded = cq.importers.importStep(str(step))
        record["step_reload_success"] = True
        stl = work / "pred.stl"
        cq.exporters.export(reloaded, str(stl))
    except Exception as error:
        record["failure_reason"] = "STEP_RELOAD_FAILURE"
        record["error"] = f"{type(error).__name__}: {error}"[-500:]
        return record
    try:
        import trimesh
        from scipy.spatial import cKDTree
        gt = trimesh.load(str(Path(row["surface_input"]).parent / "mesh.obj"), force="mesh")
        pred = trimesh.load(str(stl), force="mesh")
        if isinstance(gt, trimesh.Scene):
            gt = gt.dump(concatenate=True)
        if isinstance(pred, trimesh.Scene):
            pred = pred.dump(concatenate=True)
        gt_extent, pred_extent = gt.bounds[1] - gt.bounds[0], pred.bounds[1] - pred.bounds[0]
        gt_center, pred_center = gt.bounds.mean(0), pred.bounds.mean(0)
        diagonal = float(np.linalg.norm(gt_extent))
        a, _ = trimesh.sample.sample_surface(gt, 3000, seed=42)
        b, _ = trimesh.sample.sample_surface(pred, 3000, seed=43)
        da = cKDTree(b).query(a, k=1)[0]
        db = cKDTree(a).query(b, k=1)[0]
        record["chamfer_norm"] = float((da.mean() + db.mean()) / 2 / max(diagonal, 1e-12))
        record["hausdorff95_norm"] = float(np.percentile(np.concatenate([da, db]), 95) / max(diagonal, 1e-12))
        record["bbox_center_error_norm"] = float(np.linalg.norm(pred_center - gt_center) / max(diagonal, 1e-12))
        record["bbox_extent_error_norm"] = float(np.linalg.norm(pred_extent - gt_extent) / max(diagonal, 1e-12))
        record.update(parameter_errors(Path(row["target_dsl"]).read_text(), text, diagonal))
        record["failure_reason"] = "SUCCESS"
    except Exception as error:
        record["failure_reason"] = "GEOMETRY_METRIC_FAILURE"
        record["error"] = f"{type(error).__name__}: {error}"[-500:]
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--max-new-tokens", type=int, default=4096)
    parser.add_argument("--start-index", type=int, default=1,
                        help="One-based inclusive index in the frozen dev50 ordering.")
    parser.add_argument("--end-index", type=int, default=50,
                        help="One-based inclusive index in the frozen dev50 ordering.")
    args = parser.parse_args()
    use_anchor, q = ARMS[args.arm]
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    checkpoint = Path(args.checkpoint)
    all_rows = json.loads(DEV.read_text())["records"]
    assert len(all_rows) == 50
    assert 1 <= args.start_index <= args.end_index <= 50
    rows = all_rows[args.start_index - 1:args.end_index]
    expected_count = args.end_index - args.start_index + 1
    device = torch.device(args.device)
    v3.heldout_geometry.install()
    plugin = v3.get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True, use_fast=False)
    model = v3.module.SpatialLMLlamaForCausalLM.from_pretrained(checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    adapter = GeometryPrefixAdapter(256, model.config.hidden_size, num_queries=q, target_norm=1.9414).to(device=device, dtype=torch.bfloat16)
    branch = M2C2SpatialAnchorV1(adapter).to(device=device, dtype=torch.bfloat16) if use_anchor else adapter
    branch.load_state_dict(torch.load(checkpoint / "geometry_branch.pt", map_location=device, weights_only=True))
    model.edge_proj = branch
    model.config.separate_edge_tokens = True
    model.separate_edge_tokens = True
    model.config.use_cache = True
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    model.eval()
    runtime = {}
    original_splice = install_geometry(model, branch, use_anchor, runtime)
    executor = load_executor()
    per_path = output / "per_cad.jsonl"
    records = []
    try:
        for index, row in enumerate(rows, args.start_index):
            ids, labels, prompt_len = encode(tokenizer, row, q)
            prompt = ids[:, :prompt_len].to(device)
            surface, _ = plugin._load_cad_separate_edge(row["surface_input"])
            surface = torch.tensor(surface, device=device).unsqueeze(0)
            raw, mask = load_raw(row)
            runtime["raw_mask"] = mask
            runtime["anchors"] = load_anchor(row)
            edge = raw.to(device).unsqueeze(0)
            with torch.no_grad():
                generated = model.generate(
                    input_ids=prompt,
                    attention_mask=torch.ones_like(prompt),
                    point_clouds=surface,
                    edge_clouds=edge,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                    use_cache=True,
                    eos_token_id=list(EOS_IDS),
                    pad_token_id=128001,
                )
            new = generated[0, prompt_len:].cpu()
            text = tokenizer.decode(new, skip_special_tokens=True)
            target = Path(row["target_dsl"]).read_text()
            target_length = len(tokenizer.encode(target, add_special_tokens=False))
            with tempfile.TemporaryDirectory(dir=output) as directory:
                metrics = staged_geometry_metrics(text, row, Path(directory), executor)
            record = {
                "cad_id": row["cad_id"],
                "epoch": args.epoch,
                "arm": args.arm,
                "target_dsl": target,
                "generated_dsl": text,
                "target_token_length": target_length,
                "generated_token_length": int(new.numel()),
                "generated_target_ratio": float(new.numel() / max(target_length, 1)),
                "hit_max_new_tokens": bool(new.numel() >= args.max_new_tokens),
                "unexpected_runaway": bool(new.numel() >= args.max_new_tokens and target_length <= args.max_new_tokens),
                "eos_emitted": bool(new.numel() and int(new[-1]) in EOS_IDS),
                "op_f1": operation_f1(target, text),
                **metrics,
            }
            records.append(record)
            with per_path.open("a") as handle:
                handle.write(json.dumps(record) + "\n")
            if index % 5 == 0 or index == args.end_index:
                print(f"[{args.arm}] epoch={args.epoch} decode={index}/50 shard={args.start_index}-{args.end_index} runaway={sum(r['unexpected_runaway'] for r in records)} step={sum(r['step_reload_success'] for r in records)}", flush=True)
    finally:
        v3.module._splice_geometry = original_splice
    def mean_present(key):
        values = [r[key] for r in records if r.get(key) is not None]
        return float(np.mean(values)) if values else None
    summary = {
        "ARM": args.arm,
        "EPOCH": args.epoch,
        "CHECKPOINT": str(checkpoint),
        "N": len(records),
        "SHARD_START_INDEX": args.start_index,
        "SHARD_END_INDEX": args.end_index,
        "MAX_NEW_TOKENS": args.max_new_tokens,
        "EOS_COUNT": sum(r["eos_emitted"] for r in records),
        "RUNAWAY_COUNT": sum(r["unexpected_runaway"] for r in records),
        "PARSE_COUNT": sum(r["dsl_parse_success"] for r in records),
        "EXECUTE_COUNT": sum(r["dsl_execute_success"] for r in records),
        "BREP_VALID_COUNT": sum(r["brep_valid"] for r in records),
        "STEP_RELOAD_COUNT": sum(r["step_reload_success"] for r in records),
        "OP_F1": float(np.mean([r["op_f1"] for r in records])),
        "CHAMFER": mean_present("chamfer_norm"),
        "HAUSDORFF95": mean_present("hausdorff95_norm"),
        "BBOX_CENTER_ERROR": mean_present("bbox_center_error_norm"),
        "BBOX_EXTENT_ERROR": mean_present("bbox_extent_error_norm"),
        "BOX_ORIGIN_ERROR": mean_present("box_origin_error"),
        "EXTRUDE_ORIGIN_ERROR": mean_present("extrude_origin_error"),
        "EXTRUDE_DEPTH_ERROR": mean_present("extrude_depth_error"),
        "CIRCLE_RADIUS_ERROR": mean_present("circle_radius_error"),
        "EXECUTOR_PATH": str(EXECUTOR),
        "EXECUTOR_SHA256": EXECUTOR_SHA256,
        "ANCHOR_EVAL_100_MODEL_READ": False,
        "PILOT150_MODEL_READ": False,
        "OFFICIAL_TEST_READ": False,
        "STATUS": "PASS" if len(records) == expected_count else "FAIL",
    }
    (output / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
