# MESH2CAD DATA FACTORY V1 — Smoke100

CURRENT_GATE = SMOKE100_PASS
READ_ONLY_GUARD = PASS

These are geometry-consistent reconstructed CAD targets / pseudo-CAD supervision, not original design ground truth.

## Answers to the 11 required questions

1. Located 100 frozen source candidates; 100 source-valid, provenance-closed meshes processed. Closure is anchored to extant original part STL bytes, historical source SHA metadata, parent whole-object STL bytes, and exact float32 triangle subset membership. Original GLB/labels/download chain remain unavailable; no broader upstream closure is claimed.
2. Direct reconstruction attempted: 100.
3. Direct case-level successes (any candidate): parse 97; execution 97; STEP export 97; STEP reload 97; strict geometry pass 5.
4. Final strict accepted direct pair count: 5. Relaxed analysis only: 92; rejected: 3.
5. Final case failures: {'GEOMETRY_MISMATCH': 92, 'UNSUPPORTED_GEOMETRY': 3}. Individual candidate errors remain in each case manifest and attempts directory. A failed hypothesis does not invalidate a later successful candidate.
6. Independently confirmed P3/X-Part-needed cases: 0. This is an evidence-qualified count, not proof no mesh would benefit. Open part boundaries or template mismatch alone do not justify completion.
7. Completion attempted 0; fallback CAD reconstructed 0; fallback strict accepted 0.
8. Completion benefit is UNKNOWN / not tested. The observed fit failures concern the bounded CAD hypotheses; no causal evidence attributes them to missing source surfaces.
9. Native executable CadQuery cases: 97. DSL targets = 0; mesh-wrapper targets = 0. Rejected/no-plan cases have no accepted target. AST allowlist rejects mesh import/payloads; genuine 2D polygon sketches are capped at 96 entities, 4 profiles, 8 holes.
10. Can scale to 1000: YES. No Scale1000 execution was performed.
11. Primary blocker: None. Next allowed stage: SCALE_1000.

## Source selection and limitations

The metadata-eligible pool contained 2105 original part meshes. Selection prioritizes historical watertight status, low face count, then a deterministic object/part hash; exact-byte duplicates are removed. No historical CAD metric was used. The frozen 100 are strongly biased toward simple geometry, not a representative benchmark or category-balanced dataset. Source audit reports connected components, boundary/nonmanifold edges, finite vertices, valid faces, area and meaningful volume. Nonwatertight meshes are not automatically rejected or completed.

Every case carries dataset, object/part IDs, source/evidence/parent hashes and `split_group_id`. Future splits must group all parts of one parent object. Source hashes deduplicate identical STL bytes, not semantic duplicates across different objects.

## Coordinate and metric contract

Canonical vertices = (original vertices − original bbox midpoint) / original longest bbox edge. Source orientation is preserved. Forward and inverse 4x4 matrices, original/canonical bboxes and area-weighted centroids are retained. Local modeling axes do not rotate the evaluation frame. CAD is never independently aligned.

Each candidate is executed in a fresh subprocess, exported, reloaded with CadQuery/OCC, validated for nonempty valid solid B-Rep, then tessellated at tolerance 0.001 and angular tolerance 0.05. Only serialized tessellation of the reloaded STEP is evaluated. STEP, CAD mesh and normalized source hashes bind metrics to artifacts.

Chamfer uses 20000 area-uniform surface points per mesh, deterministic seeds, symmetric mean of unsquared nearest sampled-point distances. NCD divides this mean by the source bbox diagonal. P95 pools both directional distances. This sampled-point metric has sampling noise even on identical surfaces. Centroid is the exact triangle-area-weighted surface centroid; errors are canonical length units. Bbox error is max(center L2, extent L-infinity).

IoU protocol: APPROXIMATE_VOXEL_SCAN_FILL_IOU_V1, nominal resolution 128. One shared union-bbox grid, longest union extent /124 pitch, padded boundary cells; subdivision surface rasterization, majority XYZ scan fill and binary hole fill. This is approximate scan-filled occupancy, NOT exact solid volumetric IoU. Open sheets can receive occupancy without defining a physical enclosed volume. It is unsuitable to interpret these scores as original design validity.

Strict: approximate IoU >=0.90, NCD <=0.01, bbox error <=0.03, centroid error <=0.02 plus source/native/execution/export/reload/evaluation gates. Relaxed: all execution and evaluation gates valid but strict metrics fail. Reject: invalid source, program, execution, export/reload or evaluator. Thresholds are smoke references, not final training thresholds.

Four or fewer deterministic hypotheses per source: up to two projected silhouette extrusions, an oriented box and a cylinder. Selection ranks strict pass, then IoU, then NCD. This is finite template selection, no iterative loss optimization, LLM calls, model updates or training. Acceptance is measured on the same source used for fitting and candidate selection, not held-out reconstruction generalization.

## Reproducibility, guard and caches

Stage validation: [{'pass': True, 'n': 3, 'evaluated_n': 3, 'system_errors': [], 'strict_n': 2, 'timestamp': '2026-10-06T09:38:11.499726+00:00'}, {'pass': True, 'n': 10, 'evaluated_n': 9, 'system_errors': [], 'strict_n': 4, 'timestamp': '2026-10-06T09:43:03.423082+00:00'}, {'pass': True, 'n': 100, 'evaluated_n': 97, 'system_errors': [], 'strict_n': 5, 'timestamp': '2026-10-06T09:55:25.910294+00:00'}]. Core generator/config/evaluator SHA unchanged across stages: True. Safety/metric self-tests: True. Artifact consistency errors: [].

Read-only guard verifies 272 protected file hashes and 74530 preexisting historical file metadata entries. Access times are excluded. Scope is selected source/parent/evidence, copied donor, frozen historical audit and relevant source/output trees; this is not a server-wide filesystem proof. All writes from factory code are under the fresh factory root, and historical logic is copied rather than imported. Existing case/stage/report directories are never overwritten; reruns require a new root or a new report tag. No historical rename, deletion, training or bulk generation occurred.

Surface/curve caches: NOT_BUILT. No compatible extractor was validated for this new contract; status and reason recorded per case. This optional omission does not gate Smoke100. Software versions, seeds, source hash inventory, code hashes and code reuse provenance are supplied.

## Deliverables and entrypoint

Factory root: `/data/home/cuiyuehan/project/mesh2cad/outputs/mesh2cad_data_factory_v1_smoke100`

Entrypoint: `scripts/factory.py --limit 3`, then `--limit 10`, then `--limit 100` with the recorded cadfit-env Python. Each later stage requires the previous stage's validation pass and reruns the historical integrity guard. This frozen run is capped at 100; future scale requires a new root/config and source selection, never reusing this run as mutable storage.

Audit/report: `scripts/validate_and_report.py <new_snapshot_tag>`.

Tables: `tables/smoke100_case_table.csv`, `accepted_cases.csv`, `relaxed_cases.csv`, `rejected_cases.csv`, `failure_breakdown.csv`, `metric_distributions.csv`, `overall.csv`, `direct_vs_fallback.csv`.

Manifests: `manifests/cases.jsonl`, `source_inventory.csv`, `selection_frozen.json`. Each `cases/case_*/manifest.json` contains all candidate metadata, failures, paths, normalization, metrics, decisions and cache status. Full candidate programs, STEP files, reload metadata, tessellated meshes and logs remain inspectable.
