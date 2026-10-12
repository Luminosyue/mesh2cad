#!/usr/bin/env python3
"""Build DEEPCAD_1K_CANONICAL_V1 cohort + complexity-stratified split.

Steps:
  1. Start from manifest_train1000 (1000 QA-passed samples).
  2. Replace label-truncated samples (cutoff_len=4096) with QA-passed backups.
  3. Verify label_truncated == 0 for all 1000.
  4. Complexity-stratified split: train=800, val=100, test=100.
  5. Write manifest_train1k_v1.json + split_train1k_complexity_seed42.json.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "SpatialLM"))
sys.path.insert(0, str(ROOT / "scripts" / "deepcad"))

from audit_program_complexity import analyze_dsl  # noqa: E402
from audit_sequence_length_contract import (  # noqa: E402
    EncoderCache,
    _load_manifest_ids,
    audit_training_contract,
)
from create_spatiallm_cad_dataset import _load_dsl_label  # noqa: E402

DEFAULT_MANIFEST = ROOT / "cad_spatial_dataset/DeepCAD/manifest_train1000.json"
DEFAULT_OUT_MANIFEST = ROOT / "cad_spatial_dataset/DeepCAD/manifest_train1k_v1.json"
DEFAULT_SPLIT = ROOT / "cad_spatial_dataset/DeepCAD/split_train1k_complexity_seed42.json"
CUTOFF_LEN = 4096


@dataclass
class SampleMeta:
    sample_id: str
    gt_ops: int
    gt_dsl_tokens: int
    cut_count: int
    union_count: int
    extrude_polygon_count: int
    profile_vertex_count: int
    label_truncated: bool = False
    op_bucket: str = ""
    token_bucket: str = ""
    profile_bucket: str = ""
    has_cut: bool = False
    has_union: bool = False


def _op_bucket(op_count: int) -> str:
    if op_count <= 1:
        return "1-op"
    if op_count == 2:
        return "2-op"
    if op_count == 3:
        return "3-op"
    return "4+-op"


def _tertile_bucket(value: float, p33: float, p66: float, labels: tuple[str, str, str]) -> str:
    if value <= p33:
        return labels[0]
    if value <= p66:
        return labels[1]
    return labels[2]


def _qa_passed_ids(train_dir: Path) -> list[str]:
    out: list[str] = []
    for p in sorted(train_dir.iterdir()):
        if not p.is_dir():
            continue
        qa = p / "qa.json"
        if not qa.exists():
            continue
        if json.loads(qa.read_text(encoding="utf-8")).get("passed"):
            if _is_canonical_complete(p):
                out.append(p.name)
    return out


def _is_canonical_complete(sample_dir: Path) -> bool:
    required = (
        "features_canonical.npy",
        "program_canonical.dsl",
        "coordinate_transform.json",
        "meta.json",
    )
    return all((sample_dir / f).exists() for f in required)


def _load_sample_meta(sample_id: str, train_dir: Path, audit_rec: dict | None = None) -> SampleMeta:
    dsl_path = train_dir / sample_id / "program_canonical.dsl"
    dsl = _load_dsl_label(dsl_path)
    feat = analyze_dsl(dsl)
    gt_ops = int(feat["op_count"])
    gt_dsl_tokens = int(audit_rec["gt_dsl_tokens"]) if audit_rec else 0
    if audit_rec is None:
        gt_dsl_tokens = 0  # filled later if needed
    return SampleMeta(
        sample_id=sample_id,
        gt_ops=gt_ops,
        gt_dsl_tokens=gt_dsl_tokens,
        cut_count=int(feat["cut_count"]),
        union_count=int(feat["union_count"]),
        extrude_polygon_count=int(feat["extrude_polygon_count"]),
        profile_vertex_count=int(feat["profile_vertex_count"]),
        label_truncated=bool(audit_rec.get("label_truncated")) if audit_rec else False,
        op_bucket=_op_bucket(gt_ops),
        has_cut=feat["cut_count"] > 0,
        has_union=feat["union_count"] > 0,
    )


def _audit_ids(sample_ids: list[str], train_dir: Path, cutoff_len: int) -> dict[str, dict]:
    from spatiallm.tuner.data.template import TEMPLATES

    TEMPLATES.clear()
    records = audit_training_contract(
        sample_ids,
        train_dir,
        cutoff_len,
        num_bins=1280,
        template_name="spatiallm_cad_llama",
        encoder=EncoderCache(),
    )
    return {r["sample_id"]: r for r in records if "sample_id" in r}


def _pick_replacements(
    removed: list[str],
    removed_meta: list[SampleMeta],
    pool_ids: list[str],
    pool_audit: dict[str, dict],
    rng: random.Random,
) -> list[str]:
    """Greedy op-count matching from non-truncated QA-passed pool."""
    candidates = [
        sid
        for sid in pool_ids
        if sid not in removed and not pool_audit.get(sid, {}).get("label_truncated", True)
    ]
    cand_meta = []
    for sid in candidates:
        rec = pool_audit[sid]
        m = _load_sample_meta(sid, ROOT / "cad_spatial_dataset/DeepCAD/train", rec)
        cand_meta.append(m)
    cand_meta.sort(key=lambda m: (-m.gt_ops, -m.gt_dsl_tokens))

    picked: list[str] = []
    used: set[str] = set()
    targets = sorted([m.gt_ops for m in removed_meta], reverse=True)
    for target_ops in targets:
        best = None
        for m in cand_meta:
            if m.sample_id in used:
                continue
            if m.gt_ops >= max(1, target_ops - 2):
                best = m.sample_id
                break
        if best is None:
            for m in cand_meta:
                if m.sample_id not in used:
                    best = m.sample_id
                    break
        if best:
            picked.append(best)
            used.add(best)
    if len(picked) < len(removed):
        rest = [m.sample_id for m in cand_meta if m.sample_id not in used]
        rng.shuffle(rest)
        picked.extend(rest[: len(removed) - len(picked)])
    return picked[: len(removed)]


def _assign_buckets(metas: list[SampleMeta]) -> None:
    tok_vals = [m.gt_dsl_tokens for m in metas]
    prof_vals = [m.profile_vertex_count for m in metas]
    p33_t, p66_t = np.percentile(tok_vals, [33.33, 66.67])
    p33_p, p66_p = np.percentile(prof_vals, [33.33, 66.67])
    for m in metas:
        m.token_bucket = _tertile_bucket(
            m.gt_dsl_tokens, p33_t, p66_t, ("short", "medium", "long")
        )
        m.profile_bucket = _tertile_bucket(
            m.profile_vertex_count, p33_p, p66_p, ("low", "med", "high")
        )


def _stratum_key(m: SampleMeta, *, coarse: bool = False) -> str:
    if coarse:
        return f"{m.op_bucket}|{m.token_bucket}"
    return "|".join(
        [
            m.op_bucket,
            m.token_bucket,
            "cut" if m.has_cut else "nocut",
            "union" if m.has_union else "nounion",
            m.profile_bucket,
        ]
    )


def _hamilton_allocate(k: int, train_n: int, val_n: int, test_n: int, total: int) -> tuple[int, int, int]:
    """Largest-remainder allocation of k items into train/val/test."""
    quotas = {
        "train": k * train_n / total,
        "val": k * val_n / total,
        "test": k * test_n / total,
    }
    base = {key: int(q) for key, q in quotas.items()}
    rem = k - sum(base.values())
    order = sorted(quotas.keys(), key=lambda key: quotas[key] - base[key], reverse=True)
    for i in range(rem):
        base[order[i % 3]] += 1
    return base["train"], base["val"], base["test"]


def _complexity_split(
    metas: list[SampleMeta],
    train_n: int,
    val_n: int,
    test_n: int,
    seed: int,
) -> tuple[list[str], list[str], list[str]]:
    assert train_n + val_n + test_n == len(metas)
    rng = random.Random(seed)
    meta_by_id = {m.sample_id: m for m in metas}
    ids = [m.sample_id for m in metas]
    labels = [_stratum_key(m, coarse=True) for m in metas]

    try:
        from sklearn.model_selection import StratifiedShuffleSplit

        idx = np.arange(len(ids))
        sss_test = StratifiedShuffleSplit(n_splits=1, test_size=test_n, random_state=seed)
        train_val_idx, test_idx = next(sss_test.split(idx, labels))
        labels_tv = [labels[i] for i in train_val_idx]
        sss_val = StratifiedShuffleSplit(
            n_splits=1, test_size=val_n / max(len(train_val_idx), 1), random_state=seed
        )
        tr_local, val_local = next(sss_val.split(train_val_idx, labels_tv))
        train_ids = [ids[i] for i in train_val_idx[tr_local]]
        val_ids = [ids[i] for i in train_val_idx[val_local]]
        test_ids = [ids[i] for i in test_idx]
    except Exception:
        # Fallback: round-robin merge of shuffled strata then slice
        by_stratum: dict[str, list[str]] = defaultdict(list)
        for m in metas:
            by_stratum[_stratum_key(m)].append(m.sample_id)
        for sids in by_stratum.values():
            rng.shuffle(sids)
        merged: list[str] = []
        strata_lists = list(by_stratum.values())
        pos = 0
        while len(merged) < len(metas):
            for sl in strata_lists:
                if pos < len(sl):
                    merged.append(sl[pos])
            pos += 1
        train_ids = merged[:train_n]
        val_ids = merged[train_n : train_n + val_n]
        test_ids = merged[train_n + val_n :]

    meta_by_id = {m.sample_id: m for m in metas}

    def _swap_train_test(train: list[str], test: list[str], src: str, dst: str) -> None:
        ti = train.index(src)
        te = test.index(dst)
        train[ti] = dst
        test[te] = src

    # Boost 4+-op in test; rebalance 1-op overflow back to train
    min_4op = max(28, test_n // 4)
    test_4 = sum(1 for sid in test_ids if meta_by_id[sid].op_bucket == "4+-op")
    while test_4 < min_4op:
        train_4 = [sid for sid in train_ids if meta_by_id[sid].op_bucket == "4+-op"]
        test_1 = [sid for sid in test_ids if meta_by_id[sid].op_bucket == "1-op"]
        if not train_4 or not test_1:
            break
        _swap_train_test(train_ids, test_ids, train_4[0], test_1[0])
        test_4 += 1

    max_1op_test = int(test_n * 0.38)
    while sum(1 for sid in test_ids if meta_by_id[sid].op_bucket == "1-op") > max_1op_test:
        test_1 = next(sid for sid in test_ids if meta_by_id[sid].op_bucket == "1-op")
        donors = [
            sid
            for sid in train_ids
            if meta_by_id[sid].op_bucket in ("2-op", "3-op", "4+-op")
        ]
        if not donors:
            break
        _swap_train_test(train_ids, test_ids, donors[0], test_1)

    assert len(train_ids) == train_n
    assert len(val_ids) == val_n
    assert len(test_ids) == test_n
    assert len(set(train_ids) | set(val_ids) | set(test_ids)) == len(metas)
    return train_ids, val_ids, test_ids


def _split_stats(ids: list[str], meta_by_id: dict[str, SampleMeta]) -> dict[str, Any]:
    metas = [meta_by_id[sid] for sid in ids]
    op_c = Counter(m.op_bucket for m in metas)
    tok_c = Counter(m.token_bucket for m in metas)
    return {
        "n": len(ids),
        "op_bucket": dict(op_c),
        "token_bucket": dict(tok_c),
        "has_cut_pct": round(100.0 * sum(m.has_cut for m in metas) / max(len(metas), 1), 1),
        "has_union_pct": round(100.0 * sum(m.has_union for m in metas) / max(len(metas), 1), 1),
        "mean_gt_ops": round(float(np.mean([m.gt_ops for m in metas])), 2),
        "mean_gt_dsl_tokens": round(float(np.mean([m.gt_dsl_tokens for m in metas])), 1),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build DeepCAD-1K complexity split")
    ap.add_argument("--manifest-in", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--manifest-out", type=Path, default=DEFAULT_OUT_MANIFEST)
    ap.add_argument("--split-out", type=Path, default=DEFAULT_SPLIT)
    ap.add_argument("--train-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD/train")
    ap.add_argument("--cutoff-len", type=int, default=CUTOFF_LEN)
    ap.add_argument("--train-n", type=int, default=800)
    ap.add_argument("--val-n", type=int, default=100)
    ap.add_argument("--test-n", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = random.Random(args.seed)
    base_ids = _load_manifest_ids(args.manifest_in)
    print(f"Base cohort: {len(base_ids)} samples")

    audit = _audit_ids(base_ids, args.train_dir, args.cutoff_len)
    truncated = [sid for sid in base_ids if audit.get(sid, {}).get("label_truncated")]
    print(f"Truncated at cutoff={args.cutoff_len}: {len(truncated)}")
    if truncated:
        print("  ", truncated)

    removed_meta = [
        _load_sample_meta(sid, args.train_dir, audit.get(sid)) for sid in truncated
    ]
    pool = [sid for sid in _qa_passed_ids(args.train_dir) if sid not in base_ids]
    pool_audit = _audit_ids(pool, args.train_dir, args.cutoff_len)
    replacements = _pick_replacements(truncated, removed_meta, pool, pool_audit, rng)
    kept_set = set(base_ids) - set(truncated)
    replacements = [s for s in replacements if s not in kept_set]
    if len(replacements) < len(truncated):
        extra = [
            s
            for s in pool
            if s not in kept_set
            and s not in replacements
            and not pool_audit.get(s, {}).get("label_truncated")
        ]
        rng.shuffle(extra)
        replacements.extend(extra[: len(truncated) - len(replacements)])
    print(f"Replacements: {replacements}")

    final_ids = list(kept_set) + replacements[: len(truncated)]
    assert len(final_ids) == len(base_ids)
    assert len(set(final_ids)) == len(final_ids)

    final_audit = _audit_ids(final_ids, args.train_dir, args.cutoff_len)
    trunc_final = [sid for sid in final_ids if final_audit[sid].get("label_truncated")]
    if trunc_final:
        print(f"ERROR: still truncated after replacement: {trunc_final}")
        return 1

    metas = [_load_sample_meta(sid, args.train_dir, final_audit[sid]) for sid in final_ids]
    _assign_buckets(metas)
    meta_by_id = {m.sample_id: m for m in metas}

    train_ids, val_ids, test_ids = _complexity_split(
        metas, args.train_n, args.val_n, args.test_n, args.seed
    )

    manifest_out = {
        "name": "DEEPCAD_1K_CANONICAL_V1",
        "selection": "manifest_train1000 minus truncated + QA-passed replacements",
        "n": len(final_ids),
        "cutoff_len": args.cutoff_len,
        "label_truncated_count": 0,
        "replaced": dict(zip(truncated, replacements)),
        "sample_ids": sorted(final_ids),
    }
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_out.write_text(json.dumps(manifest_out, indent=2) + "\n", encoding="utf-8")

    split_doc = {
        "name": "split_train1k_complexity_seed42",
        "seed": args.seed,
        "scheme": "complexity-stratified",
        "train_n": args.train_n,
        "val_n": args.val_n,
        "test_n": args.test_n,
        "stratify_fields": [
            "op_count (1/2/3/4+)",
            "gt_dsl_tokens (short/medium/long)",
            "has_cut",
            "has_union",
            "profile_vertex_count (low/med/high)",
        ],
        "manifest": str(args.manifest_out),
        "train_ids": train_ids,
        "val_ids": val_ids,
        "test_ids": test_ids,
        "stats": {
            "train": _split_stats(train_ids, meta_by_id),
            "val": _split_stats(val_ids, meta_by_id),
            "test": _split_stats(test_ids, meta_by_id),
        },
    }
    args.split_out.write_text(json.dumps(split_doc, indent=2) + "\n", encoding="utf-8")

    print("\n=== DEEPCAD_1K_CANONICAL_V1 ===")
    print(f"Manifest: {args.manifest_out}")
    print(f"Split:    {args.split_out}")
    print(f"label_truncated: 0 / {len(final_ids)}")
    print("Split stats:")
    print(json.dumps(split_doc["stats"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
