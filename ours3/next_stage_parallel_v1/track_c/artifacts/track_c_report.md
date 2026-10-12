# Track C — MAC Gate 2 Geometry Baseline

Status: **PASS**

## Scope and provenance

Four original Gate1 whole-object A/B cases were selected automatically. Gate1 analysis was not rerun. PhysX, P3, STEP GT, ABC GT, ICP, and assembly were not used.

Canonical bbox diagonal: 100.0 mm. Metric sample count: 50000 per surface, seed: 20260810.

## Results

| Case | Gate1 class | STEP | Reload | BREP | Metrics | Quality | Chamfer | P95 | Coverage .02 |
|---|---|---:|---:|---:|---:|---|---:|---:|---:|
| REAL_05 | A_PROGRAM_CAD_FRIENDLY | True | True | True | True | Q3_REJECT | 0.069316158635392 | 0.1595528871121882 | 0.34876 |
| REAL_02 | B_PROGRAM_CAD_POSSIBLE | True | True | True | True | Q3_REJECT | 0.065844578845052 | 0.1538851005688834 | 0.28432 |
| REAL_06 | B_PROGRAM_CAD_POSSIBLE | True | True | True | True | Q3_REJECT | 0.20665929465931124 | 0.44031838479367447 | 0.0853 |
| REAL_08 | B_PROGRAM_CAD_POSSIBLE | True | True | True | True | Q3_REJECT | 0.19425582712361172 | 0.4852425575581775 | 0.06312 |

## Fixed quality thresholds

Q1: valid BREP, Chamfer <= 0.01, P95 <= 0.02, Coverage_02 >= 0.95. Q2: valid BREP, Chamfer <= 0.02, P95 <= 0.05, Coverage_02 >= 0.85. Otherwise Q3.

## Machine-readable summary

`/data/home/cuiyuehan/project/mesh2cad/ours3/next_stage_parallel_v1/track_c/artifacts/track_c_summary.json`
