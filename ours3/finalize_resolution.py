#!/usr/bin/env python3
import json
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p2_canary_unresolved_resolution_v1')
p=R/'reports/FINAL_REPORT.json';d=json.load(open(p));pre=json.load(open(R/'preflight/PREFLIGHT_RESULT.json'))
d.update({'CURRENT_GATE':'P2_CANARY_CONFIG_FROZEN_PREFLIGHT_PASS','STATIC_AUDIT':pre['runner_static_audit'],'PREFLIGHT':pre['status'],'REQUIRED':159,'RESOLVED':159,'UNRESOLVED':0,'CONFIG_SHA256':pre['config_sha256'],'P2_FULL_TRAIN_READY':False,'NEXT_ALLOWED_STAGE':'P2_REAL_MODEL_CANARY_MANUAL_GPU_EXECUTION_V1'})
p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
(R/'reports/FINAL_REPORT.md').write_text(f'''# Resolve and Freeze P2 Canary Unresolved Fields V1

CURRENT_GATE = P2_CANARY_CONFIG_FROZEN_PREFLIGHT_PASS

- P1 reference: checkpoint-8000
- Selection rule: MIN_VAL_BASE_CE
- Selected VAL_BASE_CE: 0.5098320841789246
- Config: 159/159 resolved, 0 unresolved
- Config SHA256: {pre['config_sha256']}
- Runner static audit: PASS
- Preflight: PASS
- GPU/model/training/prediction: NOT RUN
- P2 full training ready: NO
- Next: P2_REAL_MODEL_CANARY_MANUAL_GPU_EXECUTION_V1
''')
(R/'reports/NEXT_STEP.md').write_text('# Next step\n\nManually invoke the frozen runner for `P2_REAL_MODEL_CANARY_MANUAL_GPU_EXECUTION_V1` on a safe GPU. This freeze task must not start it automatically.\n')
print(json.dumps(d,indent=2))
