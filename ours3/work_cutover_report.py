import json
from pathlib import Path
o=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1')
(o/'runtime_cutover').mkdir(exist_ok=True)
(o/'runtime_cutover/ACTUAL_RUNTIME_CALLGRAPH.md').write_text('Actual runtime: launch_size_place.py -> train main -> DataCollator -> p2_size_loss_runtime -> splice -> Trainer compute_loss -> loss -> optimizer. Live collator still uses legacy token-id matching.')
r={'CURRENT_GATE':'REAL_RUNTIME_CUTOVER_BLOCKED_LEGACY_MATCHER','PLACEMENT_MASK_SOURCE':'native_offsets','INPUT_ID_PARITY':'PASS','DATASET_PLACEMENT_FIELDS':219,'COLLATOR_PLACEMENT_FIELDS':219,'TRAINER_USES_BATCH_NATIVE_MASK':False,'LEGACY_PLACEMENT_MATCHER_ENABLED':True,'REAL_TRAINER_INTEGRATION_STATUS':'FAIL','GPU3_TOUCHED':False,'P1V2_FULL_TRAIN_MODIFIED':False,'TEST1000_REUSED':'NO','HOLDOUT958_PREDICTION_N':0}
(o/'audits/REAL_TRAINER_CANARY_FINAL_V2.json').write_text(json.dumps(r,indent=2)+'\n')
(o/'reports/RUNTIME_CUTOVER_REPORT.md').write_text('CURRENT_GATE = REAL_RUNTIME_CUTOVER_BLOCKED_LEGACY_MATCHER\n\nNative alignment passes 219/219, but live collator still uses legacy token-id matching. No valid Trainer canary or OVERFIT32 run was started. GPU 3 was untouched.\n')
(o/'reports/FINAL_REPORT.md').write_text('CURRENT_GATE = REAL_RUNTIME_CUTOVER_BLOCKED_LEGACY_MATCHER\n')
(o/'reports/FINAL_REPORT.json').write_text(json.dumps(r,indent=2)+'\n')

