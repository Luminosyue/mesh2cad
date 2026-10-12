#!/usr/bin/env python3
"""Dump 10 real V3-1k SFT samples from files actually consumed at train time.

This is an alignment gate, not a config summary. It reconstructs the exact
user/assistant text from train_v3_smoke.encode(), loads the npy/npz/dsl that
one_forward() reads, and checks that every path ID is the same CAD.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
OUT = ROOT / "ours3/sft_sample_dump_v1"
TYPES = {0: "LINE", 1: "CIRCLE", 2: "ELLIPSE", 3: "BSPLINE"}
INSTRUCTION = (
    "Generate CAD construction program from the point cloud. "
    "Output only valid DSL assignments ending with result = ..."
)
SURFACE_MARKERS = "<|point_start|><|point_pad|><|point_end|>"
CURVE_MARKERS = (
    "<|reserved_special_token_6|><|reserved_special_token_8|>"
    "<|reserved_special_token_7|>"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sid_from_cad_id(cad_id: str) -> str:
    return cad_id.split("__", 1)[1]


def ids_in_path(path: str, sample_id: str) -> bool:
    return sample_id in Path(path).parts or Path(path).name.startswith(sample_id)


def npy_stats(arr: np.ndarray) -> dict:
    finite = np.isfinite(arr)
    return {
        "shape": list(arr.shape),
        "dtype": str(arr.dtype),
        "min": None if not finite.any() else float(np.nanmin(arr)),
        "max": None if not finite.any() else float(np.nanmax(arr)),
        "mean": None if not finite.any() else float(np.nanmean(arr)),
        "nan": int(np.isnan(arr).sum()) if np.issubdtype(arr.dtype, np.floating) else 0,
        "inf": int(np.isinf(arr).sum()) if np.issubdtype(arr.dtype, np.floating) else 0,
        "head": arr.reshape(arr.shape[0], -1)[:5].tolist() if arr.ndim >= 1 and arr.size else [],
    }


def curve_local_frame(xyz: np.ndarray) -> tuple[np.ndarray, float]:
    xyz = np.asarray(xyz, dtype=np.float64)
    center = xyz.mean(axis=0)
    scale = float(np.max(xyz.max(axis=0) - xyz.min(axis=0)))
    if scale < 1e-12:
        scale = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum()) or 1.0
    return ((xyz - center) / scale).astype(np.float32), float(scale)


def normalized_s(xyz: np.ndarray) -> np.ndarray:
    d = np.linalg.norm(np.diff(xyz, axis=0), axis=1)
    c = np.concatenate([[0.0], np.cumsum(d)])
    total = float(c[-1]) if c[-1] > 0 else 1.0
    return (c / total).astype(np.float32)[:, None]


def reconstruct_c2_32x7(z, i: int) -> np.ndarray:
    xyz = np.asarray(z["curve_xyz_normalized"][i], dtype=np.float64)
    tan = np.asarray(z["curve_tangent"][i], dtype=np.float32)
    local, _ = curve_local_frame(xyz)
    s = normalized_s(xyz.astype(np.float32))
    return np.concatenate([local, tan, s], axis=-1).astype(np.float32)


def extract_dsl_ops(dsl: str) -> list[str]:
    return re.findall(
        r"\b(Box|Extrude|ExtrudePolygon|Circle|Rectangle|Cut|Union|Sketch)\b", dsl
    )


def dump_one(row: dict, idx: int) -> dict:
    cad_id = row["cad_id"]
    sample_id = sid_from_cad_id(cad_id)
    dataset = row["source_dataset"]
    pack = ROOT / "cad_spatial_dataset" / ("DeepCAD" if dataset == "deepcad" else "Fusion360")
    train_dir = pack / "train" / sample_id
    pack_dir = pack / "geometry_pack_v1" / sample_id
    surface_path = Path(row["surface_input"])
    dsl_path = Path(row["target_dsl"])
    curve_npz = Path(row["m2_full_curves"])
    curve_tok = Path(row["m2_full_c2_tokens"])
    mesh_pack = pack_dir / "mesh.obj"
    mesh_train = train_dir / "model.obj"
    dsl_train = train_dir / "program_canonical.dsl"
    step_train = train_dir / "model.step"

    surface = np.load(surface_path)
    z = np.load(curve_npz)
    tokens = np.load(curve_tok)
    dsl = dsl_path.read_text()
    dsl_train_text = dsl_train.read_text() if dsl_train.is_file() else None
    meta_tok = json.loads(curve_tok.with_name("curve_tokens_meta.json").read_text())
    n_curves = int(z["num_curves"][0])
    sel = [int(i) for i in row["selected_m2_indices"]]
    k = int(row["k_valid"])

    curves = []
    for i in range(n_curves):
        feats = reconstruct_c2_32x7(z, i)
        curves.append(
            {
                "index": i,
                "edge_id": int(z["curve_edge_id"][i]),
                "type": TYPES[int(z["curve_type_id"][i])],
                "closed": bool(z["curve_is_closed"][i]),
                "length": float(z["curve_length"][i]),
                "length_normalized": float(z["curve_length_normalized"][i]),
                "input_32x7_shape": list(feats.shape),
                "input_32x7_schema": "local_xyz(3)+tangent(3)+s(1) from curve_xyz_normalized",
                "input_32x7_head": feats[:3].tolist(),
                "xyz_normalized_head": np.asarray(z["curve_xyz_normalized"][i][:3]).tolist(),
                "xyz_world_head": np.asarray(z["curve_xyz"][i][:3]).tolist(),
            }
        )

    kept_meta = meta_tok.get("curves", [])
    selected_curves = []
    for i in sel:
        if i >= len(kept_meta):
            selected_curves.append({"index": i, "ERROR": "index_out_of_range"})
            continue
        selected_curves.append(
            {
                "selected_index": i,
                "edge_id": kept_meta[i]["edge_id"],
                "type": kept_meta[i]["type"],
                "token_head": tokens[i, :8].tolist() if i < len(tokens) else None,
            }
        )

    prompt_user = SURFACE_MARKERS + CURVE_MARKERS + "\n" + INSTRUCTION
    llm_text = (
        "<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n"
        + prompt_user
        + "<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        + dsl
        + "<|eot_id|>"
    )

    path_fields = {
        "surface_input": row["surface_input"],
        "target_dsl": row["target_dsl"],
        "m2_full_curves": row["m2_full_curves"],
        "m2_full_c2_tokens": row["m2_full_c2_tokens"],
        "b1_full_input": row["b1_full_input"],
        "mesh_pack": str(mesh_pack),
        "mesh_train": str(mesh_train),
        "program_canonical": str(dsl_train),
        "model_step": str(step_train),
    }
    id_ok = {k: ids_in_path(v, sample_id) for k, v in path_fields.items()}
    exists = {k: Path(v).is_file() for k, v in path_fields.items()}
    dsl_sha = sha256_file(dsl_path)
    issues = []
    if not all(id_ok.values()):
        issues.append("PATH_ID_MISMATCH:" + ",".join(k for k, v in id_ok.items() if not v))
    if not all(exists.values()):
        issues.append("MISSING:" + ",".join(k for k, v in exists.items() if not v))
    if dsl_sha != row["target_dsl_sha256"]:
        issues.append("DSL_SHA_RECORD_MISMATCH")
    if dsl_train_text is not None and dsl != dsl_train_text:
        issues.append("CAD_TARGET_NE_PROGRAM_CANONICAL")
    if k != len(sel):
        issues.append(f"K_VALID_NE_SELECTED {k} vs {len(sel)}")
    if max(sel, default=-1) >= len(tokens):
        issues.append("SELECTED_M2_INDEX_OOB")
    if tokens.shape[0] != len(kept_meta):
        issues.append("TOKEN_META_COUNT_MISMATCH")
    if n_curves != tokens.shape[0] and not meta_tok.get("truncated"):
        # tokens may be sharp-only / length-ranked subset
        pass
    if meta_tok.get("sample_id") != sample_id:
        issues.append("CURVE_TOKEN_META_SAMPLE_ID_MISMATCH")

    return {
        "dump_index": idx,
        "sample_id": sample_id,
        "cad_id": cad_id,
        "split": row["split"],
        "source_dataset": dataset,
        "TEXT_INSTRUCTION": INSTRUCTION,
        "SURFACE_INPUT": {
            "path": str(surface_path),
            "exists": surface_path.is_file(),
            **npy_stats(surface),
            "schema": "[xyz(3), normal(3)]  NO edge_score; geometry_pack_v1",
            "note": "Train-time Sonata sees CAD_SURFACE_POINTS=4096 subsample of this 8192x6.",
        },
        "SURFACE_TOKENS_AFTER_ENCODER": {
            "stored_on_disk": False,
            "computed_at": "train_v3_smoke.one_forward → frozen Sonata + point_proj",
            "reason": "surface tokens are not serialized; only raw surface_points.npy is stored",
        },
        "CURVE_INPUT": {
            "path": str(curve_npz),
            "n_curves_in_npz": n_curves,
            "schema_npz": "curve_xyz_normalized (32,3) + curve_tangent (32,3) → C2 32x7",
            "type_counts": dict(Counter(c["type"] for c in curves)),
            "curves": curves,
        },
        "CURVE_TOKENS_AFTER_ENCODER": {
            "path": str(curve_tok),
            "shape": list(tokens.shape),
            "dtype": str(tokens.dtype),
            "min": float(tokens.min()),
            "max": float(tokens.max()),
            "hidden_dim": int(tokens.shape[1]) if tokens.ndim == 2 else None,
            "n_kept": int(meta_tok["n_curves_kept"]),
            "truncated": bool(meta_tok.get("truncated")),
            "type_counts": meta_tok.get("type_counts"),
            "selected_m2_indices": sel,
            "k_valid_fed_to_adapter": k,
            "selected_curves": selected_curves,
            "head_token0_8d": tokens[0, :8].tolist() if len(tokens) else [],
        },
        "FINAL_LLM_INPUT": {
            "actual_markers_not_SURFACE_START": True,
            "surface_slot": SURFACE_MARKERS,
            "curve_slot": CURVE_MARKERS,
            "user_text": prompt_user,
            "full_text_with_gt": llm_text,
            "splice": (
                "At train time <|point_pad|> is replaced by Sonata surface embeddings; "
                "<|reserved_special_token_8|> is replaced by GeometryPrefixAdapter "
                "summary tokens (8) over the selected K C2 tokens. Raw 32x7 is NOT in the LLM sequence."
            ),
        },
        "GT_OUTPUT": {
            "path": str(dsl_path),
            "sha256": dsl_sha,
            "record_sha256": row["target_dsl_sha256"],
            "chars": len(dsl),
            "ops": extract_dsl_ops(dsl),
            "record_operation_names": row["operation_names"],
            "text": dsl,
            "ends_with_result": "result =" in dsl,
        },
        "ALIGNMENT": {
            "path_contains_sample_id": id_ok,
            "files_exist": exists,
            "cad_target_equals_program_canonical": dsl_train_text == dsl if dsl_train_text is not None else None,
            "dsl_sha_matches_record": dsl_sha == row["target_dsl_sha256"],
            "mesh_pack_exists": mesh_pack.is_file(),
            "mesh_train_exists": mesh_train.is_file(),
            "issues": issues,
            "PASS": not issues,
        },
        "paths": path_fields,
    }


def audit_all(records: list[dict]) -> dict:
    bad = []
    for row in records:
        sample_id = sid_from_cad_id(row["cad_id"])
        checks = {
            "surface": ids_in_path(row["surface_input"], sample_id),
            "dsl": ids_in_path(row["target_dsl"], sample_id),
            "curves": ids_in_path(row["m2_full_curves"], sample_id),
            "tokens": ids_in_path(row["m2_full_c2_tokens"], sample_id),
            "b1": ids_in_path(row["b1_full_input"], sample_id),
        }
        if not all(checks.values()):
            bad.append({"cad_id": row["cad_id"], "checks": checks})
            continue
        dsl = Path(row["target_dsl"])
        if dsl.is_file() and sha256_file(dsl) != row["target_dsl_sha256"]:
            bad.append({"cad_id": row["cad_id"], "checks": {"dsl_sha": False}})
        train_dsl = (
            ROOT
            / "cad_spatial_dataset"
            / ("DeepCAD" if dataset_of(row) == "deepcad" else "Fusion360")
            / "train"
            / sample_id
            / "program_canonical.dsl"
        )
        if dsl.is_file() and train_dsl.is_file() and dsl.read_text() != train_dsl.read_text():
            bad.append({"cad_id": row["cad_id"], "checks": {"dsl_copy": False}})
    return {"n": len(records), "n_bad": len(bad), "bad": bad[:20]}


def dataset_of(row: dict) -> str:
    return row["source_dataset"]


def main() -> None:
    payload = json.loads((DATA / "v3_1k_train.json").read_text())
    records = payload["records"]
    rng = random.Random(42)
    picked = rng.sample(records, 10)
    OUT.mkdir(parents=True, exist_ok=True)
    dumps = [dump_one(row, i) for i, row in enumerate(picked)]
    full_audit = audit_all(records)
    summary = {
        "what_this_is": "V3-1k SpatialLM SFT (surface + frozen C2 curve tokens → CAD DSL)",
        "what_this_is_not": "C2_DORA_TRAINSET_V1.jsonl is curve-encoder training, not CAD SFT",
        "train_json": str(DATA / "v3_1k_train.json"),
        "n_train": len(records),
        "seed": 42,
        "n_dumped": 10,
        "n_dump_pass": sum(1 for d in dumps if d["ALIGNMENT"]["PASS"]),
        "n_dump_fail": sum(1 for d in dumps if not d["ALIGNMENT"]["PASS"]),
        "failed_ids": [d["cad_id"] for d in dumps if not d["ALIGNMENT"]["PASS"]],
        "full_train800_id_audit": full_audit,
        "real_llm_markers": {
            "surface": SURFACE_MARKERS,
            "curve_second_stream": CURVE_MARKERS,
            "not_used": ["<SURFACE_START>", "<CURVE_START>"],
        },
        "samples": [
            {
                "cad_id": d["cad_id"],
                "n_surface": d["SURFACE_INPUT"]["shape"],
                "n_curves_npz": d["CURVE_INPUT"]["n_curves_in_npz"],
                "n_curve_tokens": d["CURVE_TOKENS_AFTER_ENCODER"]["shape"],
                "k_valid": d["CURVE_TOKENS_AFTER_ENCODER"]["k_valid_fed_to_adapter"],
                "dsl_ops": d["GT_OUTPUT"]["ops"],
                "PASS": d["ALIGNMENT"]["PASS"],
                "issues": d["ALIGNMENT"]["issues"],
            }
            for d in dumps
        ],
    }
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    for d in dumps:
        (OUT / f"{d['cad_id']}.json").write_text(json.dumps(d, indent=2) + "\n")
        (OUT / f"{d['cad_id']}.llm_input.txt").write_text(d["FINAL_LLM_INPUT"]["full_text_with_gt"])
        (OUT / f"{d['cad_id']}.gt.dsl").write_text(d["GT_OUTPUT"]["text"])
    print(json.dumps({k: summary[k] for k in summary if k != "samples"}, indent=2))
    print("DUMPED", [d["cad_id"] for d in dumps])
    for d in dumps:
        print(
            f"{d['cad_id']} PASS={d['ALIGNMENT']['PASS']} "
            f"surf={d['SURFACE_INPUT']['shape']} "
            f"curves={d['CURVE_INPUT']['n_curves_in_npz']} "
            f"tokens={d['CURVE_TOKENS_AFTER_ENCODER']['shape']} "
            f"k={d['CURVE_TOKENS_AFTER_ENCODER']['k_valid_fed_to_adapter']} "
            f"ops={d['GT_OUTPUT']['ops']} issues={d['ALIGNMENT']['issues']}"
        )


if __name__ == "__main__":
    main()
