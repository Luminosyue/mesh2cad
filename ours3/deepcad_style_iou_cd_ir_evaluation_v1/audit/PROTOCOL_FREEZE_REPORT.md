# Frozen DeepCAD-style IoU/CD/IR Protocol V1

- Official DeepCAD commit: f7b350790a3bce0267a5345339fd09be0250c8cb
- Official evaluator source remains unchanged.
- CD: 2000 samples, squared Euclidean, bidirectional, sum of directional means.
- Deterministic sampling: global seed 20260915; case seed is SHA256("20260915:<case_id>") derived.
- IR: invalid prediction count / total case count; invalid is not 1 - STEP Reload.
- IoU: CadQuery/OCC solid BRep Boolean intersection volume / union volume.
- Coordinate frame: DATASET_CANONICAL; P1 identity; CAD-Recode x/200+[0.5,0.5,0.5]; CADFit adapter pending its authoritative coordinate audit.
- Existing V2 Chamfer/H95/Volume and STEP results are preserved and not reused as DeepCAD CD/IR.

## Validation

- IoU GT-vs-GT: 1.0
- IoU disjoint cubes: 0.0
- IoU half-overlap cubes: 0.3333333333333334
- CD identical points: 0.0
- CD deterministic repeated case: PASS
- IR valid/empty/exec-failure/sampling-failure classifier cases: PASS

CURRENT_GATE=DEEPCAD_STYLE_IOU_CD_IR_VAL1000_READY_FOR_P1_CAD_RECODE
FORMAL_VAL1000_STARTED=NO
NEXT_ALLOWED_STAGE=RUN_FROZEN_PROTOCOL_ON_SAME_VAL1000_P1_AND_CAD_RECODE
