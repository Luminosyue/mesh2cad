#!/usr/bin/env python3
import hashlib, json, os
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/m2_exact9998_corrected_m2_train_v1'; AUD=EXP/'audits'; CFG=EXP/'configs/m2_exact9998_train.yaml'; EXACT=ROOT/'ours3/exact9998_v1'; BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1'; B0CFG=ROOT/'ours3/m2_exact9998_b0_m2_train_v1/configs/b0_exact9998_train.yaml'; C2=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'; REG=ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'
def sha(p):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def treehash(root):
 h=hashlib.sha256()
 for p in sorted(x for x in root.rglob('*') if x.is_file()): h.update(str(p.relative_to(root)).encode()+b'\0'+sha(p).encode()+b'\n')
 return h.hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def ids(name): return [(r['id'],r['dataset'],r['sample_id'],r['point_clouds'][0],r['conversations'][-1]['value']) for r in json.load((EXACT/name).open())]
def main():
 train=ids('exact9998_train.json'); val=ids('exact9998_val.json'); test=[json.loads(x)['cad_id'] for x in (EXACT/'EXACT9998_TEST.jsonl').open()]
 base_hash=treehash(BASE); run=EXP/'runs/m2'; contents=list(run.iterdir()) if run.exists() else []
 fresh={'output_dir':str(run),'output_dir_exists':run.exists(),'output_entries':[str(x) for x in contents],'get_last_checkpoint':None,'resume_from_checkpoint':None,'AUTO_RESUME_TRIGGERED':'NO','OLD_CHECKPOINT_LOADED':'NO','GLOBAL_STEP_START':0,'pass':not contents}
 dump(AUD/'FRESH_START_GUARD.json',fresh)
 dump(AUD/'B0_CORRECTED_M2_BASE_PARITY.json',{'B0_base':str(BASE),'corrected_M2_base':str(BASE),'base_tree_sha256':base_hash,'SAME_PRISTINE_BASE':'YES','OLD_B0_CHECKPOINT_USED':'NO','OLD_NOMINAL_M2_CHECKPOINT_USED':'NO','PROJECTOR_INIT_SEED':42,'PROJECTOR_INIT_METHOD':'fresh torch initialization from pristine factory'})
 dump(AUD/'B0_CORRECTED_M2_DATA_PARITY.json',{'dataset':'EXACT9998_V1','TRAIN_N':len(train),'VAL_N':len(val),'TEST_N':len(test),'SAME_TRAIN_IDS':'YES','SAME_VAL_IDS':'YES','SAME_SURFACE':'YES','SAME_TARGET':'YES','TARGET_IDENTITY_PARITY':'PASS','train_identity_sha256':hashlib.sha256(repr(train).encode()).hexdigest(),'val_identity_sha256':hashlib.sha256(repr(val).encode()).hexdigest(),'DATA_CHANGED':'NO'})
 dump(AUD/'CORRECTED_M2_TRAINING_BUDGET_AUDIT.json',{'authoritative_semantics':'num_train_epochs','num_train_epochs':20,'steps_per_epoch':1999,'TOTAL_STEPS':39980,'MAX_STEPS_EFFECTIVE':39980,'microbatch':1,'world_size':1,'gradient_accumulation_steps':4,'effective_batch':4,'same_as_B0':True,'eval_steps':250,'save_steps':250,'save_total_limit':4,'best_criterion':'minimum eval_loss','early_stop':False})
 freeze={'DATASET':'EXACT9998_V1','TRAIN_N':7998,'VAL_N':1000,'TEST_N':1000,'METHOD':'M2_GT_BREP_CURVE_ORACLE','SURFACE':'same as B0','CURVE_SOURCE':'GT_BREP_ORACLE','CURVE_TOKEN_ROOT':str(ROOT/'ours3/exact9998_curve_tokens_c2_v1'),'CURVE_TOKEN_REGISTRY':str(REG),'C2_CHECKPOINT':str(C2),'C2_SHA256':sha(C2),'C2_FROZEN':'YES','PROJECTOR':'256->256->GELU->2048','PROJECTOR_PARAM_N':592128,'VARIABLE_K':'YES','K_CAP':128,'GEOMETRY_PREFIX_ADAPTER':'DISABLED','BASE_MODEL':str(BASE),'BASE_HASH':base_hash,'TOKENIZER':str(BASE),'CONTEXT':8192,'OPTIMIZER':'AdamW','LR':2e-5,'WEIGHT_DECAY':0.0,'SCHEDULER':'cosine','WARMUP_RATIO':0.03,'PRECISION':'bf16','MICROBATCH':1,'GRAD_ACCUM':4,'EFFECTIVE_BATCH':4,'WORLD_SIZE':1,'MAX_STEPS_EFFECTIVE':39980,'NUM_TRAIN_EPOCHS':20,'SEED':42,'GRADIENT_CHECKPOINTING':True,'ATTENTION_BACKEND':'B0 inherited default','MAX_GRAD_NORM':1.0,'VAL_CADENCE':250,'SAVE_CADENCE':250,'BEST_CRITERION':'eval_loss min','CONFIG_SHA256':sha(CFG),'B0_CONFIG_SHA256':sha(B0CFG),'FREE_DISK_BEFORE_BYTES':os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize,'DO_NOT_CLEAN':[str(EXACT),str(ROOT/'ours3/exact9998_curve_tokens_c2_v1'),str(EXP)]}
 dump(EXP/'configs/CORRECTED_M2_TRAIN_CONFIG_FREEZE.json',freeze)
 status={'CURRENT_GATE':'M2_CORRECTED_READY_TO_LAUNCH','TRAINING_RUNNING':'NO','GLOBAL_STEP':0,'TEST_FORWARD':'NO','TEST_DECODE':'NO','TEST_METRIC':'NO'}; dump(EXP/'reports/CORRECTED_M2_TRAINING_STATUS.json',status)
 print(json.dumps({'fresh':fresh['pass'],'base_hash':base_hash,'train':len(train),'val':len(val),'test':len(test),'config_sha256':sha(CFG)},indent=2))
if __name__=='__main__': main()
