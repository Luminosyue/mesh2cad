# A0/A1/A2/A3/P1 Geometric Effectiveness Benchmark

CURRENT_GATE = `A0_A1_A2_A3_P1_GEOMETRIC_EFFECTIVENESS_BENCH_V1_COMPLETE`
TEST_TOUCHED = `NO`
GED_STATUS = `DEFERRED_UNDEFINED`
P1_STATUS = `CURRENT_MAIN_METHOD`

## Headline

| Method | IoU valid-only | IoU success-weighted | IoU N | Our standardized CD | CD N | H95 | Volume error | STEP Reload | Valid BRep | Closed Solid |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A0 | 0.451629 | 0.099810 | 221 | 0.220650 | 223 | 0.167508 | 0.533308 | 0.867000 | 0.862000 | 0.861000 |
| A1 | 0.479763 | 0.107947 | 225 | 0.214882 | 234 | 0.196319 | 0.491006 | 0.918000 | 0.901000 | 0.901000 |
| A2 | 0.482632 | 0.098457 | 204 | 0.088402 | 210 | 0.151640 | 0.610074 | 0.862000 | 0.850000 | 0.847000 |
| A3 | 0.522252 | 0.107584 | 206 | 0.082640 | 211 | 0.159399 | 0.992954 | 0.887000 | 0.869000 | 0.864000 |
| P1 | 0.528964 | 0.124306 | 235 | 0.197984 | 239 | 0.142823 | 0.315719 | 0.956000 | 0.938000 | 0.938000 |

## Conclusions

- Program: P1 improves program-level exactness and operation F1 over A3.
- Geometry: P1 volumetric/structural geometry status is YES; standardized surface CD status is PARTIAL.
- Complexity: On GT high-operation cases, P1 complexity advantage is YES.
- Cross-paper comparison: `NO` because CD and B-Rep IoU are frozen project-standardized metrics, not officially verified paper evaluator replicas.

## Deferred

- GED is `DEFERRED_UNDEFINED`; the existing dependency graph F1 is not relabeled as GED.
- Normal consistency and manifold rate are not reported because a reliable shared implementation was not frozen.
