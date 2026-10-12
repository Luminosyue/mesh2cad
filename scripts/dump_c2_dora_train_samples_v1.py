#!/usr/bin/env python3
"""Dump real C2_DORA train samples from train800_build_v1.

This is curve-encoder supervision, not SpatialLM SFT. There is no instruction
and no CAD DSL target. The trainer (c2_dora_fitted_v1_train.py) reads:

  x      = curve_c2/curve_inputs.npy[dora_curve_index]   # [32,7]
  loglen = curve_c2/curve_lengths.npy[dora_curve_index]
  y      = gt_curve_type from MATCHED_1_TO_1 B-Rep edge
  param  = gt_world_parameters expressed in the fitted-curve local frame
"""
from __future__ import annotations

import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DATA = ROOT / "ours3/dora_fitted_curve_dataset_v1/train800_build_v1"
COHORT = ROOT / "ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl"
OUT = ROOT / "ours3/c2_dora_sample_dump_v1"
TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")


def sid(cad_id: str) -> str:
    return cad_id.split("__", 1)[1]


def npy_head(arr: np.ndarray, n: int = 5):
    return np.asarray(arr[:n]).tolist()


def load_cohort() -> dict:
    out = {}
    for line in COHORT.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out[row["cad_id"]] = row
    return out


def dump_cad(cad_id: str, entries: list[dict], split_set: dict, cohort: dict) -> dict:
    cdir = DATA / "cad" / cad_id
    sample_id = sid(cad_id)
    src = Path(
        "/data/home/cuiyuehan/project/mesh2cad/cad_spatial_dataset/DeepCAD/train"
    ) / sample_id
    inp = np.load(cdir / "curve_c2/curve_inputs.npy")
    length = np.load(cdir / "curve_c2/curve_lengths.npy")
    anchors = np.load(cdir / "curve_c2/anchors.npy")
    meta = json.loads((cdir / "curve_c2/meta.json").read_text())
    fits = json.loads((cdir / "dora/fitted_curves.json").read_text())["curves"]
    corr = json.loads((cdir / "correspondence.json").read_text())
    gt = json.loads((cdir / "gt_brep_curves.json").read_text())
    gt_by = {int(c["edge_id"]): c for c in gt["curves"]}
    dsl_path = src / "program_canonical.dsl"
    mesh_path = src / "model.obj"
    step_path = src / "model.step"
    dsl = dsl_path.read_text() if dsl_path.is_file() else None
    coh = cohort.get(cad_id, {})
    issues = []
    declared = entries[0]["cad_split"] if entries else None
    if declared != split_set.get(cad_id):
        issues.append(f"SPLIT_MISMATCH jsonl={declared} split_file={split_set.get(cad_id)}")
    if meta.get("cad_id") != cad_id:
        issues.append(f"META_CAD_ID {meta.get('cad_id')}")
    if gt.get("cad_id") not in (cad_id, sample_id):
        issues.append(f"GT_CAD_ID {gt.get('cad_id')}")
    if fits and False:
        pass
    if int(inp.shape[0]) != len(fits):
        issues.append(f"INPUT_FIT_COUNT {inp.shape[0]} vs {len(fits)}")
    if inp.ndim != 3 or inp.shape[1:] != (32, 7):
        issues.append(f"BAD_INPUT_SHAPE {inp.shape}")
    if not mesh_path.is_file():
        issues.append("MISSING_SOURCE_MESH")
    if not dsl_path.is_file():
        issues.append("MISSING_SOURCE_DSL")
    if coh and Path(coh["assets"]["model_obj"]["path"]).name != "model.obj":
        issues.append("COHORT_OBJ_NAME")
    if coh and sample_id not in coh["assets"]["model_obj"]["path"]:
        issues.append("COHORT_PATH_ID_MISMATCH")

    curves = []
    for e in entries:
        i = int(e["dora_curve_index"])
        gid = int(e["gt_edge_id"])
        rec = next(
            (
                r
                for r in corr["records"]
                if int(r["dora_curve_index"]) == i
            ),
            None,
        )
        g = gt_by.get(gid)
        local = {
            "sample_index": e["sample_index"],
            "dora_curve_index": i,
            "gt_edge_id": gid,
            "cad_split": e["cad_split"],
            "fit_type": e["fit_type"],
            "gt_curve_type": e["gt_curve_type"],
            "gt_world_parameters": e["gt_world_parameters"],
            "correspondence_metrics": e["correspondence_metrics"],
            "correspondence_classification": None if rec is None else rec["classification"],
            "INPUT_32x7": {
                "shape": list(inp[i].shape) if i < len(inp) else None,
                "dtype": str(inp.dtype),
                "schema": "[local_xyz(3), tangent(3), s(1)]",
                "min": None if i >= len(inp) else float(inp[i].min()),
                "max": None if i >= len(inp) else float(inp[i].max()),
                "head5": None if i >= len(inp) else npy_head(inp[i], 5),
            },
            "log_length": None if i >= len(length) else float(length[i]),
            "anchor": None if i >= len(anchors) else anchors[i].tolist(),
            "fitted_curve": None if i >= len(fits) else {
                "type": fits[i].get("type"),
                "chain_id": fits[i].get("chain_id"),
                "curve_length": fits[i].get("curve_length"),
                "normalized_residual": fits[i].get("normalized_residual"),
            },
            "gt_brep": None
            if g is None
            else {
                "curve_type": g["curve_type"],
                "edge_id": g["edge_id"],
                "start_point": g.get("start_point"),
                "end_point": g.get("end_point"),
            },
        }
        if i >= len(inp):
            issues.append(f"DORA_INDEX_OOB {i} n_input={len(inp)}")
        if rec is None:
            issues.append(f"NO_CORRESPONDENCE_ROW index={i}")
        elif rec["classification"] != "MATCHED_1_TO_1":
            issues.append(f"NOT_MATCHED_1_TO_1 index={i} {rec['classification']}")
        if rec is not None and rec.get("gt_curve_id") != gid:
            issues.append(f"GT_EDGE_JSONL_NE_CORR index={i} jsonl={gid} corr={rec.get('gt_curve_id')}")
        if g is None:
            issues.append(f"GT_EDGE_MISSING {gid}")
        elif g["curve_type"] != e["gt_curve_type"] and not (
            g["curve_type"] == "BEZIER" and e["gt_curve_type"] == "BSPLINE"
        ):
            issues.append(f"GT_TYPE_MISMATCH jsonl={e['gt_curve_type']} brep={g['curve_type']}")
        if e["cad_id"] != cad_id:
            issues.append("JSONL_CAD_ID_NE_GROUP")
        if e["source_id"] != sample_id:
            issues.append(f"SOURCE_ID {e['source_id']}")
        curves.append(local)

    return {
        "cad_id": cad_id,
        "source_id": sample_id,
        "cad_split": declared,
        "n_train_curves": len(entries),
        "n_dora_fitted": len(fits),
        "n_gt_brep": len(gt["curves"]),
        "n_corr": len(corr["records"]),
        "input_shape_cad": list(inp.shape),
        "input_schema": meta.get("input_schema"),
        "source": "Dora fitted continuous curves only; GT is B-Rep edge type+params",
        "NOT_IN_THIS_DATASET": {
            "text_instruction": False,
            "surface_npy": False,
            "surface_tokens": False,
            "curve_tokens_256": False,
            "cad_dsl_as_training_target": False,
            "reason": "C2_DORA is curve-encoder supervision, not SpatialLM SFT",
        },
        "SOURCE_CAD_FOR_ALIGNMENT": {
            "mesh": str(mesh_path),
            "mesh_exists": mesh_path.is_file(),
            "step": str(step_path),
            "dsl": str(dsl_path),
            "dsl_exists": dsl_path.is_file(),
            "dsl_text": dsl,
            "cohort_model_obj": None if not coh else coh["assets"]["model_obj"]["path"],
            "cohort_step": None if not coh else coh["assets"]["model_step"]["path"],
            "cohort_dsl": None if not coh else coh["assets"]["program_dsl"]["path"],
        },
        "TRAINER_SEES": {
            "x": "[32,7] from curve_inputs.npy[dora_curve_index]",
            "scale_feat": "log(polyline_length) from curve_lengths.npy",
            "type_id": "gt_curve_type in {LINE,CIRCLE,ELLIPSE,BSPLINE}",
            "param": "gt_world_parameters mapped into fitted-curve local frame",
        },
        "type_counts": dict(Counter(e["gt_curve_type"] for e in entries)),
        "fit_type_counts": dict(Counter(e["fit_type"] for e in entries)),
        "curves": curves,
        "issues": issues,
        "PASS": not issues,
    }


def audit_all(entries: list[dict], split: dict, cohort: dict) -> dict:
    train = set(split["train_cad_ids"])
    val = set(split["val_cad_ids"])
    issues = []
    if train & val:
        issues.append({"CAD_IN_BOTH_SPLITS": sorted(train & val)[:10]})
    if len(train) != 720 or len(val) != 80:
        issues.append({"SPLIT_COUNT": (len(train), len(val))})
    by = defaultdict(list)
    for e in entries:
        by[e["cad_id"]].append(e)
    split_mismatch = []
    oob = []
    type_mismatch = []
    not_matched = []
    missing_src = []
    for cad, es in by.items():
        declared = {e["cad_split"] for e in es}
        expect = "train" if cad in train else "val" if cad in val else None
        if declared != {expect} or expect is None:
            split_mismatch.append({"cad_id": cad, "jsonl": sorted(declared), "split_file": expect})
        cdir = DATA / "cad" / cad
        inp = np.load(cdir / "curve_c2/curve_inputs.npy")
        gt = {int(c["edge_id"]): c["curve_type"] for c in json.loads((cdir / "gt_brep_curves.json").read_text())["curves"]}
        corr = {(int(r["dora_curve_index"]), int(r["gt_curve_id"]) if r["gt_curve_id"] is not None else None): r["classification"] for r in json.loads((cdir / "correspondence.json").read_text())["records"]}
        src = ROOT / "cad_spatial_dataset/DeepCAD/train" / sid(cad)
        if not (src / "model.obj").is_file() or not (src / "program_canonical.dsl").is_file():
            missing_src.append(cad)
        for e in es:
            i = int(e["dora_curve_index"])
            gid = int(e["gt_edge_id"])
            if i < 0 or i >= len(inp):
                oob.append((cad, i, len(inp)))
            if corr.get((i, gid)) != "MATCHED_1_TO_1":
                not_matched.append((cad, i, gid, corr.get((i, gid))))
            gtyp = gt.get(gid)
            if gtyp != e["gt_curve_type"] and not (gtyp == "BEZIER" and e["gt_curve_type"] == "BSPLINE"):
                type_mismatch.append((cad, gid, e["gt_curve_type"], gtyp))
            if e["source_id"] != sid(cad):
                issues.append({"SOURCE_ID": [cad, e["source_id"]]})
    n_train_curve = sum(e["cad_split"] == "train" for e in entries)
    n_val_curve = sum(e["cad_split"] == "val" for e in entries)
    return {
        "n_jsonl": len(entries),
        "n_cad": len(by),
        "jsonl_split_counts": {"train_curve": n_train_curve, "val_curve": n_val_curve},
        "split_file_counts": split["counts"],
        "n_split_mismatch": len(split_mismatch),
        "n_index_oob": len(oob),
        "n_not_matched_1to1": len(not_matched),
        "n_gt_type_mismatch": len(type_mismatch),
        "n_missing_source_mesh_or_dsl": len(missing_src),
        "split_mismatch_head": split_mismatch[:10],
        "index_oob_head": oob[:10],
        "not_matched_head": not_matched[:10],
        "gt_type_mismatch_head": type_mismatch[:10],
        "missing_src_head": missing_src[:10],
        "PASS": not (
            split_mismatch or oob or not_matched or type_mismatch or missing_src or train & val
        ),
    }


def main() -> None:
    split = json.loads((DATA / "C2_DORA_CAD_SPLIT_V1.json").read_text())
    entries = [json.loads(x) for x in (DATA / "C2_DORA_TRAINSET_V1.jsonl").read_text().splitlines() if x]
    split_set = {c: "train" for c in split["train_cad_ids"]}
    split_set.update({c: "val" for c in split["val_cad_ids"]})
    cohort = load_cohort()
    by = defaultdict(list)
    for e in entries:
        by[e["cad_id"]].append(e)
    rng = random.Random(42)
    train_cads = [c for c in split["train_cad_ids"] if c in by]
    picked = rng.sample(train_cads, 10)
    OUT.mkdir(parents=True, exist_ok=True)
    dumps = [dump_cad(c, by[c], split_set, cohort) for c in picked]
    full = audit_all(entries, split, cohort)
    # one fully expanded trainer sample (first curve of first dumped CAD)
    example = dumps[0]["curves"][0]
    summary = {
        "dataset": str(DATA),
        "split_file": str(DATA / "C2_DORA_CAD_SPLIT_V1.json"),
        "jsonl": str(DATA / "C2_DORA_TRAINSET_V1.jsonl"),
        "what_a_sample_is": "one MATCHED_1_TO_1 Dora-fitted curve → B-Rep type+params",
        "not_spatiallm_sft": True,
        "split": split["counts"],
        "seed": 42,
        "n_dumped_cad": 10,
        "n_dump_pass": sum(d["PASS"] for d in dumps),
        "failed_ids": [d["cad_id"] for d in dumps if not d["PASS"]],
        "full_jsonl_audit": full,
        "dumped_cads": [
            {
                "cad_id": d["cad_id"],
                "split": d["cad_split"],
                "n_train_curves": d["n_train_curves"],
                "n_dora_fitted": d["n_dora_fitted"],
                "n_gt_brep": d["n_gt_brep"],
                "gt_types": d["type_counts"],
                "fit_types": d["fit_type_counts"],
                "PASS": d["PASS"],
                "issues": d["issues"],
            }
            for d in dumps
        ],
        "example_trainer_item": {
            "cad_id": dumps[0]["cad_id"],
            **example,
        },
    }
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    for d in dumps:
        (OUT / f"{d['cad_id']}.json").write_text(json.dumps(d, indent=2) + "\n")
        if d["SOURCE_CAD_FOR_ALIGNMENT"]["dsl_text"]:
            (OUT / f"{d['cad_id']}.source.dsl").write_text(d["SOURCE_CAD_FOR_ALIGNMENT"]["dsl_text"])
    print(json.dumps({k: summary[k] for k in summary if k != "example_trainer_item"}, indent=2))
    print("EXAMPLE", dumps[0]["cad_id"], "curve0 gt", example["gt_curve_type"], "fit", example["fit_type"], "idx", example["dora_curve_index"])


if __name__ == "__main__":
    main()
