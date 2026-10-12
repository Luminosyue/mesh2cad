# NATIVE PARAMETRIC CAD AUDIT V1

V1 is the primary 209-part cohort requested by the 4 Strict / 63 Near / 142 Reject stratification. V3 is a separate supplementary audit of the 209 parts shown in the latest assembly images. These are 209 corresponding part identities at two versions, not 418 unique dataset parts. No fitting, P3 rerun, new dataset examples or SCALE100 was performed. Synthetic validator controls are tests only.

## Result

| Field | Original V1 | Current V3 |
|---|---:|---:|
| Native parametric A | 209 | 209 |
| Native nonparametric B | 0 | 0 |
| Faceted B-Rep C | 0 | 0 |
| Mesh wrapper D | 0 | 0 |
| Uncertain E | 0 | 0 |
| Isolated reconstruction passed | 209 | 209 |
| Median source triangles | 17563.0 | 17563.0 |
| Median STEP faces | 51.0 | 51.0 |
| Median source triangles / STEP faces | 673.157895 | 564.500000 |
| Median analytic ratio | 1.0 | 1.0 |
| Median planar triangle ratio | 0.0 | 0.0 |

READ_ONLY_GUARD = PASS; REPRESENTATION_GATE = PASS. File guard checks SHA256, size, mtime, additions and removals across all four historical output trees (V1, V2, V3, assembly visualizations). It does not cover unrelated training directories. See integrity/READ_ONLY_GUARD.json.

All V1 statuses remain 4/63/142, with native representation in each group. V3 geometry statuses remain 15/77/117. **Representation eligibility is not paired-training acceptance**: only a separate geometry gate can accept fidelity. Existing geometry gate remains FAIL; no automatic scale-up or training admission.

V1 STEP faces range [3, 97]; V3 [3, 94]. V1 has 149 polyline programs; V3 158. These fitted numeric profiles are compact parametric feature definitions but may remain polygonal. Surface distributions and every face's area/edge/bbox evidence are in tables/ and cases/.

## Assemblies and visuals
Three historical partial STEP assemblies reloaded and their surface counts matched the audited native member parts (2, 1, 1 parts). Current 20 GLB/PLY previews trace to 209 audited native parts, including Near/Reject; no complete geometric assembly acceptance is implied. See assembly_audit.csv and v3_preview_assembly_audit.csv.

The visual gallery contains 10 representative current parts selected by surface diversity and the most complex topology, plus one clearly labeled synthetic faceted control. No real faceted cases were found, so none were invented to meet a 5+5 illustration suggestion. For each: STEP smooth shading, actual B-Rep edges, surface types. Main evidence is AST + OCC topology + source comparison, not screenshots.

## Prior validator and root cause
Old executor already had strict AST/import/operation restrictions and complexity limits, but lacked per-face OCC surface classification, triangular-face audit, independent reexecution-to-STEP correspondence and source-to-BRep compression reporting. No evidence of previous mesh-wrapper admission in these cohorts.

Polygonal fitted sketches produce genuine planar strips/conical segments; the STEP tessellation is then rendered with per-triangle normals by the preview renderer. Neither is source triangle wrapping. See ROOT_CAUSE_REPORT.md and evidence/source_evidence.json for scripts/functions/lines. Normal CAD display tessellation must be distinguished from triangle B-Rep topology. Native polygonal extrusion is a third category of visual angularity and remains a fitting-quality concern.

## Validation and scope
22 validator tests passed. All 209 programs in each version were reexecuted from cad.py alone with file access unavailable in the supported restricted grammar. No original STEP was rewritten. In-memory reconstruction was compared to original reloaded STEP using topology/surface counts, bounds, volume and area. This is not an arbitrary-code security sandbox or formal shape-equivalence proof. Unsupported future syntax fails closed to review.

## Decision
Representation validity passes; fitting quality remains relevant. The requested CAN_CONTINUE_PART_CAD_FITTING_V2 is YES at the representation gate, but V2 already exists and was not rerun. NEXT_ALLOWED_STAGE = GEOMETRY_FITTING_REVIEW_WITH_NATIVE_REPRESENTATION_VALIDATOR. No native generator rebuild is indicated. This audit installs no automatic pipeline hook because historical code is read-only; future work must invoke the delivered validator explicitly.

## Deliverables
scripts/validate_native_parametric_cad.py; tables/representation_audit_209.csv (V1) and representation_audit_209_v3.csv; surface/status/suspicious/accepted tables; per-face CSVs; per-case JSON and isolated cad.py execution logs; assembly topology JSON; source evidence snapshots; tests; gallery; integrity guard and structured SUMMARY.json.

Neither cohort has a dense triangular B-Rep pattern. Each contains 2 actual triangular planar faces in total (see actual_triangular_face_cases tables); the median ratio 0 does not mean every face is nontriangular. These small counts are consistent with native feature intersections/caps and do not satisfy triangle-wrapper evidence.
