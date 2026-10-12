import json
from pathlib import Path
O=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1v2_size_placement_overfit32_v1')
for x in json.loads((O/'registry/PARAMETER_FIELD_TOKEN_REGISTRY.jsonl').read_text().splitlines()[0]) if False else []: pass
lines=[json.loads(x) for x in (O/'registry/PARAMETER_FIELD_TOKEN_REGISTRY.jsonl').read_text().splitlines()]
(O/'implementation').mkdir(exist_ok=True)
(O/'implementation/TRAIN_SIZE_TOKEN_MASK_REGISTRY.jsonl').write_text('\n'.join(json.dumps({'response_sha256':x['response_sha256'],'size_spans':x['size_spans']+x['placement_spans']}) for x in lines)+'\n')
(O/'implementation/VAL_SIZE_TOKEN_MASK_REGISTRY.jsonl').write_text((O/'implementation/TRAIN_SIZE_TOKEN_MASK_REGISTRY.jsonl').read_text())
base=(Path('/data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_surface_line_ablation_v1/configs/a1_exact9998_train.yaml').read_text())
for arm,rt in [('control','control_runtime.py'),('size_place','size_place_runtime.py')]:
 s=base
 s=s.replace('model_name_or_path: /data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1','model_name_or_path: /data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_surface_line_ablation_v1/runs/a1/checkpoint-6000')
 s=s.replace('dataset_dir: /data/home/cuiyuehan/project/mesh2cad/ours3/exact9998_v1',f'dataset_dir: {O}/manifests')
 s=s.replace('output_dir: /data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_surface_line_ablation_v1/runs/a1',f'output_dir: {O}/runs/{arm}')
 s=s.replace('num_train_epochs: 20','num_train_epochs: 125')
 s=s.replace('num_train_epochs: 125','num_train_epochs: 125\nmax_steps: 1000')
 s=s.replace('eval_steps: 250','eval_steps: 50').replace('save_steps: 250','save_steps: 100').replace('save_total_limit: 4','save_total_limit: 3')
 (O/f'configs_{arm}.yaml').write_text(s)
 launch=f'''#!/bin/bash
set -e
export CUDA_VISIBLE_DEVICES={2 if arm=="control" else 7}
export CAD_SECOND_STREAM=curve_tokens
export CAD_USE_SEPARATE_EDGE_TOKENS=1
export CURVE_TOKEN_ROOT={Path('/data/home/cuiyuehan/project/mesh2cad/ours3/exact9998_curve_tokens_c2_v1')}
export CURVE_TOKEN_REGISTRY={Path('/data/home/cuiyuehan/project/mesh2cad/ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl')}
export REQUIRE_CURVE_TOKEN_REGISTRY=1
export C2_CHECKPOINT_PATH={Path('/data/home/cuiyuehan/project/mesh2cad/ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt')}
export P1_LAMBDA_OP=1.0
export P1V2_LAMBDA_SIZE=1.0
export P1_RUNTIME_STATS={O}/runs/{arm}/runtime_stats.json
export ZERO_LR_AUDIT_PATH={O}/audits/ZERO_LR_{arm}.json
cd {Path('/data/home/cuiyuehan/project/mesh2cad')}
exec /data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python {O}/launch_{arm}.py {O}/configs_{arm}.yaml
'''
 (O/f'launch_{arm}.sh').write_text(launch)
 (O/f'launch_{arm}.py').write_text(f'''import os,sys
from pathlib import Path
ROOT=Path("/data/home/cuiyuehan/project/mesh2cad");EXP=ROOT/"ours3/p1v2_size_placement_overfit32_v1"
sys.path[:0]=[str(EXP),str(ROOT),str(ROOT/"scripts"),str(ROOT/"ours3/m2_exact9998_corrected_m2_train_v1/launch"),str(ROOT/"SpatialLM")]
os.environ["P1V2_CONFIG_OVERRIDE"]=sys.argv[1]
import corrected_m2_runtime_audit;corrected_m2_runtime_audit.install()
import {"p1_operation_loss_runtime" if arm=="control" else "p2_size_loss_runtime"};{"p1_operation_loss_runtime" if arm=="control" else "p2_size_loss_runtime"}.install()
from spatiallm_curve_token_v1.train_curve_token_spatiallm import main
sys.argv=[sys.argv[0],sys.argv[1]]
raise SystemExit(main())
''')
print('configured')
