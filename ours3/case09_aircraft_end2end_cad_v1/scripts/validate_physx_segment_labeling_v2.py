#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

import numpy as np


CASE = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1")
DEST = CASE / "01_part_discovery/physx_grounded_v2"
P3 = CASE / "01_part_discovery/p3"
FROZEN = CASE / "01_part_discovery/physx"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


labels = np.load(P3 / "triangle_part_id.npy", allow_pickle=False)
manifest = load(DEST / "artifacts/prepare_manifest.json")
result = load(DEST / "physx_segment_labels.json")
gate = load(DEST / "artifacts/gate.json")

tests = {}
tests["frozen_p3_has_10_segments"] = len(np.unique(labels)) == 10
tests["manifest_has_10_segments"] = len(manifest["segments"]) == 10
tests["result_has_10_labels"] = len(result["labels"]) == 10
tests["gate_pass"] = gate["GATE_PASS"] is True
tests["segment_specific_output_rate_1"] = gate["SEGMENT_SPECIFIC_OUTPUT_RATE"] == 1.0
tests["no_parts_table"] = gate["WHOLE_OBJECT_PARTS_TABLE_USED"] is False
tests["no_first_l0_binding"] = gate["FIRST_L0_BINDING_USED"] is False
tests["p3_count_unchanged"] = gate["P3_SEGMENT_COUNT_CHANGED"] is False
tests["no_multi_part_accepted"] = gate["MULTI_PART_OUTPUT_ACCEPTED"] is False
tests["no_physx_dimensions"] = gate["PHYSX_DIMENSIONS_USED"] is False
tests["eval_gt_not_used_in_inference"] = gate["geometry_gt_for_eval_only_used_in_inference"] is False
tests["frozen_physx_not_modified_during_run"] = gate["frozen_physx_modified"] is False

required = {
    "p3_segment_id",
    "generic_part_label",
    "geometry_role",
    "function_hint",
    "confidence",
    "status",
    "alternatives",
    "evidence_views",
    "global_context_used",
}
for segment in manifest["segments"]:
    sid = segment["p3_segment_id"]
    part_id = int(segment["p3_part_id"])
    expected = np.flatnonzero(labels == part_id)
    actual = np.load(segment["triangle_mask"], allow_pickle=False)
    tests[f"{sid}_exact_triangle_mask"] = np.array_equal(actual, expected)
    output = load(DEST / "labels" / f"{sid}.json")
    tests[f"{sid}_schema"] = required.issubset(output)
    tests[f"{sid}_bound_id"] = output["p3_segment_id"] == sid
    tests[f"{sid}_one_object"] = output["OUTPUT_CONTRACT_OK"] is True
    tests[f"{sid}_five_views"] = len(output["evidence_views"]) == 5 and all(Path(p).is_file() for p in output["evidence_views"])
    tests[f"{sid}_geometry_descriptor"] = Path(segment["geometry"]).is_file()
    tests[f"{sid}_global_context"] = output["global_context_used"] == "Aircraft"

frozen_files = {
    str(path.relative_to(FROZEN)): sha(path)
    for path in sorted(FROZEN.rglob("*"))
    if path.is_file()
}
summary = {
    "schema": "P3ConditionedPhysXSegmentLabelingV2IndependentValidation",
    "passed": all(tests.values()),
    "tests_passed": sum(tests.values()),
    "tests_total": len(tests),
    "tests": tests,
    "frozen_physx_file_count": len(frozen_files),
    "frozen_physx_snapshot_sha256": hashlib.sha256(
        json.dumps(frozen_files, sort_keys=True).encode("utf-8")
    ).hexdigest(),
    "family_accuracy_eval_only": gate["family_accuracy"],
    "exact_accuracy_eval_only": gate["exact_accuracy"],
    "blockers": [],
}
(DEST / "artifacts/validation_summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(summary, indent=2))
raise SystemExit(0 if summary["passed"] else 1)
