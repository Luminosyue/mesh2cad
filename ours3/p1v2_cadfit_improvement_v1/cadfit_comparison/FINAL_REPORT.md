# P1v2 vs CADFit - DeepCAD-style IoU/CD/IR VAL1000

FULL_N=1000
FROZEN_GT_VALID_N=253
PAIR_COMMON_VALID_N=192
TRIPLE_COMMON_VALID_N=188

## Formal P1v2 vs CADFit

| Dataset | Method | N | IR | IoU mean | IoU median | CD mean | CD median | Common N |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| all | P1v2 | 1000 | 0.126000 | 0.546278 | 0.571627 | 2722.199849 | 0.004898 | 192 |
| all | CADFit | 1000 | 0.045000 | 0.888362 | 0.990633 | 33.653187 | 0.000839 | 192 |
| deepcad | P1v2 | 956 | 0.121339 | 0.580602 | 0.610635 | 0.055456 | 0.002352 | 163 |
| deepcad | CADFit | 956 | 0.046025 | 0.877797 | 0.990458 | 0.003769 | 0.000652 | 163 |
| fusion360 | P1v2 | 44 | 0.227273 | 0.353356 | 0.237846 | 18022.528677 | 212.524873 | 29 |
| fusion360 | CADFit | 44 | 0.022727 | 0.947742 | 0.991498 | 222.786122 | 4.165757 | 29 |

## Old P1 vs P1v2 vs CADFit on the same triple-common cases

| Dataset | Method | IR (full dataset) | IoU mean | IoU median | CD mean | CD median | Triple N |
|---|---|---:|---:|---:|---:|---:|---:|
| all | Old P1 | 0.062000 | 0.572646 | 0.665042 | 42094.862434 | 0.001931 | 188 |
| all | P1v2 | 0.126000 | 0.555437 | 0.578750 | 2780.115993 | 0.004383 | 188 |
| all | CADFit | 0.045000 | 0.891339 | 0.990419 | 34.369205 | 0.000846 | 188 |
| deepcad | Old P1 | 0.058577 | 0.677010 | 0.749511 | 0.021929 | 0.001472 | 159 |
| deepcad | P1v2 | 0.121339 | 0.592295 | 0.620807 | 0.053302 | 0.002345 | 159 |
| deepcad | CADFit | 0.046025 | 0.881051 | 0.990379 | 0.003856 | 0.000653 | 159 |
| fusion360 | Old P1 | 0.136364 | 0.000443 | 0.000029 | 272890.712098 | 3929.555380 | 29 |
| fusion360 | P1v2 | 0.227273 | 0.353356 | 0.237846 | 18022.528677 | 212.524873 | 29 |
| fusion360 | CADFit | 0.022727 | 0.947742 | 0.991498 | 222.786122 | 4.165757 | 29 |

## Conclusion

P1v2 does not exceed CADFit on DeepCAD or Fusion360. On the triple-common Fusion360 cohort, P1v2 improves strongly over old P1 (IoU 0.000443 -> 0.353356; CD 272890.712098 -> 18022.528677), but remains behind CADFit (IoU 0.947742; CD 222.786122). On DeepCAD, P1v2 regresses versus old P1 in IoU, CD, and IR.

IR uses the full dataset denominator. IoU/CD use only frozen-GT-valid strict common-valid cases. Lower CD and IR are better; higher IoU is better.
