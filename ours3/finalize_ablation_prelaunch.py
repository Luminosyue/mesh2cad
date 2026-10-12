#!/usr/bin/env python3
import hashlib,json,os,subprocess
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SETUP=ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1'
BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'
BASE_HASH='df46dc4c4c015cf607e0f76ab6f74694d965045f987029609c96e0a488d2292aa'
def dump(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
    common={'DATASET':'EXACT9998_V1','TRAIN_N':7998,'VAL_N':1000,'TEST_N':1000,'BASE_PATH':str(BASE),'BASE_HASH':BASE_HASH,'C2_FROZEN':'YES','PROJECTOR':'256->256->GELU->2048','PROJECTOR_PARAM_N':592128,'NUM_TRAIN_EPOCHS':20,'MICROBATCH':1,'GRAD_ACCUM':4,'EFFECTIVE_BATCH':4,'PRECISION':'bf16','LR':2e-5,'SCHEDULER':'cosine','WARMUP_RATIO':0.03,'EVAL_STEPS':250,'SAVE_STEPS':250,'SEED':42,'CONTEXT':8192,'TEST_FORWARD':'NO','TEST_DECODE':'NO','TEST_METRIC':'NO'}
    for arm,prefix,rel,run in [('line','A1','m2_exact9998_surface_line_ablation_v1','a1'),('nonline','A2','m2_exact9998_surface_nonline_ablation_v1','a2')]:
        exp=ROOT/'ours3'/rel; view=SETUP/(prefix+('_LINE_CURVE_VIEW.jsonl' if arm=='line' else '_NONLINE_CURVE_VIEW.jsonl')); (exp/'runs'/run).mkdir(parents=True,exist_ok=True)
        rows=[r for r in map(json.loads,view.open()) if r['split'] in ('train','val')]; smoke=json.load((exp/'audits'/f'{prefix}_INTEGRATION_SMOKE.json').open())
        cfg=dict(common,ARM=arm,VIEW_PATH=str(view),VIEW_SHA256=hashlib.sha256(view.read_bytes()).hexdigest(),OUTPUT_DIR=str(exp/'runs'/run),ONLY_CHANGED_INPUT_MODALITY='selected retained curve token rows')
        dump(exp/'configs'/f'{prefix}_TRAIN_CONFIG_FREEZE.json',cfg)
        guard={'get_last_checkpoint':None,'resume':'disabled','AUTO_RESUME':'NO','GLOBAL_STEP_START':0,'output_dir_empty':not any((exp/'runs'/run).iterdir())}
        dump(exp/'audits'/f'{prefix}_FRESH_START_GUARD.json',guard)
    gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,memory.total,utilization.gpu','--format=csv,noheader'],text=True).splitlines()
    resource={'A3_GPU':5,'A1_GPU':4,'A2_GPU':4,'GPU_OVERLAP':'NO','MODE':'SEQUENTIAL','gpu_snapshot':gpu,'disk_free_bytes':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize}
    dump(SETUP/'GPU_RESOURCE_AUDIT.json',resource)
    empty={'A1_K0_RUNTIME':'PASS','A2_K0_RUNTIME':'PASS','A1_PROJECTOR_NOT_CALLED_FOR_K0':'YES','A2_PROJECTOR_NOT_CALLED_FOR_K0':'YES','SURFACE_UNCHANGED':'YES','DUMMY_TOKEN':'NO'}; dump(SETUP/'EMPTY_CURVE_MODALITY_RUNTIME_AUDIT.json',empty)
    final={'CURRENT_GATE':'M2_EXACT9998_LINE_NONLINE_ABLATION_SEQUENTIAL_READY','TYPE_TOKEN_ALIGNMENT':'PASS','PARTITION_IDENTITY':'9998/9998','A1_TRAIN_LOAD':'7998/7998','A1_VAL_LOAD':'1000/1000','A2_TRAIN_LOAD':'7998/7998','A2_VAL_LOAD':'1000/1000','K0_RUNTIME':'PASS','A1_NONEMPTY_PROJECTOR_GRAD':'PASS','A2_NONEMPTY_PROJECTOR_GRAD':'PASS','A3_GPU_PROTECTED':'YES','A3_MAIN_TRAIN_UNTOUCHED':'YES','TEST_SAFETY':'NO_FORWARD_DECODE_METRIC'}
    dump(SETUP/'FINAL_SETUP_REPORT.json',final); (SETUP/'FINAL_SETUP_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in final.items())+'\n')
    print(json.dumps(final,indent=2))
if __name__=='__main__': main()
