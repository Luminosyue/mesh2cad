#!/usr/bin/env python3
"""CAD_SEQUENCE_LENGTH_CONTRACT_AUDIT_V1

Audit training label length + inference generation length contracts for DeepCAD.

Per sample (training):
  sample_id, gt_ops, gt_dsl_tokens, prompt_tokens, total_text_tokens,
  point_patches, effective_total_tokens, supervised_label_tokens,
  cutoff_len, label_truncated

Per sample (decode, optional):
  max_new_tokens, prediction_tokens, stop_reason, pred_ops, gt_ops,
  predicted_op_count_over_gt_op_count

Also reports GT token length vs under-generation correlation.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPATIALLM = ROOT / "SpatialLM"
sys.path.insert(0, str(SPATIALLM))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

from audit_program_complexity import SOLID_OPS, analyze_dsl  # noqa: E402
from create_spatiallm_cad_dataset import (  # noqa: E402
    CAD_INSTRUCTION,
    _load_dsl_label,
)

DEFAULT_TOKENIZER = SPATIALLM / "models/SpatialLM1.1-Llama-1B"
DEFAULT_MANIFEST = ROOT / "cad_spatial_dataset/DeepCAD/manifest_train1000.json"
DEFAULT_OUT = ROOT / "cad_spatial_dataset/DeepCAD/sequence_length_contract_audit_v1.json"


def _pct(n: int, total: int) -> float:
    return 100.0 * n / total if total else 0.0


def _stats(xs: list[float]) -> dict[str, float | None]:
    if not xs:
        return {k: None for k in ("mean", "median", "p25", "p75", "p95", "min", "max")}
    arr = np.asarray(xs, dtype=float)
    return {
        "mean": float(arr.mean()),
        "median": float(np.median(arr)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "p95": float(np.percentile(arr, 95)),
        "min": float(arr.min()),
        "max": float(arr.max()),
    }


def _load_manifest_ids(manifest: Path) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return [str(s).replace("/", "_") for s in data.get("sample_ids", [])]


def _setup_training_template(cutoff_len: int, num_bins: int, template_name: str):
    from spatiallm.tuner.data.template import (
        TEMPLATES,
        get_template_and_fix_tokenizer,
        register_spatiallm_templates,
        Role,
    )
    from spatiallm.tuner.data.collator import _encode_messages_example, infer_seqlen
    from spatiallm.tuner.data.mm_plugin import POINT_CLOUD_PLACEHOLDER
    from spatiallm.tuner.hparams.data_args import DataArguments
    from transformers import AutoTokenizer

    if not TEMPLATES:
        register_spatiallm_templates(cutoff_len=cutoff_len, num_bins=num_bins)
    elif template_name in TEMPLATES:
        TEMPLATES[template_name].cutoff_len = cutoff_len
    tokenizer = AutoTokenizer.from_pretrained(
        str(DEFAULT_TOKENIZER), trust_remote_code=True
    )
    data_args = DataArguments(template=template_name, cutoff_len=cutoff_len)
    template = get_template_and_fix_tokenizer(tokenizer, data_args)
    return tokenizer, template, Role, POINT_CLOUD_PLACEHOLDER, _encode_messages_example, infer_seqlen


def _solid_op_count_from_dsl(dsl_text: str) -> int:
    feat = analyze_dsl(dsl_text)
    return int(feat.get("op_count", 0))


@dataclass
class EncoderCache:
    model: Any | None = None
    device: str = "cpu"

    def point_patches(self, sample_dir: Path) -> int | None:
        if self.model is None:
            return None
        import torch
        from spatiallm_cad_frontend import preprocess_cad_point_cloud

        feats = np.load(sample_dir / "features_canonical.npy")
        pts, normals = feats[:, :3], feats[:, 3:6]
        edge = feats[:, 6] if feats.shape[1] >= 7 else np.zeros(len(feats))
        part = preprocess_cad_point_cloud(pts, normals, edge, already_canonical=True)
        with torch.inference_mode():
            enc = self.model.forward_point_cloud(
                part.tensor[0].to(self.device),
                self.device,
                torch.bfloat16,
            )
        return int(enc.shape[1])


def _load_encoder(checkpoint: Path | None, device: str) -> EncoderCache:
    if checkpoint is None:
        return EncoderCache()
    import torch
    import spatiallm  # noqa: F401
    from transformers import AutoModelForCausalLM

    model = AutoModelForCausalLM.from_pretrained(
        str(checkpoint), torch_dtype=torch.bfloat16, trust_remote_code=True
    )
    model.to(device)
    model.eval()
    return EncoderCache(model=model, device=device)


def audit_training_contract(
    sample_ids: list[str],
    train_dir: Path,
    cutoff_len: int,
    num_bins: int,
    template_name: str,
    encoder: EncoderCache,
) -> list[dict[str, Any]]:
    from spatiallm.tuner.data.template import IGNORE_INDEX

    (
        tokenizer,
        template,
        Role,
        POINT_CLOUD_PLACEHOLDER,
        encode_messages,
        infer_seqlen,
    ) = _setup_training_template(cutoff_len, num_bins, template_name)
    plugin = template.mm_plugin
    records: list[dict[str, Any]] = []

    for sid in sample_ids:
        sample_dir = train_dir / sid
        dsl_path = sample_dir / "program_canonical.dsl"
        pc_path = sample_dir / "features_canonical.npy"
        if not dsl_path.exists() or not pc_path.exists():
            records.append({"sample_id": sid, "error": "missing_canonical_artifacts"})
            continue

        dsl_label = _load_dsl_label(dsl_path)
        gt_dsl_tokens = len(tokenizer.encode(dsl_label, add_special_tokens=False))
        gt_ops = _solid_op_count_from_dsl(dsl_label)

        feats = plugin._load_cad_npy(str(pc_path))
        messages = [
            {
                "role": Role.USER.value,
                "content": f"{POINT_CLOUD_PLACEHOLDER}\n{CAD_INSTRUCTION.strip()}",
            },
            {"role": Role.ASSISTANT.value, "content": dsl_label},
        ]
        transformations = [
            {
                "angle_z": 0.0,
                "center_pt": np.zeros(3),
                "scaling": 1.0,
                "min_bound": np.zeros(3),
                "transformed_points": feats[:, 3:6],
            }
        ]
        proc = plugin.process_messages(messages, transformations)
        pairs = template.encode_multiturn(tokenizer, proc, system=None)
        source_ids, target_ids = pairs[0]
        full_prompt_tokens = len(source_ids)
        full_target_tokens = len(target_ids)

        input_ids, labels = encode_messages(
            proc, None, [str(pc_path)], template, tokenizer, cutoff_len
        )
        supervised_label_tokens = sum(1 for x in labels if x != IGNORE_INDEX)
        _, truncated_target_len = infer_seqlen(
            full_prompt_tokens, full_target_tokens, cutoff_len
        )
        label_truncated = truncated_target_len < full_target_tokens

        point_patches = encoder.point_patches(sample_dir)
        total_text_tokens = len(input_ids)
        effective_total_tokens = None
        if point_patches is not None:
            # point_pad placeholder replaced by encoder patches in model forward
            effective_total_tokens = total_text_tokens - 1 + point_patches

        records.append(
            {
                "sample_id": sid,
                "gt_ops": gt_ops,
                "gt_dsl_tokens": gt_dsl_tokens,
                "prompt_tokens": full_prompt_tokens,
                "total_text_tokens": total_text_tokens,
                "point_patches": point_patches,
                "effective_total_tokens": effective_total_tokens,
                "supervised_label_tokens": supervised_label_tokens,
                "cutoff_len": cutoff_len,
                "label_truncated": label_truncated,
                "label_tokens_lost": max(0, full_target_tokens - supervised_label_tokens),
            }
        )
    return records


def _infer_stop_reason(
    pred_text: str,
    prediction_tokens: int,
    max_new_tokens: int,
    parsed: bool,
) -> str:
    if prediction_tokens >= max(1, max_new_tokens - 2):
        return "MAX_LENGTH"
    text = pred_text.strip()
    if parsed and "result =" in text:
        return "EOS"
    if text.endswith("<|eot_id|>") or text.endswith("<|endoftext|>"):
        return "EOS"
    # Short incomplete output — model stopped before finishing program
    if prediction_tokens < max_new_tokens * 0.5:
        return "EOS"
    return "UNKNOWN"


def audit_decode_contract(
    pred_root: Path,
    tokenizer,
    max_new_tokens: int,
    train_dir: Path,
) -> list[dict[str, Any]]:
    from edge_aware_cad_planner_v1.cad_dsl import extract_dsl_code, parse_dsl

    rows: list[dict[str, Any]] = []
    for sample_dir in sorted(p for p in pred_root.iterdir() if p.is_dir()):
        sid = sample_dir.name
        gt_path = sample_dir / "gt.dsl"
        pred_path = None
        for name in ("pred_canonical.dsl", "pred.dsl", "pred.txt"):
            p = sample_dir / name
            if p.exists():
                pred_path = p
                break
        if gt_path is None or not gt_path.exists() or pred_path is None:
            rows.append({"sample_id": sid, "error": "missing_gt_or_pred"})
            continue

        gt_text = gt_path.read_text(encoding="utf-8")
        pred_text = pred_path.read_text(encoding="utf-8")
        gt_ops = _solid_op_count_from_dsl(gt_text)
        pred_ops = _solid_op_count_from_dsl(pred_text)
        gt_dsl_tokens = len(tokenizer.encode(gt_text, add_special_tokens=False))
        prediction_tokens = len(
            tokenizer.encode(pred_text, add_special_tokens=False)
        )
        parsed = False
        try:
            parse_dsl(extract_dsl_code(pred_text))
            parsed = True
        except Exception:
            parsed = False
        ratio = pred_ops / gt_ops if gt_ops > 0 else None
        rows.append(
            {
                "sample_id": sid,
                "max_new_tokens": max_new_tokens,
                "prediction_tokens": prediction_tokens,
                "gt_dsl_tokens": gt_dsl_tokens,
                "stop_reason": _infer_stop_reason(
                    pred_text, prediction_tokens, max_new_tokens, parsed
                ),
                "pred_parse_ok": parsed,
                "pred_ops": pred_ops,
                "gt_ops": gt_ops,
                "predicted_op_count_over_gt_op_count": ratio,
                "under_generation": pred_ops < gt_ops if gt_ops > 0 else False,
            }
        )
    return rows


def _correlation(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2:
        return None
    if np.std(xs) < 1e-12 or np.std(ys) < 1e-12:
        return None
    return float(np.corrcoef(xs, ys)[0, 1])


def _summarize_training(records: list[dict[str, Any]], cutoff_len: int) -> dict[str, Any]:
    ok = [r for r in records if "gt_dsl_tokens" in r]
    n = len(ok)
    trunc = sum(1 for r in ok if r["label_truncated"])
    return {
        "n_samples": n,
        "cutoff_len": cutoff_len,
        "label_truncation_rate_pct": round(_pct(trunc, n), 2),
        "label_truncated_count": trunc,
        "gt_dsl_tokens": _stats([float(r["gt_dsl_tokens"]) for r in ok]),
        "prompt_tokens": _stats([float(r["prompt_tokens"]) for r in ok]),
        "total_text_tokens": _stats([float(r["total_text_tokens"]) for r in ok]),
        "supervised_label_tokens": _stats(
            [float(r["supervised_label_tokens"]) for r in ok]
        ),
        "point_patches": _stats(
            [float(r["point_patches"]) for r in ok if r.get("point_patches") is not None]
        ),
        "effective_total_tokens": _stats(
            [
                float(r["effective_total_tokens"])
                for r in ok
                if r.get("effective_total_tokens") is not None
            ]
        ),
        "gt_ops": _stats([float(r["gt_ops"]) for r in ok]),
    }


def _summarize_decode(rows: list[dict[str, Any]], max_new_tokens: int) -> dict[str, Any]:
    ok = [r for r in rows if "prediction_tokens" in r]
    n = len(ok)
    stop_counts = Counter(r["stop_reason"] for r in ok)
    ratios = [
        float(r["predicted_op_count_over_gt_op_count"])
        for r in ok
        if r.get("predicted_op_count_over_gt_op_count") is not None
    ]
    gt_toks = [float(r["gt_dsl_tokens"]) for r in ok]
    pred_toks = [float(r["prediction_tokens"]) for r in ok]
    op_ratios = [
        float(r["predicted_op_count_over_gt_op_count"])
        for r in ok
        if r.get("predicted_op_count_over_gt_op_count") is not None
    ]
    corr = _correlation(gt_toks, op_ratios) if op_ratios else None
    return {
        "n_samples": n,
        "max_new_tokens": max_new_tokens,
        "stop_reason_counts": dict(stop_counts),
        "prediction_tokens": _stats(pred_toks),
        "gt_dsl_tokens": _stats(gt_toks),
        "mean_predicted_op_count_over_gt_op_count": float(np.mean(ratios))
        if ratios
        else None,
        "under_generation_rate_pct": round(
            _pct(sum(1 for r in ok if r.get("under_generation")), n), 2
        ),
        "gt_token_length_vs_op_ratio_pearson_r": corr,
    }


def _verdict(
    train_summary: dict[str, Any],
    decode_summaries: dict[str, dict[str, Any]],
    cutoff_len: int,
    max_new_tokens: int,
) -> dict[str, Any]:
    gt_p95 = train_summary["gt_dsl_tokens"]["p95"]
    trunc_rate = train_summary["label_truncation_rate_pct"]
    eff_p95 = (train_summary.get("effective_total_tokens") or {}).get("p95")

    train_ok = trunc_rate <= 1.0 and cutoff_len >= (gt_p95 or 0) + (
        train_summary["prompt_tokens"]["mean"] or 0
    )
    decode_issues = []
    for tag, ds in decode_summaries.items():
        pred_p95 = (ds.get("prediction_tokens") or {}).get("p95")
        gt_p95_dec = (ds.get("gt_dsl_tokens") or {}).get("p95")
        max_len_hits = ds.get("stop_reason_counts", {}).get("MAX_LENGTH", 0)
        if gt_p95_dec and max_new_tokens < gt_p95_dec:
            decode_issues.append(
                f"{tag}: max_new_tokens={max_new_tokens} < GT DSL p95={gt_p95_dec:.0f}"
            )
        if max_len_hits > 0:
            decode_issues.append(f"{tag}: {max_len_hits} samples hit MAX_LENGTH")
        if pred_p95 and gt_p95_dec and pred_p95 < gt_p95_dec * 0.5:
            decode_issues.append(
                f"{tag}: pred token p95 ({pred_p95:.0f}) << GT p95 ({gt_p95_dec:.0f})"
            )

    if trunc_rate > 5:
        recommendation = (
            f"DO NOT train 1K yet: label_truncation_rate={trunc_rate:.1f}% at cutoff_len={cutoff_len}. "
            f"Raise cutoff_len to cover GT DSL p95={gt_p95:.0f} + prompt (~54), or filter long samples."
        )
        root_cause = "TRAINING_LABEL_TRUNCATION"
    elif decode_summaries:
        eos_hits = sum(
            ds.get("stop_reason_counts", {}).get("EOS", 0)
            for ds in decode_summaries.values()
        )
        max_len_hits = sum(
            ds.get("stop_reason_counts", {}).get("MAX_LENGTH", 0)
            for ds in decode_summaries.values()
        )
        mean_ratio = np.mean(
            [
                ds.get("mean_predicted_op_count_over_gt_op_count") or 1.0
                for ds in decode_summaries.values()
            ]
        )
        if max_len_hits > 0 and gt_p95 and max_new_tokens < gt_p95:
            recommendation = (
                f"Training labels OK (truncation={trunc_rate:.1f}%), but decode budget too small: "
                f"max_new_tokens={max_new_tokens} < GT DSL p95={gt_p95:.0f}. "
                f"Raise to ≥4096 before eval. Also {max_len_hits} val samples already hit MAX_LENGTH."
            )
            root_cause = "DECODE_MAX_NEW_TOKENS"
        elif mean_ratio < 0.67 and eos_hits > max_len_hits:
            recommendation = (
                f"Length contract OK for training (truncation={trunc_rate:.1f}%, effective p95={eff_p95:.0f}). "
                f"Under-generation (pred/gt≈{mean_ratio:.2f}) is primarily early EOS ({eos_hits} stops) "
                f"not max_new_tokens ({max_len_hits} stops). Safe to proceed 1K with complexity-stratified split; "
                f"still raise max_new_tokens to ≥4096 for long GT (p95={gt_p95:.0f})."
            )
            root_cause = "EARLY_EOS_UNDER_GENERATION"
        elif decode_issues:
            recommendation = (
                "Training labels mostly intact, but decode contract is tight: "
                + "; ".join(decode_issues)
            )
            root_cause = "DECODE_MAX_NEW_TOKENS"
        else:
            recommendation = "Length contract looks OK for 1K training."
            root_cause = "OK"
    else:
        recommendation = "Length contract looks OK for 1K training (decode audit not run)."
        root_cause = "OK"

    return {
        "root_cause": root_cause,
        "recommendation": recommendation,
        "train_contract_ok": train_ok,
        "effective_total_p95": eff_p95,
        "gt_dsl_p95": gt_p95,
        "decode_issues": decode_issues,
    }


def _print_report(
    train_summary: dict[str, Any],
    decode_summaries: dict[str, dict[str, Any]],
    verdict: dict[str, Any],
) -> None:
    print("=== CAD_SEQUENCE_LENGTH_CONTRACT_AUDIT_V1 ===")
    print(f"Training samples: {train_summary['n_samples']}")
    print(f"cutoff_len={train_summary['cutoff_len']}")
    print(
        f"label_truncation_rate: {train_summary['label_truncation_rate_pct']:.1f}% "
        f"({train_summary['label_truncated_count']} samples)"
    )
    for key in (
        "gt_dsl_tokens",
        "prompt_tokens",
        "total_text_tokens",
        "supervised_label_tokens",
        "point_patches",
        "effective_total_tokens",
    ):
        s = train_summary.get(key) or {}
        if s.get("mean") is None:
            continue
        print(
            f"  {key}: mean={s['mean']:.0f} median={s['median']:.0f} "
            f"p95={s['p95']:.0f} max={s['max']:.0f}"
        )
    print()
    for tag, ds in decode_summaries.items():
        print(f"--- Decode: {tag} ---")
        print(f"  stop_reason: {ds.get('stop_reason_counts')}")
        pt = ds.get("prediction_tokens") or {}
        gt = ds.get("gt_dsl_tokens") or {}
        print(
            f"  pred_tokens mean={pt.get('mean', 0):.0f} p95={pt.get('p95', 0):.0f} | "
            f"gt_tokens p95={gt.get('p95', 0):.0f} | max_new_tokens={ds.get('max_new_tokens')}"
        )
        print(
            f"  pred/gt op ratio mean={ds.get('mean_predicted_op_count_over_gt_op_count')} "
            f"under-gen={ds.get('under_generation_rate_pct')}% "
            f"corr(gt_tokens, op_ratio)={ds.get('gt_token_length_vs_op_ratio_pearson_r')}"
        )
    print()
    print(f"ROOT CAUSE: {verdict['root_cause']}")
    print(f"VERDICT: {verdict['recommendation']}")


def main() -> int:
    ap = argparse.ArgumentParser(description="CAD sequence length contract audit v1")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--train-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD/train")
    ap.add_argument("--cutoff-len", type=int, default=4096)
    ap.add_argument("--max-new-tokens", type=int, default=2048)
    ap.add_argument("--num-bins", type=int, default=1280)
    ap.add_argument("--template", default="spatiallm_cad_llama")
    ap.add_argument(
        "--encoder-checkpoint",
        type=Path,
        default=SPATIALLM / "saves/deepcad_train100_canonical_ours/checkpoint-1000",
        help="Checkpoint for exact point encoder patch counts (GPU). Empty to skip.",
    )
    ap.add_argument(
        "--skip-encoder",
        action="store_true",
        help="Skip GPU encoder patch counts (faster label-only audit)",
    )
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--pred-dir", type=Path, action="append", default=None)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    sample_ids = _load_manifest_ids(args.manifest)
    encoder = _load_encoder(
        None
        if args.skip_encoder or not args.encoder_checkpoint.exists()
        else args.encoder_checkpoint,
        args.device,
    )

    print(f"Auditing {len(sample_ids)} training samples (cutoff_len={args.cutoff_len})...")
    train_records = audit_training_contract(
        sample_ids,
        args.train_dir,
        args.cutoff_len,
        args.num_bins,
        args.template,
        encoder,
    )
    train_summary = _summarize_training(train_records, args.cutoff_len)

    decode_summaries: dict[str, dict[str, Any]] = {}
    decode_records: dict[str, list[dict[str, Any]]] = {}
    if args.pred_dir:
        from transformers import AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(
            str(DEFAULT_TOKENIZER), trust_remote_code=True
        )
        for pred_root in args.pred_dir:
            tag = pred_root.name
            rows = audit_decode_contract(
                pred_root, tokenizer, args.max_new_tokens, args.train_dir
            )
            decode_records[tag] = rows
            decode_summaries[tag] = _summarize_decode(rows, args.max_new_tokens)

    verdict = _verdict(
        train_summary, decode_summaries, args.cutoff_len, args.max_new_tokens
    )
    _print_report(train_summary, decode_summaries, verdict)

    report = {
        "audit": "CAD_SEQUENCE_LENGTH_CONTRACT_AUDIT_V1",
        "manifest": str(args.manifest),
        "cutoff_len": args.cutoff_len,
        "max_new_tokens": args.max_new_tokens,
        "encoder_checkpoint": str(args.encoder_checkpoint)
        if encoder.model is not None
        else None,
        "training_summary": train_summary,
        "training_samples": train_records,
        "decode_summary": decode_summaries,
        "decode_samples": decode_records,
        "verdict": verdict,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path = args.out.with_suffix(".md")
    _write_markdown(md_path, train_summary, decode_summaries, verdict)
    print(f"\nReport: {args.out}\nMarkdown: {md_path}")
    return 0


def _write_markdown(
    path: Path,
    train_summary: dict[str, Any],
    decode_summaries: dict[str, dict[str, Any]],
    verdict: dict[str, Any],
) -> None:
    lines = [
        "# CAD_SEQUENCE_LENGTH_CONTRACT_AUDIT_V1",
        "",
        f"- cutoff_len: **{train_summary['cutoff_len']}**",
        f"- label truncation rate: **{train_summary['label_truncation_rate_pct']:.1f}%** "
        f"({train_summary['label_truncated_count']}/{train_summary['n_samples']})",
        "",
        "## Training token budget",
        "",
        "| Field | mean | median | p95 | max |",
        "|---|---:|---:|---:|---:|",
    ]
    for key, title in [
        ("gt_dsl_tokens", "GT DSL tokens"),
        ("prompt_tokens", "Prompt tokens (text)"),
        ("total_text_tokens", "Total text tokens (after cutoff)"),
        ("supervised_label_tokens", "Supervised label tokens"),
        ("point_patches", "Point encoder patches"),
        ("effective_total_tokens", "Effective total (text − 1 + patches)"),
    ]:
        s = train_summary.get(key) or {}
        if s.get("mean") is None:
            continue
        lines.append(
            f"| {title} | {s['mean']:.0f} | {s['median']:.0f} | {s['p95']:.0f} | {s['max']:.0f} |"
        )
    lines.extend(["", "## Decode contract", ""])
    for tag, ds in decode_summaries.items():
        pt, gt = ds.get("prediction_tokens") or {}, ds.get("gt_dsl_tokens") or {}
        lines.extend(
            [
                f"### {tag}",
                "",
                f"- stop_reason counts: `{ds.get('stop_reason_counts')}`",
                f"- pred tokens: mean={pt.get('mean', 0):.0f}, p95={pt.get('p95', 0):.0f}",
                f"- GT DSL tokens p95: {gt.get('p95', 0):.0f}",
                f"- max_new_tokens: {ds.get('max_new_tokens')}",
                f"- pred/gt op ratio mean: {ds.get('mean_predicted_op_count_over_gt_op_count')}",
                f"- corr(GT tokens, op ratio): {ds.get('gt_token_length_vs_op_ratio_pearson_r')}",
                "",
            ]
        )
    lines.extend(
        [
            "## Verdict",
            "",
            f"**Root cause:** {verdict['root_cause']}",
            "",
            verdict["recommendation"],
            "",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
