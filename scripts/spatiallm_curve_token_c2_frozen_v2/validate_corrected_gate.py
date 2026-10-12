#!/usr/bin/env python3
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
BASE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire"
RUN1 = BASE / "v2_100_corrected/runs/run1/MANIFEST.json"
RUN2 = BASE / "v2_100_corrected/runs/run2/MANIFEST.json"
PROVENANCE = BASE / "provenance20_v2/PROVENANCE.json"
V1_MAP = ROOT / "cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/V1_FROZEN_SHA256.json"
EVIDENCE_MAP = ROOT / "cad_spatial_dataset/geometry_pack_v2_mesh2cad/placement_fix_retest_v3/DELIVERY_SHA256.json"
REPORT_DIR = BASE / "v2_100_corrected/reports"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_map(path):
    expected = json.loads(path.read_text())
    ok = 0
    missing = []
    mismatch = []
    for name, digest in expected.items():
        target = Path(name)
        if not target.exists():
            missing.append(name)
        elif sha256(target) == digest:
            ok += 1
        else:
            mismatch.append(name)
    return {"expected": len(expected), "unchanged": ok, "missing": missing, "mismatch": mismatch}


def stats(values):
    a = np.asarray(values, dtype=np.float64)
    return {
        "min": float(np.min(a)),
        "mean": float(np.mean(a)),
        "median": float(np.median(a)),
        "p10": float(np.percentile(a, 10)),
        "p90": float(np.percentile(a, 90)),
        "max": float(np.max(a)),
    }


d1 = json.loads(RUN1.read_text())
d2 = json.loads(RUN2.read_text())
p = json.loads(PROVENANCE.read_text())
r1, r2 = d1["rows"], d2["rows"]

budget = sum(bool(r["budget_equality"]) and r["k_valid"] == r["B1"]["second_stream_active"] == r["M2"]["second_stream_active"] for r in r1)
attention = sum(bool(r["attention_equality"]) and r["B1"]["second_stream_active"] == r["M2"]["second_stream_active"] for r in r1)
total_attention = sum(r["B1"]["total_active_attention"] == r["M2"]["total_active_attention"] for r in r1)
physical = sum(bool(r["physical_length_equality"]) and r["B1"]["physical_padded_length"] == r["M2"]["physical_padded_length"] for r in r1)
fake_valid = sum(r["B1"]["fake_valid_padding"] + r["M2"]["fake_valid_padding"] for r in r1)
padding_attention = sum(r["B1"]["padding_attention"] + r["M2"]["padding_attention"] for r in r1)

by_id2 = {r["cad_id"]: r for r in r2}
selection_identical = sum(
    r["cad_id"] in by_id2
    and r["selected_b1_indices"] == by_id2[r["cad_id"]]["selected_b1_indices"]
    and r["selected_m2_indices"] == by_id2[r["cad_id"]]["selected_m2_indices"]
    and r["k_valid"] == by_id2[r["cad_id"]]["k_valid"]
    for r in r1
)

v1 = verify_map(V1_MAP)
evidence = verify_map(EVIDENCE_MAP)
k = [r["k_valid"] for r in r1]
b1_ret = [r["b1_retention_ratio"] for r in r1]
m2_ret = [r["m2_retention_ratio"] for r in r1]

manifest_sha1 = sha256(RUN1)
manifest_sha2 = sha256(RUN2)
passed = all([
    p.get("PASS") is True,
    p.get("DIRECT_C2_VS_EXPORTED_TOKEN") == "20/20",
    p.get("MAX_ABS_TOKEN_DIFF") == 0.0,
    len(r1) == len(r2) == 100,
    budget == attention == total_attention == physical == selection_identical == 100,
    fake_valid == padding_attention == 0,
    manifest_sha1 == manifest_sha2,
    v1["unchanged"] == v1["expected"] == 19580,
    evidence["unchanged"] == evidence["expected"] == 3669,
])

result = {
    "CURRENT_GATE": "B1_POST_ENCODER_BUDGET_C2_CORRECTED_V2_100_PASS" if passed else "B1_POST_ENCODER_BUDGET_C2_CORRECTED_V2_100_HARD_STOP",
    "PROTOCOL_STATUS": "IMPLEMENTED_AND_VERIFIED" if passed else "FAILED",
    "CURVE_ENCODER_CHECKPOINT": p["CURVE_ENCODER_CHECKPOINT"],
    "CURVE_ENCODER_CHECKPOINT_SHA256": p["CURVE_ENCODER_CHECKPOINT_SHA256"],
    "CURVE_ENCODER_FROZEN": p["CURVE_ENCODER_FROZEN"],
    "CURVE_ENCODER_PROVENANCE": "PASS" if p["PASS"] else "FAIL",
    "DIRECT_C2_VS_EXPORTED_TOKEN": p["DIRECT_C2_VS_EXPORTED_TOKEN"],
    "MAX_ABS_TOKEN_DIFF": p["MAX_ABS_TOKEN_DIFF"],
    "BUDGET_EQUALITY": f"{budget}/100",
    "ATTENTION_EQUALITY": f"{attention}/100",
    "TOTAL_ATTENTION_EQUALITY": f"{total_attention}/100",
    "PHYSICAL_PADDED_LENGTH_EQUALITY": f"{physical}/100",
    "FAKE_VALID_COUNT": fake_valid,
    "PADDING_ATTENTION_COUNT": padding_attention,
    "DETERMINISM": f"{selection_identical}/100",
    "MANIFEST_HASH_IDENTICAL": manifest_sha1 == manifest_sha2,
    "MANIFEST_CONTENT_SHA256": d1["content_sha256"],
    "MANIFEST_FILE_SHA256": manifest_sha1,
    "K_VALID_DISTRIBUTION": stats(k),
    "B1_RETENTION_RATIO": stats(b1_ret),
    "M2_RETENTION_RATIO": stats(m2_ret),
    "V1_FROZEN_HASHES": f'{v1["unchanged"]}/{v1["expected"]}',
    "OLD_EVIDENCE_HASHES": f'{evidence["unchanged"]}/{evidence["expected"]}',
    "V1_HASH_FAILURES": len(v1["missing"]) + len(v1["mismatch"]),
    "OLD_EVIDENCE_HASH_FAILURES": len(evidence["missing"]) + len(evidence["mismatch"]),
    "FULL_C2_TOKEN_EXPORT_COUNT": 2796,
    "SPATIALLM_TRAINING_STARTED": False,
    "V2_1K_STARTED": False,
    "ALLOW_V2_1K_BUILD": passed,
}

REPORT_DIR.mkdir(parents=True, exist_ok=True)
(REPORT_DIR / "FINAL_GATE.json").write_text(json.dumps(result, indent=2) + "\n")
lines = ["# Corrected C2 V2-100 Gate", ""] + [f"{key}={value}" for key, value in result.items() if not isinstance(value, dict)]
lines += ["", "## K_valid distribution", "", json.dumps(result["K_VALID_DISTRIBUTION"], indent=2), "", "## Retention", "", json.dumps({"B1": result["B1_RETENTION_RATIO"], "M2": result["M2_RETENTION_RATIO"]}, indent=2)]
(REPORT_DIR / "FINAL_GATE.md").write_text("\n".join(lines) + "\n")
print(json.dumps(result, indent=2))
if not passed:
    raise SystemExit(2)
