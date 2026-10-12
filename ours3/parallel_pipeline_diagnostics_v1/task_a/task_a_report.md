# CAD Structure Audit V1

Read-only OCP audit of explicitly named STEP files. No STEP, CASE09 source, or shared code was modified.

## Latest artifact results

| Case | Structural class | Faces | BSpline ratio | Surface groups | Strip edges | Strip ratio |
|---|---|---:|---:|---:|---:|---:|
| CASE_02 | FRAGMENTED_SPLINE_BREP | 3522 | 0.999432 | 160 | 8242 | 0.580096 |
| CASE_03 | ANALYTIC_FEATURE_BREP | 6 | 0.000000 | 6 | 0 | 0.000000 |
| CASE_04 | FRAGMENTED_SPLINE_BREP | 322 | 0.993789 | 89 | 448 | 0.318182 |
| CASE_05 | FRAGMENTED_SPLINE_BREP | 5780 | 0.996540 | 1114 | 3288 | 0.135197 |
| CASE_08 | FRAGMENTED_SPLINE_BREP | 3522 | 0.999432 | 1196 | 156 | 0.010980 |
| CASE_09 | UNKNOWN | 92 | 0.347826 | 86 | 12 | 0.027778 |

## Method notes

- Every available input was loaded into a new STEPControl_Reader and freshly tessellated.
- Surface groups require shared TopoDS_Edge adjacency and either the same analytic hypothesis or a conservative representative-normal G1 proxy.
- Strip detection operates on real TopoDS_Edge samples, direction families, local spatial regions, and near-equal spacing tests.
- Compact classification requires surface abstraction evidence; low face count alone is never sufficient.
- Missing explicit version paths are recorded as NOT_AVAILABLE; no path guessing was used.

- Contact sheet: `/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1/task_a/artifacts/cad_structure_contact_sheet.png`

## CASE09 in-flight disclosure

CASE09's live final changed across two separate read-only audit runs: 137 faces in run 1 and 92 faces in run 2. The headline metrics are the run-2 point-in-time result. Its size, mtime, and SHA256 were identical before and after fresh reload/rendering, and still matched during finalization. This is not a claim that the live producer stayed unchanged for the whole task. The stable explicit baseline/V1/V2 results remain separately preserved in the version matrix.

## Tests

- Embedded artifact checks: 12 passed, 0 failed.
- Independent pytest suite: 8 passed, 0 failed.
