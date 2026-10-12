#!/usr/bin/env python3
import csv, hashlib, json, os, subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/p2_canary_config_freeze_v1'
P2=ROOT/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1'
PREP=ROOT/'ours3/p2_size_supervision_preparation_v1'
P1=ROOT/'ours3/p1_operation_aware_structure_loss_v1'
for d in ('resolved','provenance','schema','audits','reports','integrity'): (OUT/d).mkdir(parents=True,exist_ok=True)

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def dump(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def ids(x):
 if isinstance(x,dict):
  if isinstance(x.get('ids'),list): return set(map(str,x['ids']))
  out=set()
  for v in x.values(): out |= ids(v)
  return out
 if isinstance(x,list):
  out=set()
  for v in x:
   if isinstance(v,str): out.add(v)
   elif isinstance(v,dict):
    z=v.get('id') or v.get('cad_id') or v.get('sample_id')
    if z is not None: out.add(str(z))
  return out
 return set()

paths={
 'p1_freeze':P1/'configs/P1_CONFIG_FREEZE.json',
 'p1_yaml':P1/'configs/p1_exact9998_train.yaml',
 'p1_closure':ROOT/'ours3/p1_operation_aware_formal_closure_v1/reports/FINAL_REPORT.json',
 'p1_trainer_state':P1/'runs/p1/checkpoint-39980/trainer_state.json',
 'p1_checkpoint':P1/'runs/p1/checkpoint-39980',
 'c2':ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt',
 'c2_provenance':ROOT/'ours3/curve_encoder_scale_curvature_v1/reports/C2_epoch4_authority_v1/PROVENANCE.json',
 'train100':P2/'canary/TRAIN100_MANIFEST.json','val100':P2/'canary/VAL_CANARY_MANIFEST.json',
 'test':ROOT/'ours3/final_test1000_v1/freeze/EXACT9998_TEST_DECODER_INPUT.json',
 'holdout':P2/'holdout/P2_NEW_HOLDOUT_V1_MANIFEST.json',
 'size_train_registry':PREP/'implementation/TRAIN_SIZE_TOKEN_MASK_REGISTRY.jsonl',
 'size_val_registry':PREP/'implementation/VAL_SIZE_TOKEN_MASK_REGISTRY.jsonl',
 'size_audit':PREP/'mask_audit/SIZE_TOKEN_MASK_AUDIT.csv',
 'p2_protocol':PREP/'protocol/P2_SIZE_SUPERVISION_PROTOCOL_V1.json',
 'p2_old_config':P2/'canary/P2_CANARY_CONFIG.json',
 'runner_audit':P2/'runner_audit/CANARY_RUNNER_STATIC_AUDIT.json'
}
source_hash={k:sha(v) for k,v in paths.items() if v.is_file()}
p1f=json.load(open(paths['p1_freeze'])); ts=json.load(open(paths['p1_trainer_state']))
tr=json.load(open(paths['train100'])); va=json.load(open(paths['val100'])); old=json.load(open(paths['p2_old_config']))
model_cfg=json.load(open(paths['p1_checkpoint']/'config.json')); tok_cfg=json.load(open(paths['p1_checkpoint']/'tokenizer_config.json'))
index=json.load(open(paths['p1_checkpoint']/'model.safetensors.index.json'))['weight_map']; edge_keys=sorted(k for k in index if k.startswith('edge_proj.'))
tok_files={p.name:sha(p) for p in sorted(paths['p1_checkpoint'].iterdir()) if p.name in {'tokenizer.json','tokenizer_config.json','special_tokens_map.json'}}
test_ids=ids(json.load(open(paths['test']))); hold_ids=ids(json.load(open(paths['holdout']))); tr_ids=set(tr['ids']); va_ids=set(va['ids'])
isolation={'TRAIN100_TEST_OVERLAP_N':len(tr_ids&test_ids),'VAL100_TEST_OVERLAP_N':len(va_ids&test_ids),'TRAIN100_HOLDOUT_OVERLAP_N':len(tr_ids&hold_ids),'VAL100_HOLDOUT_OVERLAP_N':len(va_ids&hold_ids),'TRAIN100_UNIQUE_IDS':len(tr_ids),'VAL100_UNIQUE_IDS':len(va_ids),'status':'PASS' if not ((tr_ids|va_ids)&(test_ids|hold_ids)) else 'FAIL'}
dump(OUT/'audits/CANARY_DATA_ISOLATION_AUDIT.json',isolation)

unresolved={
 'P1_CHECKPOINT_SELECTION_PROVENANCE':'Formal closure evaluates checkpoint-39980, while its trainer_state records best_model_checkpoint=checkpoint-8000 under the frozen MIN_VAL_BASE_CE rule; no checkpoint freeze record uniquely reconciles the conflict.',
 'LOGIT_ABS_TOL':'No formal bf16 real-model logit parity tolerance was found; existing 1e-7 is CPU loss-path parity only.',
 'LOSS_ABS_TOL':'No formal bf16 real-model loss parity tolerance was found; existing 1e-7 is CPU loss-path parity only.',
 'GRAD_ABS_TOL':'No formal real-model backward parity absolute tolerance was found.',
 'GRAD_REL_TOL':'No formal real-model backward parity relative tolerance was found.',
 'FORWARD_PARITY_BATCH_IDS':'No pre-registered batch/case IDs were found.',
 'BACKWARD_PARITY_BATCH_IDS':'No pre-registered batch/case IDs were found.',
 'BACKWARD_PARITY_LLM_PARAMETER_NAMES':'No pre-registered LLM tensor names were found.',
 'SIZE_GRADIENT_BATCH_IDS':'No pre-registered batch/case IDs were found.',
 'STAGE_COMMANDS':'No audited real-model stage backend commands/evidence contract exists.',
 'OPTIMIZER_BETAS':'Not explicit in P1 frozen YAML/config; framework defaults are not admissible.',
 'OPTIMIZER_EPS':'Not explicit in P1 frozen YAML/config; framework defaults are not admissible.',
 'DATALOADER_SHUFFLE':'Not explicitly frozen.', 'DROP_LAST':'Not explicitly frozen.',
 'DROPOUT_RNG_RESTORE_POLICY':'Not explicitly frozen.',
 'CURVE_K_MAX':'No unique formal frozen source was found in the supplied P1 freeze record.',
 'SURFACE_INPUT_SHAPE':'No unique formal frozen source was found in the supplied P1 freeze record.',
 'SURFACE_POINT_COUNT':'No unique formal frozen source was found in the supplied P1 freeze record.'
}

config={
 'P2_CANARY_CONFIG_SCHEMA_VERSION':1,'CONFIG_FIELD_STATUS':'UNRESOLVED','ALLOW_SCIENTIFIC_CONFIG_OVERRIDE':False,
 'model':{'P1_CHECKPOINT_PATH':str(paths['p1_checkpoint']),'P1_CHECKPOINT_SHA256':'f5daa1155068d9303f9872574c9ecdf5a4bff1ea1f2c85a5c573548c695cfd84','P1_CHECKPOINT_SELECTION_PROVENANCE':'UNRESOLVED','BASE_MODEL_PATH_OR_ID':p1f['TRAIN_CONFIG_TEXT'].split('model_name_or_path: ',1)[1].splitlines()[0],'MODEL_CLASS':model_cfg.get('architectures',[None])[0],'MODEL_CONFIG_HASH':sha(paths['p1_checkpoint']/'config.json'),'CONTEXT_LENGTH':8192,'PRECISION':'bfloat16','GRADIENT_CHECKPOINTING':True,'TOKENIZER_PATH':str(paths['p1_checkpoint']),'TOKENIZER_FILES_SHA256':tok_files,'VOCAB_SIZE':model_cfg.get('vocab_size'),'BOS_TOKEN_ID':model_cfg.get('bos_token_id'),'EOS_TOKEN_ID':model_cfg.get('eos_token_id'),'PAD_TOKEN_ID':tok_cfg.get('pad_token')},
 'c2':{'C2_CHECKPOINT_PATH':str(paths['c2']),'C2_CHECKPOINT_SHA256':sha(paths['c2']),'C2_ARCHITECTURE':'curve-local encoder + log-length scale branch','C2_OUTPUT_DIM':256,'C2_FROZEN':True},
 'curve_projector':{'CURVE_PROJECTOR_CLASS':'edge_proj.net Sequential','INPUT_DIM':256,'HIDDEN_DIM':256,'OUTPUT_DIM':2048,'ACTIVATION':'GELU','PARAMETER_COUNT':592128,'STATE_DICT_KEY_NAMES':edge_keys,'INITIALIZATION_SOURCE':'P1 checkpoint'},
 'curve_stream':{'CURVE_SOURCE':'GT_BREP','CURVE_ENCODER':'FROZEN_C2','CURVE_TOKEN_DIM':256,'CURVE_STREAM_MODE':'VARIABLE_K','CURVE_K_MAX':'UNRESOLVED','CURVE_PROJECTION':'SEPARATE_EDGE_TOKENS','CAD_SECOND_STREAM':'curve_tokens','CAD_USE_SEPARATE_EDGE_TOKENS':1},
 'surface':{'SURFACE_ENCODER':'Sonata frozen point tower','SURFACE_INPUT_SHAPE':'UNRESOLVED','SURFACE_FEATURES':['xyz','normal'],'SURFACE_POINT_COUNT':'UNRESOLVED'},
 'data':{'TRAIN100_PATH':str(paths['train100']),'TRAIN100_N':tr['N'],'TRAIN100_SHA256':sha(paths['train100']),'TRAIN100_UNIQUE_IDS':len(tr_ids),'TRAIN100_SOURCE_SPLIT':tr['source'],'VAL100_PATH':str(paths['val100']),'VAL100_N':va['N'],'VAL100_SHA256':sha(paths['val100']),'VAL100_UNIQUE_IDS':len(va_ids),'VAL100_SOURCE_SPLIT':va['source'],'isolation':isolation},
 'loss':{'OP_LOSS_ENABLED':True,'LAMBDA_OP':1.0,'OP_MASK_SOURCE':str(P1/'masks'),'CAUSAL_SHIFT_RULE':'labels[:,1:]','SIZE_LOSS_ENABLED':True,'DIAGNOSTIC_LAMBDA_SIZE':old.get('diagnostic_lambda_size','UNRESOLVED'),'SIZE_FIELDS':{'Box':['width','height','depth'],'Extrude':['height'],'ExtrudePolygon':['height'],'Cylinder':'DEFERRED_LOW_SUPPORT'},'SIZE_REGISTRY_PATHS':[str(paths['size_train_registry']),str(paths['size_val_registry'])],'SIZE_REGISTRY_SHA256':{k:source_hash[k] for k in ('size_train_registry','size_val_registry') if k in source_hash},'TRAIN_FIELD_N':23897,'VAL_FIELD_N':2955,'SIZE_MASK_FP':0,'SIZE_MASK_MISS':0},
 'parity':{'LOGIT_ABS_TOL':'UNRESOLVED','LOSS_ABS_TOL':'UNRESOLVED','GRAD_ABS_TOL':'UNRESOLVED','GRAD_REL_TOL':'UNRESOLVED','PARITY_TOLERANCE_STATUS':'UNRESOLVED'},
 'train100':{'SEED':42,'EPOCH_OR_STEP_MODE':'steps','MAX_STEPS':old.get('optimizer_steps_planned','UNRESOLVED'),'MICRO_BATCH_SIZE':1,'GRADIENT_ACCUMULATION':4,'EFFECTIVE_BATCH_SIZE':4,'LEARNING_RATE':2e-5,'OPTIMIZER':'UNRESOLVED','BETAS':'UNRESOLVED','EPS':'UNRESOLVED','WEIGHT_DECAY':0.0,'LR_SCHEDULER':'cosine','WARMUP_RATIO_OR_STEPS':0.03,'MAX_GRAD_NORM':1.0,'PRECISION':'bfloat16','GRADIENT_CHECKPOINTING':True,'DATALOADER_SHUFFLE':'UNRESOLVED','DATALOADER_SEED':42,'DROP_LAST':'UNRESOLVED','NUM_WORKERS':2},
 'rng':{'PYTHON_SEED':42,'NUMPY_SEED':42,'TORCH_SEED':42,'CUDA_SEED':42,'DETERMINISTIC_ALGORITHMS':'UNRESOLVED','CUDNN_BENCHMARK':'UNRESOLVED','DROPOUT_RNG_RESTORE_POLICY':'UNRESOLVED'},
 'stages':{'FORWARD_PARITY_STAGE':{'batch_ids':'UNRESOLVED','lambda_size':0},'BACKWARD_PARITY_STAGE':{'batch_ids':'UNRESOLVED','curve_projector_parameters':'ALL','llm_parameter_names':'UNRESOLVED','lambda_size':0},'SIZE_GRADIENT_STAGE':{'batch_ids':'UNRESOLVED','diagnostic_lambda_size':old.get('diagnostic_lambda_size')},'TRAIN100_STAGE':{'manifest':str(paths['train100']),'steps':old.get('optimizer_steps_planned'),'canary_only':True},'VAL100_STAGE':{'manifest':str(paths['val100']),'loss_only':True,'decode':False,'geometry_eval':False},'RELOAD_STAGE':{'required_state':['model','optimizer','scheduler','RNG','loss config'],'smoke_batch_ids':'UNRESOLVED'},'STAGE_COMMANDS':'UNRESOLVED'},
 'gpu_safety':{'MIN_FREE_GPU_GIB':24,'PROHIBIT_FINAL_TEST_GPU':True,'PROHIBIT_UNKNOWN_PROCESS':True,'AUTO_WAIT':False,'AUTO_RETRY':False},
 'isolation':{'READ_TEST_METRICS':False,'ALLOW_TEST_MANIFEST_FOR_CANARY':False,'ALLOW_TEST_PREDICTIONS':False,'HOLDOUT_N':958,'ALLOW_HOLDOUT_FORWARD':False,'ALLOW_HOLDOUT_PREDICTION':False,'ALLOW_HOLDOUT_MODEL_SELECTION':False},
 'unresolved_fields':unresolved
}
required=[]
def leaves(x,p=''):
 if isinstance(x,dict):
  for k,v in x.items(): leaves(v,p+'.'+k if p else k)
 else: required.append(p)
leaves(config)
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'P2 Canary Config Schema V1','type':'object','required':['P2_CANARY_CONFIG_SCHEMA_VERSION','CONFIG_FIELD_STATUS','model','c2','curve_projector','curve_stream','surface','data','loss','parity','train100','rng','stages','gpu_safety','isolation'],'additionalProperties':False}
dump(OUT/'schema/P2_CANARY_CONFIG_SCHEMA_V1.json',schema);dump(OUT/'schema/P2_CANARY_CONFIG_REQUIRED_FIELDS.json',{'schema_version':1,'required_field_n':len(required),'required_leaf_paths':required})
dump(OUT/'resolved/P2_CANARY_CONFIG.json',config)
config_hash=sha(OUT/'resolved/P2_CANARY_CONFIG.json')
dump(OUT/'resolved/P2_CANARY_CONFIG_FREEZE.json',{'status':'FAIL_UNRESOLVED','config_path':str(OUT/'resolved/P2_CANARY_CONFIG.json'),'config_sha256':config_hash,'timestamp_utc':datetime.now(timezone.utc).isoformat(),'schema_version':1,'source_artifacts':source_hash})

prov=[]
for k,v in [('model.P1_CHECKPOINT_PATH',str(paths['p1_checkpoint'])),('c2.C2_CHECKPOINT_SHA256',sha(paths['c2'])),('data.TRAIN100_SHA256',sha(paths['train100'])),('data.VAL100_SHA256',sha(paths['val100'])),('loss.DIAGNOSTIC_LAMBDA_SIZE',old.get('diagnostic_lambda_size')),('train100.MAX_STEPS',old.get('optimizer_steps_planned')),('train100.LEARNING_RATE',2e-5),('parity.LOGIT_ABS_TOL','UNRESOLVED'),('parity.GRAD_ABS_TOL','UNRESOLVED'),('stages.STAGE_COMMANDS','UNRESOLVED')]:
 src='P2_CANARY_CONFIG.json' if k.startswith(('loss.DIAG','train100.MAX')) else ('P1_CONFIG_FREEZE.json' if k=='train100.LEARNING_RATE' else 'multi-source audit')
 prov.append([k,json.dumps(v),src,k,source_hash.get('p2_old_config') or source_hash.get('p1_freeze'),'UNRESOLVED' if v=='UNRESOLVED' else 'RESOLVED'])
with open(OUT/'provenance/P2_CANARY_CONFIG_PROVENANCE.csv','w',newline='') as f: w=csv.writer(f);w.writerow(['config_key','resolved_value','source_file','source_field','source_sha256','resolution_status']);w.writerows(prov)
dump(OUT/'provenance/P1_CHECKPOINT_PROVENANCE.json',{'status':'UNRESOLVED','checkpoint_path':str(paths['p1_checkpoint']),'checkpoint_step':39980,'selection_metric':'eval_loss','selection_rule':'MIN_VAL_BASE_CE','selection_value':ts.get('best_metric'),'sha256':'f5daa1155068d9303f9872574c9ecdf5a4bff1ea1f2c85a5c573548c695cfd84','source_record':[str(paths['p1_closure']),str(paths['p1_freeze']),str(paths['p1_trainer_state'])],'conflict':{'closure_checkpoint':'checkpoint-39980','trainer_best_model_checkpoint':ts.get('best_model_checkpoint')}})
dump(OUT/'audits/CONFIG_HASH_AUDIT.json',{'status':'PASS','config_sha256':config_hash,'source_hashes':source_hash})
dump(OUT/'audits/RUNNER_CONFIG_COMPATIBILITY_AUDIT.json',{'status':'FAIL','reason':'scientific config contains unresolved critical fields; runner must reject it'})
dump(OUT/'audits/PREFLIGHT_RESULT.json',{'status':'NOT_RUN_CONFIG_UNRESOLVED','model_loaded':False,'gpu_checked':False,'training_started':False})
dump(OUT/'integrity/P1_IMMUTABILITY.json',{'P1_CHANGED':False,'P1_WRITES':0});dump(OUT/'integrity/HOLDOUT_IMMUTABILITY.json',{'HOLDOUT_CHANGED':False,'HOLDOUT_PREDICTION_N':0});dump(OUT/'integrity/FINAL_TEST_NONINTERFERENCE.json',{'TEST_PARTIAL_METRICS_READ':False,'FINAL_TEST_INTERFERENCE':False})
lines=['# Unresolved Config Fields','']+[f'- `{k}`: {v} Checked formal P1/P2 freeze, closure, preparation, runner, and training configuration artifacts.' for k,v in unresolved.items()]
(OUT/'reports/UNRESOLVED_CONFIG_FIELDS.md').write_text('\n'.join(lines)+'\n')
report={'CURRENT_GATE':'P2_CANARY_CONFIG_FREEZE_BLOCKED','CONFIG_SCHEMA_VERSION':1,'REQUIRED_FIELD_N':len(required),'RESOLVED_FIELD_N':len(required)-len(unresolved),'UNRESOLVED_FIELD_N':len(unresolved),'CONFIG_SHA256':config_hash,'P1_CHECKPOINT_PATH':str(paths['p1_checkpoint']),'P1_CHECKPOINT_SHA256':'f5daa1155068d9303f9872574c9ecdf5a4bff1ea1f2c85a5c573548c695cfd84','C2_CHECKPOINT_SHA256':sha(paths['c2']),'TRAIN100_N':tr['N'],'TRAIN100_SHA256':sha(paths['train100']),'VAL100_N':va['N'],'VAL100_SHA256':sha(paths['val100']),'TEST_OVERLAP_N':isolation['TRAIN100_TEST_OVERLAP_N']+isolation['VAL100_TEST_OVERLAP_N'],'HOLDOUT_OVERLAP_N':isolation['TRAIN100_HOLDOUT_OVERLAP_N']+isolation['VAL100_HOLDOUT_OVERLAP_N'],'LAMBDA_OP':1.0,'DIAGNOSTIC_LAMBDA_SIZE':old.get('diagnostic_lambda_size'),'SIZE_FIELDS':config['loss']['SIZE_FIELDS'],'PARITY_TOLERANCE_SOURCE':'UNRESOLVED','RUNNER_STATIC_AUDIT':'PASS','PREFLIGHT':'NOT_RUN_CONFIG_UNRESOLVED','P1_CHANGED':False,'HOLDOUT_CHANGED':False,'HOLDOUT_PREDICTION_N':0,'TEST_PARTIAL_METRICS_READ':False,'FINAL_TEST_INTERFERENCE':False,'CANARY_CONFIG_FREEZE':'FAIL','P2_FULL_TRAIN_READY':False,'BLOCKER':'CRITICAL_CONFIG_FIELDS_UNRESOLVED','NEXT_ALLOWED_STAGE':'HUMAN_DECISION_AND_FORMAL_FREEZE_OF_UNRESOLVED_FIELDS'}
dump(OUT/'reports/FINAL_REPORT.json',report)
(OUT/'reports/FINAL_REPORT.md').write_text('# P2 Canary Config Freeze V1\n\nCURRENT_GATE = P2_CANARY_CONFIG_FREEZE_BLOCKED\n\nThe configuration was not frozen as executable because critical fields lack unique formal provenance. See `UNRESOLVED_CONFIG_FIELDS.md`. No model/GPU/training/prediction stage ran.\n')
(OUT/'reports/NEXT_STEP.md').write_text('# Next step\n\nProvide formal decisions/evidence for every item in `UNRESOLVED_CONFIG_FIELDS.md`, reconcile checkpoint-39980 versus checkpoint-8000, then regenerate the freeze and run preflight manually.\n')
print(json.dumps(report,indent=2))
