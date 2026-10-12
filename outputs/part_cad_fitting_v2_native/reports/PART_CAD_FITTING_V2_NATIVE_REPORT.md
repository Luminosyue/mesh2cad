# PART_CAD_FITTING_V2_NATIVE

Same 20 objects / 209 parts / 153 major parts. This output name follows the task; it is a new experiment after historical V2/V3, not an overwrite of them. Original V1 (4/63/142) is the requested paired comparison. Preserved strongest V1/V3 baseline retains prior gains; this round's extra gains are separately labeled.

Final: 17 Strict / 76 Near / 116 Reject. Major Strict: 15/153 (9.80%). Additional Strict this round: 2. Parts actually refit: 205. Strict damage: 0.

Representation/self-contained/STEP validation pass: 209/209. Every newly accepted candidate is checked by the copied independent validator, extended only to count compact arc and spline entities; no geometry thresholds changed. Existing baseline validations are reused only after exact source-code/STEP hash matching. New representation failures cannot reach geometric ranking. Candidate failures and roundtrip discrepancies are retained in logs.

Metrics: NCD median 0.017964 -> 0.013350; IoU 0.602951 -> 0.700698; centroid 0.029690 -> 0.008268. Weighted score improved/unchanged/worse: 200/9/0. Ranking prioritizes class then loss, so class promotion can worsen the combined score; individual deltas remain visible.

No P3 rerun, source change, case-specific hardcode, model training, threshold relaxation or assembly optimization. There is no claim that smooth-looking CAD implies source fidelity. Successful geometric training candidates still require the original strict thresholds plus valid representation.

Required tables, source evidence, selected native code/STEP/metrics, candidate logs and profile fitting parameters accompany this report. Render V4 is in ../cad_render_v4/ and deliberately renders unchanged historical V3 STEP, not these newly fitted shapes, to isolate display changes.

Implementation limits: reliable general fillet/chamfer and blind-hole inference is not implemented; no features are invented in their absence. Family search on Reject uses measured revolve/loft hypotheses and preserved baselines under <=8 candidates, <=8 primitive features and <=6 booleans. No unrestricted high-detail freeform solver is claimed. Zero FREEFORM_UNSUPPORTED classifications means no case was conclusively reclassified into that semantic category, not that all freeform geometry is solved.

## Persisted-mesh verification

All new candidate metrics were recomputed from the serialized evaluation PLY, matching the historical replay protocol. Initial in-memory metrics and original records are retained. No candidate code/STEP geometry changed. {"pass": true, "case_n": 209, "new_candidates_recomputed": 346, "max_abs_metric_drift": {"iou": 7.841353731330436e-06, "normalized_chamfer": 2.2668691635752136e-06, "bbox_error": 3.5004176890396366e-08, "centroid_l2_error": 2.326912774377728e-08}, "candidate_class_changes": 0, "case_selection_changes": 0, "case_status_changes": 0, "candidate_geometry_changed": false}
