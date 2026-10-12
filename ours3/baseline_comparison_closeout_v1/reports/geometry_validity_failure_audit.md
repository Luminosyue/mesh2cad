# Geometry Validity Failure Audit

Definition: STEP reload success is tracked separately from geometry validity. This audit counts only `STEP_RELOAD_PASS_BUT_GEOMETRY_INVALID`.

| Method | STEP reload pass but geometry invalid | empty solid | non-solid | invalid BRep | boolean failure | zero volume | sampling failure | normalization failure | other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| P1 | 719 | 0 | 0 | 719 | 0 | 0 | 0 | 0 | 0 |
| CAD-Recode | 639 | 0 | 0 | 633 | 0 | 0 | 0 | 0 | 6 |
| CADFit | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Case-level evidence is retained in the per-case CSVs; unavailable full CADFit cases remain pending until the detached official inference finishes.
