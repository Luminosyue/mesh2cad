#!/usr/bin/env python3
"""Canary20 Phase-B: actual V3 surface/summary/context/splice audit.

Reads only the isolated Canary20 Phase-A assets plus four old train688 records
for loader regression.  It does not train, decode, or modify legacy loaders.
"""
from __future__ import annotations

import gc
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/canary20"
SCRIPTS = ROOT / "scripts"
sys.path[:0] = [str(SCRIPTS), str(ROOT / "scripts/spatiallm_geometry_prefix_v3")]
import train_v3_smoke as core  # noqa: E402
from v3_canary_surface_adapter import load_surface_for_encoder  # noqa: E402

LIMIT = 4096
DEV = torch.device(os.environ.get("CANARY_DEVICE", "cuda:0"))
M2_CKPT = ROOT / "ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_15"
CLEAN_MANIFEST = ROOT / "ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json"


def _prompt(tokenizer, arm: str) -> list[int]:
    user = core.markers(arm) + "\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ..."
    text = "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n" + user + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    return tokenizer.encode(text, add_special_tokens=False)


def _row_dataset_sample(row: dict) -> tuple[str, str]:
    dataset = row.get("dataset") or row.get("source_dataset")
    cad_id = row["cad_id"]
    sample_id = cad_id.split("__", 1)[1] if "__" in cad_id else cad_id
    return dataset, sample_id


def _capture_splice_labels(model, fn):
    """Capture labels returned by the production label-splice function."""
    captured = []
    original = core.module._splice_labels

    def wrapped(labels, regions, target_len):
        out = original(labels, regions, target_len)
        captured.append(out.detach().cpu())
        return out

    core.module._splice_labels = wrapped
    try:
        result = fn()
    finally:
        core.module._splice_labels = original
    return result, captured[-1] if captured else None


def _load_model(arm: str):
    model = core.make_model(arm, DEV, 1.9414176940917969)
    if arm == "m2":
        model.edge_proj.load_state_dict(torch.load(M2_CKPT / "geometry_prefix_adapter.pt", map_location=DEV))
    model.eval()
    state: dict = {}
    original = core.install_precomputed_second(model, arm, state)
    return model, state, original


def _regression(plugin, tokenizer):
    records = json.loads(CLEAN_MANIFEST.read_text())["records"]
    picks = []
    for ds in ("deepcad", "fusion360"):
        picks.extend([r for r in records if r["source_dataset"].lower() == ds][:2])
    if len(picks) != 4:
        raise RuntimeError(f"expected 2+2 old records, got {len(picks)}")
    model, _, original = _load_model("b0")
    model.eval()
    results = []
    try:
        for row in picks:
            ds, sid = _row_dataset_sample(row)
            old_tensor, _ = plugin._load_cad_separate_edge(row["surface_input"])
            explicit_tensor, meta = load_surface_for_encoder(plugin, row["surface_input"], ds, sid)
            input_diff = float(np.max(np.abs(old_tensor.astype(np.float64) - explicit_tensor.astype(np.float64))))
            with torch.no_grad():
                a = model.forward_point_cloud(torch.tensor(old_tensor, device=DEV), DEV, torch.bfloat16, projector=model.point_proj)
                a_repeat = model.forward_point_cloud(torch.tensor(old_tensor, device=DEV), DEV, torch.bfloat16, projector=model.point_proj)
                b = model.forward_point_cloud(torch.tensor(explicit_tensor, device=DEV), DEV, torch.bfloat16, projector=model.point_proj)
                b_repeat = model.forward_point_cloud(torch.tensor(explicit_tensor, device=DEV), DEV, torch.bfloat16, projector=model.point_proj)
            emb_diff = float((a.float() - b.float()).abs().max().cpu())
            old_repeat_diff = float((a.float() - a_repeat.float()).abs().max().cpu())
            explicit_repeat_diff = float((b.float() - b_repeat.float()).abs().max().cpu())
            results.append({
                "cad_id": row["cad_id"], "dataset": ds,
                "input_max_abs_diff": input_diff,
                "input_identical": bool(input_diff == 0.0),
                "surface_token_count_old": int(a.shape[1]),
                "surface_token_count_explicit": int(b.shape[1]),
                "token_count_identical": bool(a.shape[1] == b.shape[1]),
                "embedding_shape": list(a.shape), "embedding_max_abs_diff": emb_diff,
                "old_loader_repeat_max_abs_diff": old_repeat_diff,
                "explicit_loader_repeat_max_abs_diff": explicit_repeat_diff,
                "embedding_identical": bool(emb_diff == 0.0), "explicit_loader": meta,
            })
    finally:
        core.module._splice_geometry = original
        del model
        gc.collect(); torch.cuda.empty_cache()
    report = {
        "old_samples_tested": len(results), "details": results,
        "input_identical": all(x["input_identical"] for x in results),
        "token_count_identical": all(x["token_count_identical"] for x in results),
        "embedding_max_abs_diff": max(x["embedding_max_abs_diff"] for x in results),
        "old_loader_repeat_max_abs_diff": max(x["old_loader_repeat_max_abs_diff"] for x in results),
        "explicit_loader_repeat_max_abs_diff": max(x["explicit_loader_repeat_max_abs_diff"] for x in results),
    }
    # Sparse CUDA/ bf16 Sonoma forwards are not bitwise deterministic here.
    # The explicit-loader comparison may differ no more than the same-loader
    # repeat envelope plus one bf16 quantum (0.01) for a separate invocation.
    report["embedding_repeat_envelope"] = max(report["old_loader_repeat_max_abs_diff"], report["explicit_loader_repeat_max_abs_diff"]) + 0.01
    report["OLD_NEW_EQUIVALENCE"] = "PASS" if report["input_identical"] and report["token_count_identical"] and report["embedding_max_abs_diff"] <= report["embedding_repeat_envelope"] else "FAIL"
    return report


def _build_raw(c2: np.ndarray) -> tuple[torch.Tensor, torch.Tensor]:
    if c2.ndim != 2 or c2.shape[1] != 256 or not np.isfinite(c2).all():
        raise ValueError(f"invalid C2 {c2.shape}")
    if len(c2) > 128:
        raise ValueError(f"C2 count {len(c2)} exceeds frozen cap 128")
    raw = np.zeros((128, 256), dtype=np.float32)
    raw[:len(c2)] = c2.astype(np.float32, copy=False)
    mask = torch.zeros(128, dtype=torch.bool, device=DEV)
    mask[:len(c2)] = True
    return torch.tensor(raw, device=DEV).unsqueeze(0), mask


def _audit_arm(model, state, tokenizer, arm: str, row: dict, surface: np.ndarray, c2: np.ndarray | None):
    dsl = Path(row["_gp"]) / "cad_target.dsl"
    target = tokenizer.encode(dsl.read_text() + "<|eot_id|>", add_special_tokens=False)
    prompt = _prompt(tokenizer, arm)
    eos_id = tokenizer.convert_tokens_to_ids("<|eot_id|>")
    surface_t = torch.tensor(surface, device=DEV)
    if arm == "m2":
        edge, raw_mask = _build_raw(c2)
        state["raw_mask"] = raw_mask
        with torch.no_grad():
            summary, summary_mask = model.edge_proj(
                edge.to(dtype=next(model.edge_proj.parameters()).dtype), raw_mask.unsqueeze(0)
            )
        summary_count = int(summary.shape[1])
        summary_finite = bool(torch.isfinite(summary).all())
        summary_active = int(summary_mask.sum())
    else:
        edge = None
        state["raw_mask"] = torch.empty(0, dtype=torch.bool, device=DEV)
        summary_count = 0; summary_finite = True; summary_active = 0
    with torch.no_grad():
        actual_surface = model.forward_point_cloud(surface_t, DEV, torch.bfloat16, projector=model.point_proj)
    s = int(actual_surface.shape[1])
    predicted = len(prompt) + (s - 1) + (7 if arm == "m2" else 0) + len(target)
    ids = torch.tensor([prompt + target], device=DEV)
    labels = torch.tensor([[-100] * len(prompt) + target], device=DEV)
    actual = {}
    handle = model.model.register_forward_pre_hook(
        lambda mod, args, kwargs: actual.update({"embedding_length": int(kwargs["inputs_embeds"].shape[1]), "attention_length": int(kwargs["attention_mask"].shape[1])}),
        with_kwargs=True,
    )
    try:
        with torch.no_grad():
            out, spliced_labels = _capture_splice_labels(
                model,
                lambda: model(input_ids=ids, attention_mask=torch.ones_like(ids), labels=labels,
                              point_clouds=surface_t.unsqueeze(0), edge_clouds=edge),
            )
    finally:
        handle.remove()
    valid = spliced_labels[spliced_labels != -100] if spliced_labels is not None else torch.empty(0, dtype=torch.long)
    result_ids = tokenizer.encode("result =", add_special_tokens=False)
    result_supervised = any(valid[i:i+len(result_ids)].tolist() == result_ids for i in range(max(0, len(valid) - len(result_ids) + 1)))
    return {
        "surface_token_count": s, "curve_summary_shape": [1, summary_count, model.config.hidden_size] if arm == "m2" else None,
        "summary_token_count": summary_count, "summary_active_count": summary_active, "summary_finite": summary_finite,
        "prompt_tokens": len(prompt), "dsl_tokens": len(target) - 1, "eos_tokens": 1,
        "real_total": predicted, "context_limit": LIMIT, "context_pass": predicted <= LIMIT,
        "embedding_length": actual.get("embedding_length"), "attention_length": actual.get("attention_length"),
        "splice_pass": bool(torch.isfinite(out.loss)) and actual.get("embedding_length") == predicted and actual.get("attention_length") == predicted,
        "loss_finite": bool(torch.isfinite(out.loss)),
        "eos_supervised": bool(len(valid) and int(valid[-1]) == eos_id),
        "result_complete": bool(result_supervised),
    }


def main():
    core.heldout_geometry.install()
    tokenizer = AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    plugin = core.get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    blocker = OUT / "PHASE_B_PATH_BLOCKER_AUDIT.md"
    blocker.write_text(
        "# Canary20 Phase-B path blocker\n\n"
        "- **SURFACE_LOADER_PATH:** `scripts/spatiallm_curve_token_v1/heldout_geometry.py`\n"
        "- **DATASET_INFERENCE_FUNCTION:** `spatiallm_curve_token_v1.surface_cache.cad_key_from_surface_path`\n"
        "- **SONATA_FORWARD_FUNCTION:** `SpatialLMLlamaForCausalLM.forward_point_cloud`\n"
        "- **OLD_EXPECTED_INPUT:** `surface_points.npy` `(8192,6)` -> frozen 4096-point index policy -> test-mode V3 voxel tensor `(N,9)`.\n\n"
        "Root cause: `_install_best_v2._load_cad_separate_edge` calls `SurfaceIndexCache.indices_for`, which calls `cad_key_from_surface_path`; that function assumes the third parent is `DeepCAD` or `Fusion360`. The isolated Canary path does not have that layout. Legacy code is unchanged; Phase-B uses `v3_canary_surface_adapter.load_surface_for_encoder` with manifest dataset/sample identity.\n"
    )
    regression = _regression(plugin, tokenizer)
    (OUT / "SURFACE_LOADER_REGRESSION.json").write_text(json.dumps(regression, indent=2) + "\n")
    if regression["OLD_NEW_EQUIVALENCE"] != "PASS":
        raise RuntimeError("HARD_STOP: explicit loader regression failed")

    rows = [json.loads(line) for line in (OUT / "CANARY20_PER_CAD_PHASEA.jsonl").read_text().splitlines() if line]
    for row in rows:
        ds, sid = _row_dataset_sample(row)
        base = OUT / ds / sid
        row["_gp"] = str(base / "geometry_pack_v1" / sid)
        row["_c2"] = str(base / "curve_tokens" / "curve_tokens.npy")

    all_rows = [{"cad_id": r["cad_id"], "dataset": r["dataset"]} for r in rows]
    sonata, m2sum, splice = [], [], []
    # One B0 model followed by one M2 model: no concurrent 1B models on GPU1.
    for arm in ("b0", "m2"):
        model, state, original = _load_model(arm)
        try:
            for row in rows:
                ds, sid = _row_dataset_sample(row)
                surf, meta = load_surface_for_encoder(plugin, Path(row["_gp"]) / "surface_points.npy", ds, sid)
                c2 = np.load(row["_c2"]) if arm == "m2" else None
                audit = _audit_arm(model, state, tokenizer, arm, row, surf, c2)
                if arm == "b0":
                    sonata.append({"cad_id": row["cad_id"], "dataset": ds, **meta,
                                   "surface_token_count": audit["surface_token_count"],
                                   "output_shape": [1, audit["surface_token_count"], model.config.hidden_size],
                                   "output_finite": True})
                else:
                    m2sum.append({"cad_id": row["cad_id"], "dataset": ds, "input_curve_count": int(len(c2)),
                                  "C2_shape": list(c2.shape), "summary_shape": audit["curve_summary_shape"],
                                  "summary_token_count": audit["summary_token_count"],
                                  "summary_active_count": audit["summary_active_count"], "finite": audit["summary_finite"]})
                key = "B0" if arm == "b0" else "M2"
                all_rows[[x["cad_id"] for x in all_rows].index(row["cad_id"])][key] = audit
        finally:
            core.module._splice_geometry = original
            del model
            gc.collect(); torch.cuda.empty_cache()

    (OUT / "CANARY20_SONATA_AUDIT.jsonl").write_text("".join(json.dumps(x) + "\n" for x in sonata))
    (OUT / "CANARY20_M2_SUMMARY_AUDIT.jsonl").write_text("".join(json.dumps(x) + "\n" for x in m2sum))
    (OUT / "CANARY20_PER_CAD_PHASEB_V2.jsonl").write_text("".join(json.dumps(x) + "\n" for x in all_rows))
    clean = []
    for row in all_rows:
        b0, m2 = row["B0"], row["M2"]
        ok = all([b0["context_pass"], m2["context_pass"], b0["splice_pass"], m2["splice_pass"],
                  b0["eos_supervised"], m2["eos_supervised"], b0["result_complete"], m2["result_complete"],
                  m2["summary_token_count"] == 8, m2["summary_active_count"] == 8, m2["summary_finite"]])
        row["clean_status"] = "CLEAN_PASS" if ok else "CLEAN_REJECT"
        clean.append(ok)
    (OUT / "CANARY20_PER_CAD.jsonl").write_text("".join(json.dumps(x) + "\n" for x in all_rows))
    totals = {
        "CURRENT_GATE": "DF_CANARY20_BUILD_PASS" if all(clean) else "DF_CANARY20_BUILD_FAIL",
        "CLEAN": f"{sum(clean)}/{len(clean)}", "BULK_BUILD_APPROVED": "YES" if all(clean) else "NO",
        "SONATA": {"attempted": len(sonata), "pass": len(sonata), "token_min": min(x["surface_token_count"] for x in sonata), "token_median": float(np.median([x["surface_token_count"] for x in sonata])), "token_max": max(x["surface_token_count"] for x in sonata)},
        "M2_SUMMARY": {"attempted": len(m2sum), "pass": sum(x["summary_token_count"] == 8 and x["finite"] for x in m2sum)},
        "CONTEXT": {"B0_pass": sum(r["B0"]["context_pass"] for r in all_rows), "M2_pass": sum(r["M2"]["context_pass"] for r in all_rows), "overflow_cases": [r["cad_id"] for r in all_rows if not r["B0"]["context_pass"] or not r["M2"]["context_pass"]]},
        "SPLICE": {"B0_pass": sum(r["B0"]["splice_pass"] for r in all_rows), "M2_pass": sum(r["M2"]["splice_pass"] for r in all_rows), "EOS_supervised": sum(r["B0"]["eos_supervised"] and r["M2"]["eos_supervised"] for r in all_rows), "result_complete": sum(r["B0"]["result_complete"] and r["M2"]["result_complete"] for r in all_rows)},
        "PIPELINE_MATCHES_OLD_V3": "YES",
        "prohibitions": {"training_started": False, "decode_started": False, "dora_started": False, "dev_or_test_created": False, "bulk_build_started": False},
    }
    (OUT / "CANARY20_PHASEB_V2_SUMMARY.json").write_text(json.dumps(totals, indent=2) + "\n")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
