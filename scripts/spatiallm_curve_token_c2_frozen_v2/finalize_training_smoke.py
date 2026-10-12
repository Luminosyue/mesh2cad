#!/usr/bin/env python3
import hashlib,json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
BASE=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_smoke_v1'
V2REPORT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected/reports/c2_corrected_final'
TOKEN_ROOT=ROOT/'ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2'
V1=ROOT/'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v2/V1_FROZEN_SHA256.json';OLD=ROOT/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/placement_fix_retest_v3/DELIVERY_SHA256.json'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def verify_map(p):
 d=json.loads(p.read_text());ok=sum(Path(k).is_file() and sha(Path(k))==v for k,v in d.items());return f'{ok}/{len(d)}'
def verify_token_manifest():
 d=json.loads((V2REPORT/'C2_TOKEN_FILE_MANIFEST.json').read_text());ok=0
 for rel,digest in d['files'].items():
  p=TOKEN_ROOT/rel;ok+=p.is_file() and sha(p)==digest
 return f"{ok}/{len(d['files'])}",d['content_sha256']
arms={'B0':json.loads((BASE/'runs/b0/SMOKE_REPORT.json').read_text()),'B1-BM':json.loads((BASE/'runs/b1_bm/SMOKE_REPORT.json').read_text()),'M2-C2-BM':json.loads((BASE/'runs/m2_c2_bm/SMOKE_REPORT.json').read_text())}
train=json.loads((BASE/'data/pilot_smoke_train.json').read_text());val=json.loads((BASE/'data/pilot_smoke_val.json').read_text());token_status,token_hash=verify_token_manifest();v1=verify_map(V1);old=verify_map(OLD)
def pass_arm(x):return all([x['status']=='PASS',x['forward_pass'],x['backward_pass'],x['nan_count']==x['inf_count']==x['oom_count']==x['entry_budget_failures']==0,x['loss_trend_down'],x['checkpoint_save_pass'],x['checkpoint_load_pass'],x['decode_pass'],x['first_backward_gradient_audit']['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count']==0,x['first_backward_gradient_audit']['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count']==0,x['first_backward_gradient_audit']['LLM']['grad_non_none_parameter_count']>0])
passed=all(pass_arm(x) for x in arms.values()) and arms['B1-BM']['first_backward_gradient_audit']['B1_ENCODER']['trainable_parameter_count']==0 and arms['B1-BM']['first_backward_gradient_audit']['ARM_PROJECTOR']['grad_non_none_parameter_count']>0 and arms['M2-C2-BM']['first_backward_gradient_audit']['C2']['trainable_parameter_count']==arms['M2-C2-BM']['first_backward_gradient_audit']['C2']['grad_non_none_parameter_count']==0 and arms['M2-C2-BM']['first_backward_gradient_audit']['ARM_PROJECTOR']['grad_non_none_parameter_count']>0 and token_status=='5592/5592' and v1=='19580/19580' and old=='3669/3669'
summary={'CURRENT_GATE':'CANONICAL_V2_1K_THREE_ARM_TRAINING_SMOKE_PASS' if passed else 'CANONICAL_V2_1K_THREE_ARM_TRAINING_SMOKE_HARD_STOP','SMOKE_TRAIN_SPLIT':'192 CAD','SMOKE_VAL_SPLIT':'48 CAD','SMOKE_TRAIN_SHA256':train['content_sha256'],'SMOKE_VAL_SHA256':val['content_sha256'],'SAME_CADS_ALL_ARMS':True,'STEPS_PER_ARM':100,'arms':{},'C2_TOKEN_FILES_UNCHANGED':token_status,'C2_TOKEN_MANIFEST_SHA256':token_hash,'V1_FROZEN_HASHES':v1,'OLD_EVIDENCE_HASHES':old,'ALLOW_PILOT_TRAINING':passed,'FORMAL_TRAINING_STARTED':False}
for name,x in arms.items():
 g=x['first_backward_gradient_audit'];summary['arms'][name]={'status':x['status'],'forward':x['forward_pass'],'backward':x['backward_pass'],'first20_train_loss_mean':x['first20_mean'],'last20_train_loss_mean':x['last20_mean'],'post_val_loss_48':x['post_val_loss_48'],'loss_trend_down':x['loss_trend_down'],'nan':x['nan_count'],'inf':x['inf_count'],'oom':x['oom_count'],'training_entry_budget_failures':x['entry_budget_failures'],'checkpoint_save':x['checkpoint_save_pass'],'checkpoint_load':x['checkpoint_load_pass'],'decode':x['decode_pass'],'SONATA_TRAINABLE_PARAM_COUNT':g['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count'],'SONATA_GRAD_NON_NONE_COUNT':g['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count'],'C2_TRAINABLE_PARAM_COUNT':g['C2']['trainable_parameter_count'],'C2_GRAD_NON_NONE_COUNT':g['C2']['grad_non_none_parameter_count'],'B1_ENCODER_TRAINABLE_PARAM_COUNT':g['B1_ENCODER']['trainable_parameter_count'],'B1_ENCODER_GRAD_NON_NONE_COUNT':g['B1_ENCODER']['grad_non_none_parameter_count'],'PROJECTOR_TRAINABLE_PARAM_COUNT':g['ARM_PROJECTOR']['trainable_parameter_count'],'PROJECTOR_GRAD_NON_NONE_COUNT':g['ARM_PROJECTOR']['grad_non_none_parameter_count'],'LLM_TRAINABLE_PARAM_COUNT':g['LLM']['trainable_parameter_count'],'LLM_GRAD_NON_NONE_COUNT':g['LLM']['grad_non_none_parameter_count']}
out=BASE/'reports';out.mkdir(parents=True,exist_ok=False);(out/'FINAL_SMOKE_GATE.json').write_text(json.dumps(summary,indent=2)+'\n');(out/'FINAL_SMOKE_GATE.md').write_text('# Three-arm canonical training smoke\n\n'+json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2));raise SystemExit(0 if passed else 2)
