# P1 TANK ALLPARTS EXACT OVERFIT REPORT

TANK_PART_N=45
TOTAL_BLOCK_N=2226
TOTAL_TOKEN_N=2235061
BASE_CHECKPOINT=/data/home/cuiyuehan/project/mesh2cad/ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000

LR=1e-5
MICRO_BATCH_SIZE=1
GRAD_ACCUM_STEPS=3
EFFECTIVE_BATCH_SIZE=3
SAMPLER=deterministic shuffled-cycle balanced Tank-part sampler; max exposure difference <=1
GEOMETRY_DTYPE_ALIGNED=YES
FP32_GATE_EVAL=YES (no free decode launched because TF threshold was not reached)
MAX_EXTRA_UPDATES=1000

FIRST_ALL_TF_ZERO_CHECKPOINT=NONE
FIRST_ALL_EXACT_CHECKPOINT=NONE
BEST_CHECKPOINT=NONE

TF_ZERO_ERROR_N=5/45 at checkpoint-1000
RAW_TOKEN_EXACT_N=0/45 (free decoding not run)
BLOCK_EXACT_N=0/45 (free decoding not run)
EOS_N=0/45 (free decoding not run)
CAD_PARSE_PASS_N=0/45 (free decoding not run)
CAD_EXECUTION_PASS_N=0/45 (free decoding not run)
STEP_EXPORT_PASS_N=0/45 (free decoding not run)
STEP_READBACK_PASS_N=0/45 (free decoding not run)
SAFETY_CAP_HIT_N=0 (free decoding not run)

EXACT_MEMORIZATION_STABLE=NO
P1_TANK_ALLPARTS_GATE=FAIL
NEXT_GATE=diagnose residual multi-sample optimization / conditioning interference; no 3000/5000 expansion started

## Trajectory

| checkpoint | TF errors | zero-error parts | free exact parts |
|---|---:|---:|---:|
| +50 | 668648 | 0/45 | not run |
| +1000 | 528093 | 5/45 | not run |

All 45 GT parts passed the repaired data gate before training. Training stopped at the instructed 1000-update budget. No GT prefix, target length, block count, token deletion, or denominator change was used.
