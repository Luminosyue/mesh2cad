#!/usr/bin/env python3
"""Task-level edge ablation on a trained separate_edge_tokens_v1 checkpoint.

One checkpoint, one surface stream, four edge conditions:

    real       Surface A + Edge A
    zero       Surface A + zeroed edge features (lattice preserved)
    wrong      Surface A + Edge B from a different CAD part
    corrupted  Surface A + spatially scrambled Edge A

Reports eval loss and CAD token accuracy per condition, plus greedy-decode
validity, so the conclusion rests on task behaviour rather than on embedding
movement alone.

The interpretation rule is fixed in advance:

    real clearly better than wrong/zero  -> the edge stream carries information
    real ~= wrong ~= corrupted           -> EDGE_PRESENCE_ONLY, no structure learned
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import (  # noqa: E402
    CACHE_DIR,
    OUT_ROOT,
    build_batch,
    corrupt_edge,
    json_dump,
    load_geometry,
    load_model,
    make_plugin,
    read_dsl,
    set_deterministic_serialization,
    zero_edge_like,
)

CONDITIONS = ("real", "zero", "wrong", "corrupted")


def dsl_is_valid(text: str) -> bool:
    """Structural validity: parses as Python and assigns `result`."""
    body = "\n".join(
        ln for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")
    )
    if not body.strip():
        return False
    try:
        tree = ast.parse(body, mode="exec")
    except SyntaxError:
        return False
    assigns = [
        t.id
        for st in tree.body
        if isinstance(st, ast.Assign)
        for t in st.targets
        if isinstance(t, ast.Name)
    ]
    return "result" in assigns


def make_edge_variant(condition: str, edge_a, edge_other, seed: int):
    if condition == "real":
        return edge_a
    if condition == "zero":
        return zero_edge_like(edge_a)
    if condition == "corrupted":
        return corrupt_edge(edge_a, seed=seed)
    if condition == "wrong":
        return edge_other
    raise ValueError(condition)


@torch.no_grad()
def score(model, tokenizer, sample_ids, condition, plugin, device, decode, max_new):
    losses, correct, total = [], 0, 0
    valid, decoded_n = 0, 0
    per_sample = []
    geoms = {sid: load_geometry(sid, plugin) for sid in sample_ids}

    for i, sid in enumerate(sample_ids):
        surface, edge_a = geoms[sid]
        # "wrong" pairs each part with the next part's edges, deterministically.
        other_sid = sample_ids[(i + 1) % len(sample_ids)]
        edge_other = geoms[other_sid][1]
        edge = make_edge_variant(condition, edge_a, edge_other, seed=i)

        dsl = read_dsl(sid)
        batch = build_batch(tokenizer, surface, edge, dsl, device, separate_edge=True)
        out = model(**batch)
        loss = float(out.loss.item())
        losses.append(loss)

        target_len = int((batch["labels"] != -100).sum().item())
        pred = out.logits[0, -target_len - 1 : -1].argmax(-1)
        gold = batch["labels"][0, -target_len:]
        c = int((pred == gold).sum().item())
        correct += c
        total += target_len

        row = {
            "sample_id": sid,
            "wrong_edge_from": other_sid if condition == "wrong" else None,
            "loss": loss,
            "token_accuracy": c / max(target_len, 1),
        }

        if decode:
            gen_batch = build_batch(
                tokenizer, surface, edge, None, device, separate_edge=True
            )
            gen = model.generate(
                input_ids=gen_batch["input_ids"],
                attention_mask=gen_batch["attention_mask"],
                point_clouds=gen_batch["point_clouds"],
                edge_clouds=gen_batch.get("edge_clouds"),
                max_new_tokens=max_new,
                do_sample=False,
                num_beams=1,
                pad_token_id=tokenizer.eos_token_id,
            )
            text = tokenizer.decode(
                gen[0, gen_batch["input_ids"].shape[1] :], skip_special_tokens=True
            )
            ok = dsl_is_valid(text)
            valid += int(ok)
            decoded_n += 1
            row["decoded_valid"] = ok
            row["decoded"] = text
        per_sample.append(row)

    return {
        "condition": condition,
        "num_samples": len(sample_ids),
        "eval_loss": float(np.mean(losses)),
        "eval_loss_std": float(np.std(losses)),
        "token_accuracy": float(correct / max(total, 1)),
        "cad_validity": (valid / decoded_n) if decoded_n else None,
        "num_decoded": decoded_n,
        "per_sample": per_sample,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--ids-file", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--device", type=str, default="cuda")
    ap.add_argument("--out", type=Path, default=OUT_ROOT / "ablations/edge_ablation.json")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--max-new-tokens", type=int, default=256)
    args = ap.parse_args()

    ids = [
        ln.strip()
        for ln in args.ids_file.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    ids = [i for i in ids if (CACHE_DIR / i / "edge_points.npy").is_file()]
    if args.limit:
        ids = ids[: args.limit]
    if len(ids) < 2:
        raise SystemExit("need >= 2 samples so 'wrong' can pair distinct parts")

    model, tokenizer = load_model(
        args.checkpoint, separate_edge=True, device=args.device, dtype=torch.float32
    )
    set_deterministic_serialization(model.point_backbone)
    model.eval()
    plugin = make_plugin(separate_edge=True)

    results = {}
    for cond in CONDITIONS:
        results[cond] = score(
            model, tokenizer, ids, cond, plugin, args.device, args.decode, args.max_new_tokens
        )
        print(
            f"{cond:10s} loss={results[cond]['eval_loss']:.4f} "
            f"acc={results[cond]['token_accuracy']:.4f} "
            f"validity={results[cond]['cad_validity']}",
            flush=True,
        )

    real = results["real"]
    deltas = {
        f"real_vs_{c}": {
            "loss_delta": results[c]["eval_loss"] - real["eval_loss"],
            "accuracy_delta": real["token_accuracy"] - results[c]["token_accuracy"],
        }
        for c in ("zero", "wrong", "corrupted")
    }

    # Paired per-sample test: is real better on a majority of individual parts?
    paired = {}
    for c in ("zero", "wrong", "corrupted"):
        r = np.array([p["loss"] for p in real["per_sample"]])
        o = np.array([p["loss"] for p in results[c]["per_sample"]])
        paired[f"real_vs_{c}"] = {
            "real_better_fraction": float((r < o).mean()),
            "mean_paired_loss_gap": float((o - r).mean()),
            "paired_loss_gap_std": float((o - r).std()),
        }

    beats_zero = deltas["real_vs_zero"]["loss_delta"] > 0
    beats_wrong = deltas["real_vs_wrong"]["loss_delta"] > 0
    beats_corrupted = deltas["real_vs_corrupted"]["loss_delta"] > 0

    report = {
        "experiment": "separate_edge_tokens_v1",
        "checkpoint": str(args.checkpoint),
        "num_samples": len(ids),
        "sample_ids": ids,
        "REAL_EDGE_EVAL_LOSS": real["eval_loss"],
        "ZERO_EDGE_EVAL_LOSS": results["zero"]["eval_loss"],
        "WRONG_EDGE_EVAL_LOSS": results["wrong"]["eval_loss"],
        "CORRUPTED_EDGE_EVAL_LOSS": results["corrupted"]["eval_loss"],
        "deltas": deltas,
        "paired": paired,
        "REAL_BEATS_ZERO": bool(beats_zero),
        "REAL_BEATS_WRONG": bool(beats_wrong),
        "REAL_BEATS_CORRUPTED": bool(beats_corrupted),
        # Structure is only credited when a *correct* edge cloud beats a
        # geometrically wrong one, not merely an absent one.
        "EDGE_STRUCTURE_LEARNED": bool(beats_wrong and beats_corrupted),
        "EDGE_PRESENCE_ONLY": bool(beats_zero and not (beats_wrong and beats_corrupted)),
        "results": results,
    }
    json_dump(args.out, report)
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in ("results", "sample_ids")},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
