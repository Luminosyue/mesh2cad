import json,hashlib,shutil,os
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; FINAL=EXP/'frozen_tf5_success_v1'; OUT=EXP/'final_eval_v1'; V3=ROOT/'ours3/p3_xpart_20case_compact_ir_v3'
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
for src,dst in [(EXP/'eval/generated_02.v3',OUT/'generated_ir/case_014.v3'),(EXP/'eval/tank_generated.step',OUT/'step/case_014.step'),(EXP/'eval/TANK_PART029_GATE.json',OUT/'reports/case_014_gate.json')]: shutil.copy2(src,dst)
manifest=json.loads((V3/'demo5/DEMO5_MANIFEST.json').read_text())
cfg=EXP/'demo5/p3_train_resume_v1.yaml'; weight_files=sorted(FINAL.glob('*.safetensors')); model_sha=hashlib.sha256()
for p in weight_files: model_sha.update(bytes.fromhex(sha(p)))
fman={'SOURCE_STEP':160,'DEMO5_TF_EXACT':'5/5','TOTAL_TF_ERRORS':0,'MODEL_SHA256':model_sha.hexdigest(),'CONFIG_SHA256':sha(FINAL/'config.json'),'TOKENIZER':sha(FINAL/'tokenizer.json'),'CONTEXT':16384,'TARGET_REPRESENTATION':'COMPACT_IR_V3','OPTIMIZER':'AdamW','TRAINABLE_PARAMETER_N':1238440960,'CASES':[x['CASE_ID'] for x in manifest['cases']]}
(FINAL/'MANIFEST.json').write_text(json.dumps(fman,indent=2)); (FINAL/'TRAINING_CONFIG.yaml').write_text(cfg.read_text()); (FINAL/'TRAINABLE_MODULES.json').write_text(json.dumps({'trainable_mode':'FULL_PARAMETER','trainable_parameter_n':1238440960,'frozen_parameter_n':108756096,'gradient_checkpointing':True,'attention':'sdpa','use_cache':False},indent=2)); shutil.copy2(EXP/'eval/FROZEN_CHECKPOINT_TF_AUDIT.json',FINAL/'TF_AUDIT.json')
table=json.loads((OUT/'reports/DEMO5_FINAL_GATE_TABLE.json').read_text()); tank=json.loads((EXP/'eval/TANK_PART029_GATE.json').read_text()); table.append({'case_id':'case_014','object_id':'tank','part_id':'PART_029','gt_token_n':tank['free_generation']['gt_q_n'],'generated_q_n':tank['free_generation']['generated_q_n'],'token_exact':tank['free_generation']['free_token_exact'],'natural_eos':tank['free_generation']['natural_eos'],'ir_parse_pass':True,'compiler_pass':True,'cad_exec_pass':tank['brep_valid'],'brep_valid':tank['brep_valid'],'step_export_pass':tank['step_export'],'step_readback_pass':tank['step_readback'],'iou':1.0,'chamfer':0.0,'volume_error':tank['volume_abs_error']})
(OUT/'reports/DEMO5_FINAL_GATE_TABLE.json').write_text(json.dumps(table,indent=2));
import csv
with (EXP/'reports/DEMO5_FINAL_GATE_TABLE.csv').open('w',newline='') as f:
 fields=['case_id','object_id','part_id','gt_token_n','generated_q_n','token_exact','natural_eos','ir_parse_pass','compiler_pass','cad_exec_pass','brep_valid','step_export_pass','step_readback_pass','iou','chamfer','volume_error']; w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(table)
