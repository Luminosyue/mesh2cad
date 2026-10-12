# P3 high-detail Mesh2CAD factory V1 Smoke20

2026-10-06T13:26:54.110988+00:00

```json
{
  "CURRENT_GATE": "P3_HIGH_DETAIL_SMOKE20_ENGINEERING_PASS_QUALITY_FAIL",
  "READ_ONLY_GUARD": "PASS",
  "OBJECT_INPUT_N": 20,
  "P3_SUCCESS_N": 20,
  "TOTAL_PART_N": 209,
  "MAJOR_PART_N": 153,
  "MICRO_PART_N": 0,
  "CAD_ATTEMPTED_N": 209,
  "STEP_EXPORT_PASS_N": 209,
  "STEP_RELOAD_PASS_N": 209,
  "PART_STRICT_ACCEPT_N": 4,
  "PART_NEAR_PASS_N": 63,
  "PART_REJECT_N": 142,
  "PART_STRICT_ACCEPT_RATE": 0.019138755980861243,
  "P3_ROLE": "PART_DECOMPOSITION",
  "XPART_NEEDED_N": 0,
  "XPART_ATTEMPTED_N": 0,
  "XPART_SUCCESS_N": 0,
  "XPART_STRICT_ACCEPT_N": 0,
  "FULL_STRICT_ASSEMBLY_N": 0,
  "PARTIAL_ASSEMBLY_N": 3,
  "ASSEMBLY_FAIL_N": 17,
  "FULL_OBJECT_ASSEMBLY_RATE": 0.0,
  "OBJECT_NCD_MEDIAN": 0.0873810212082718,
  "OBJECT_IOU_MEDIAN": 0.016347604519395178,
  "OBJECT_METRICS_DENOMINATOR_N": 3,
  "PSEUDO_PART_PAIR_N": 4,
  "EXACT_PART_PAIR_N": 4,
  "PSEUDO_OBJECT_PAIR_N": 0,
  "EXACT_OBJECT_PAIR_N": 3,
  "PAIR_TYPE_SEPARATION": "PASS",
  "MEDIAN_PART_PRIMITIVE_N": 1.0,
  "MEDIAN_BOOLEAN_OP_N": 0.0,
  "EXTRUSION_N": 3,
  "REVOLVE_N": 0,
  "BOOLEAN_N": 0,
  "MULTI_PRIMITIVE_N": 0,
  "FRAME_BEAM_N": 3,
  "UNSUPPORTED_N": 15,
  "IS_HIGH_DETAIL_CAD_DATA": "NO",
  "IS_MORE_COMPLEX_THAN_SIMPLE_DEEPCAD_STYLE": "NO",
  "CAN_SCALE_TO_100": "NO",
  "PRIMARY_BLOCKER": "Compact part CAD fitting does not recover source geometry sufficiently; no demonstrated high-detail full-object reconstruction.",
  "NEXT_ALLOWED_STAGE": "IMPROVE_PART_CAD_RECONSTRUCTION",
  "COMPLEXITY_GATE": "PASS",
  "CANDIDATE_ATTEMPT_N": 1211,
  "CAD_PARSE_PASS_N": 209,
  "CAD_EXECUTE_PASS_N": 209,
  "ENGINEERING_GATE": "PASS",
  "QUALITY_GATE": "FAIL"
}
```

1. P3 successful objects: 20/20.

2. Total parts: 209.

3. Major parts: 153.

4. At least one native executable candidate: 209/209. This is not geometry acceptance.

5. Strict accepted parts: 4/209 (1.91%); near-pass: 63; rejected: 142.

6. Accepted planned families: B_EXTRUSION: 1/55, G_FRAME_OR_BEAM_STRUCTURE: 3/31. Other planned families had zero strict accepts. See tables/family_breakdown.csv; small counts do not establish universal ranking.

7. Curved housings, changing cross sections, openings and disconnected surface fragments exceed the compact fitting hypotheses. Selected-candidate failed strict checks (overlapping counts): {"IoU": 193, "NCD": 151, "centroid": 142, "bbox": 83}. Per-candidate errors and metrics are retained.

8. No paired whole-object baseline was run, so a significant causal benefit from P3 has not been demonstrated. P3 produced independently addressable geometry with recoverable transforms.

9. X-Part used: 0. No independently confirmed severe truncation plus direct failure was established; open segmentation boundaries alone are insufficient.

10. X-Part benefit: not evaluated; no treated/control examples.

11. Full major-part strict assemblies: 0; exported strict subsets: 3. Partial can contain only a small fraction of the source, explicitly recorded.

12. Full-only IoU/NCD medians: None / None. Overall nonempty assembly medians use n=3 and must not be mistaken for full-object quality.

13. Pseudo pairs: parts=4, objects=0. These are reconstructed pseudo supervision, never original design GT.

14. CAD-derived exact pairs: parts=4, objects=3. Partial-object exact pairs retain their partial status.

15. No demonstrated richer accepted CAD distribution than a simple DeepCAD-style dataset. High source triangle count and dense CAD tessellation are not proof of parametric design complexity.

16. Do not scale to 100. Improve part structure and parameter fitting under the same strict gate first.

## Method and limits

All original sources and historical results remained read-only within the recorded integrity scope. The new pipeline uses full source objects and real P3 inference. Source hashes, normalization, inverse transforms, face assignments, features, plans, candidates, reload geometry and failures are retained. Geometry uses 20,000 sampled points and the inherited IoU128 approximate scan-fill protocol; this is not exact solid Boolean IoU. All thresholds are frozen.

LLM planning was performed by the interactive Codex assistant after inspecting per-part geometry summaries, with explicit response maps and prompt hashes. It is a replayable frozen-plan run, not a separately callable unattended LLM service. Numeric dimensions come from deterministic geometry fitting. Plans are hypotheses, not recovered design intent. Eight family labels are available, but the initial emitters only cover bounded extrusion/cuts, loft, radial revolve, primitives and limited component unions; true connected frame graph reconstruction is not implemented. This limitation is material.

Strict CAD parts alone enter training-pair manifests and source assemblies. Near and rejected CAD artifacts remain diagnostic only. Assembly compounds preserve independent solids. Source-frame and canonical-frame outputs are distinguished. No mesh wrappers, embedded source facets, per-triangle solids, invented sheet thicknesses or whole-object bounding-box success claims are used.

Exact-pair tessellation uses tighter OCC tolerances; if planar CAD retained the same triangle count, one subdivision is recorded explicitly. More triangles do not imply more design detail. Optional scan-like corruption was omitted.

The synthetic two-solid assembly fixture is an engineering check only, excluded from all object/part/pair counts. Stage records describe whether source-data assembly actually closed; fixture success must not be described as a successful real-object reconstruction.

## Deliverables

See tables/object_summary.csv, tables/part_summary.csv, tables/candidate_summary.csv, tables/strict_accepted_parts.json, tables/full_assemblies.json, manifests/pseudo_pairs.json, manifests/exact_pairs.json, visualizations/index.html, scripts/run_pipeline.py and reports/REPRODUCE.md.


## Audit semantics

GOOD in the initial mesh audit means finite, nondegenerate geometry with no independently established severe missing-surface evidence. It is not a watertightness or complete-part certificate. Watertight parts: 3/209. Disconnected parts: 29. Open P3 boundaries were never sufficient to trigger X-Part. Family confidence scores are uncalibrated planning confidence, not estimated acceptance probability.

Failed strict checks on selected candidates (overlapping counts): {"IoU": 193, "NCD": 151, "centroid": 142, "bbox": 83}. Missing metrics are excluded from these counts. See candidate_summary for execution failures and part result.json for generation failures. The family_breakdown table uses planned families; realized_candidate_family uses actual selected construction types. CAD complexity summary medians and operation counts use strict accepted parts only; UNSUPPORTED_N counts attempted H-family plans.

The per-part prompt.txt is a reconstructed planning-context record from the geometry summary inspected in this conversation, not a separately submitted API prompt. Actual interactive model input also included the conversation and batched tool output. Response maps record the explicit decisions used; no independent unattended LLM inference log is claimed.
