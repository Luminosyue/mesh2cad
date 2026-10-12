#!/usr/bin/env python3
"""Free causal test on the frozen M2 checkpoint (no retraining).

Variants (second stream only; surface unchanged):

  correct  real curve tokens for this CAD
  drop     remove curve region entirely (surface-only prompt + no edge_clouds)
  zero     keep region / K, but zero the curve embeddings
  shuffle  keep K from donor CAD's curve tokens (wrong CAD)

If all four scores match, M2 is mostly memorizing via the surface stream.
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
for p in (
    str(REPO_ROOT / "SpatialLM"),
    str(REPO_ROOT / "scripts"),
    str(REPO_ROOT / "scripts" / "deepcad"),
    str(REPO_ROOT / "scripts" / "geometry_pack_v1"),
    str(REPO_ROOT / "scripts" / "separate_edge_tokens_v1"),
):
    if p not in sys.path:
        sys.path.insert(0, p)

from decode_joint_j0_j2 import _evaluate_one, _load_sepedge, _summarize  # noqa: E402
from separate_edge_tokens_v1.common import (  # noqa: E402
    make_plugin,
    set_deterministic_serialization,
)

from spatiallm_curve_token_v1.config import OUTPUT_ROOT, SUBSET_DIR  # noqa: E402
from spatiallm_curve_token_v1.decode_curve100 import (  # noqa: E402
    ARM_CKPT,
    MEDIA_DEFAULT,
    _configure_env,
    _load_m2_checkpoint,
    generate_dsl,
)

VARIANTS = ("correct", "drop", "zero", "shuffle")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", choices=VARIANTS, required=True)
    ap.add_argument("--checkpoint", type=Path, default=ARM_CKPT["M2"])
    ap.add_argument("--split-json", type=Path, default=SUBSET_DIR / "curve100_train.json")
    ap.add_argument("--media-dir", type=Path, default=MEDIA_DEFAULT)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dtype", default="bfloat16", choices=("bfloat16", "float32"))
    ap.add_argument("--max-new-tokens", type=int, default=4096)
    ap.add_argument(
        "--gt-len-exclude-above",
        type=int,
        default=2048,
        help="Also write report excluding GT CAD tokens > this. 0 disables.",
    )
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--shuffle-seed", type=int, default=0)
    args = ap.parse_args()

    _configure_env("M2")
    out = args.out or (OUTPUT_ROOT / "causal_m2" / args.variant)
    out.mkdir(parents=True, exist_ok=True)

    records = json.loads(args.split_json.read_text(encoding="utf-8"))
    records = records[args.offset :]
    if args.limit is not None:
        records = records[: args.limit]

    # Deterministic donor permutation for shuffle (derangement when n>1).
    rng = np.random.default_rng(args.shuffle_seed)
    donor_idx = np.arange(len(records))
    if args.variant == "shuffle" and len(records) > 1:
        for _ in range(50):
            donor_idx = rng.permutation(len(records))
            if not np.any(donor_idx == np.arange(len(records))):
                break
        else:
            # fallback: rotate by 1
            donor_idx = np.roll(np.arange(len(records)), 1)

    plugin = make_plugin(separate_edge=True)
    dtype = getattr(torch, args.dtype)
    model, tokenizer = _load_m2_checkpoint(args.checkpoint, "cuda", dtype)
    set_deterministic_serialization(model.point_backbone)
    model.eval()

    # Preload all curve tensors once (cheap .npy) for shuffle donors.
    curve_cache: dict[str, torch.Tensor] = {}
    surface_cache: dict[str, torch.Tensor] = {}

    def _load_pair(rec: dict):
        sid = rec["id"]
        if sid not in surface_cache:
            npy = args.media_dir / rec["point_clouds"][0]
            surface, edge = _load_sepedge(plugin, npy)
            surface_cache[sid] = surface
            curve_cache[sid] = edge
        return surface_cache[sid], curve_cache[sid]

    rows: list[dict] = []
    for i, rec in enumerate(records):
        sid = rec["id"]
        sample_out = out / sid
        row_path = sample_out / "row.json"
        if args.resume and row_path.exists():
            rows.append(json.loads(row_path.read_text(encoding="utf-8")))
            print(f"[resume] {sid}", flush=True)
            continue

        surface, curve = _load_pair(rec)
        separate_edge = True
        edge = curve
        donor_id = None

        if args.variant == "drop":
            separate_edge = False
            edge = None
        elif args.variant == "zero":
            edge = torch.zeros_like(curve)
        elif args.variant == "shuffle":
            donor = records[int(donor_idx[i])]
            donor_id = donor["id"]
            _, edge = _load_pair(donor)
        elif args.variant == "correct":
            pass
        else:
            raise ValueError(args.variant)

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
        row["arm"] = "M2"
        row["causal_variant"] = args.variant
        row["donor_id"] = donor_id
        row["curve_K_used"] = None if edge is None else int(edge.shape[1])
        row_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        rows.append(row)

        print(
            f"[M2-{args.variant}] {sid}: exact={row['exact_match']} "
            f"step={row.get('step_ok')} op_f1={row['op_f1']:.2f} "
            f"stop={row.get('stop_reason')} gt_tok={gt_cad_tokens} donor={donor_id}",
            flush=True,
        )

        if (i + 1) % 10 == 0 or (i + 1) == len(records):
            _write_causal_reports(
                out,
                rows,
                {
                    "arm": "M2",
                    "causal_variant": args.variant,
                    "checkpoint": str(args.checkpoint),
                    "max_new_tokens": args.max_new_tokens,
                },
                args.gt_len_exclude_above,
            )

    report, report_filt = _write_causal_reports(
        out,
        rows,
        {
            "arm": "M2",
            "causal_variant": args.variant,
            "checkpoint": str(args.checkpoint),
            "max_new_tokens": args.max_new_tokens,
            "shuffle_seed": args.shuffle_seed,
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


def _write_causal_reports(
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
