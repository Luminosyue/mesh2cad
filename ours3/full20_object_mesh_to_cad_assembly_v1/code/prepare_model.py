import json,sys,csv,hashlib,shutil,os
from pathlib import Path
import numpy as np,trimesh,yaml
from transformers import AutoTokenizer
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1'
STORE=Path('/var/tmp/cuiyuehan_full20_p1_v3_20260925'); STORE.mkdir(parents=True,exist_ok=True)
assert os.stat(STORE).st_dev!=os.stat(O).st_dev
assert shutil.disk_usage('/data').free>15e9 and shutil.disk_usage(STORE).free>120e9
C=R/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1/frozen_tf5_success_v1'
tok=AutoTokenizer.from_pretrained(C,use_fast=False)
sys.path.insert(0,str(R/'scripts'))
from geometry_pack_v1.surface import sample_surface_uniform
priority=['pottery_large','android_figure_orange','cube','baby_car','fire_truck','mini_excavator']
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
allrows=[];blocked=[]; datasets={}
for f in sorted((O/'objects').iterdir()):
 if not f.is_dir():continue
 rows=[];provenance=[];frame=json.loads((f/'OBJECT_FRAME.json').read_text())
 for p in sorted((f/'cad_parts').glob('*/result.json')):
  r=json.loads(p.read_text());pid=r['PART_ID'];cid=f.name+'__'+pid
  if f.name=='tank' and pid=='PART_029':
   blocked.append(dict(object=f.name,part=pid,status='FROZEN_HISTORICAL_REUSE_EXCLUDED_FROM_NEW_TRAIN_AND_GENERATE'));continue
  if not r['PASS']:
   blocked.append(dict(object=f.name,part=pid,status='BLOCKED_LABEL_OR_MISSING_INPUT',reason=r['FAILURE_REASON']));continue
  ir=p.parent/'compact_ir_v3.v3';target=ir.read_text().removesuffix('<|eot_id|>').rstrip()+'\n'
  assert target.startswith('V3 14\n') and target.endswith('\nE\n')
  cloud=E/'data'/f.name/f'{pid}_surface_points.npy';cloud.parent.mkdir(parents=True,exist_ok=True)
  meshpath=Path(r['PART_MESH_PATH']);m=trimesh.load(meshpath,force='mesh',process=False)
  xyz=sample_surface_uniform(m.vertices,m.faces,2048,0)[0]
  xyz=(xyz-np.array(frame['center']))*frame['scale']
  np.save(cloud,np.c_[xyz,np.zeros_like(xyz)].astype(np.float32))
  prompt='<point_cloud>\nGenerate a CAD construction program from the point cloud.\nOutput only valid Compact IR V3 assignments ending with E.\n'
  row=dict(id=cid,dataset='full20_p1_v3',point_clouds=[str(cloud)],conversations=[dict(**{'from':'human'},value=prompt),dict(**{'from':'gpt'},value=target)])
  rows.append(row); allrows.append(row)
  provenance.append(dict(id=cid,object=f.name,part=pid,input_mesh=str(meshpath),input_mesh_sha256=sha(meshpath),point_cloud=str(cloud),point_sha256=sha(cloud),input_frame=frame,target_path=str(ir),target_sha256=sha(ir),target_tokens=len(tok.encode(target,add_special_tokens=False)),label_dir=str(p.parent),curve_tokens_used=False,zero_normal_channels=True))
 if rows:
  d=E/'data'/f.name;dump(d/'train.json',rows);dump(d/'provenance.json',provenance)
  dump(d/'dataset_info.json',{'object_train':dict(file_name='train.json',formatting='sharegpt',columns=dict(messages='conversations',point_clouds='point_clouds'))})
  cutoff=65536 if f.name=='tank' else 32768
  assert max(x['target_tokens'] for x in provenance)+2048<cutoff
  cfg=dict(model_name_or_path=str(C),low_cpu_mem_usage=False,trust_remote_code=False,use_fast_tokenizer=False,do_train=True,do_eval=False,freeze_language_tower=False,freeze_point_tower=True,train_proj_only=False,dataset='object_train',dataset_dir=str(d),media_dir=str(d),template='spatiallm_cad_llama_baseline',num_bins=1280,do_augmentation=False,random_rotation=False,cutoff_len=cutoff,preprocessing_num_workers=1,dataloader_num_workers=0,output_dir=str(STORE/f.name),overwrite_output_dir=False,logging_steps=1,report_to='none',seed=42,data_seed=42,per_device_train_batch_size=1,gradient_accumulation_steps=1,learning_rate=5e-6,bf16=True,tf32=True,gradient_checkpointing=True,max_steps=640)
  (d/'train.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False)); datasets[f.name]=dict(samples=len(rows),max_target_tokens=max(x['target_tokens'] for x in provenance),config=str(d/'train.yaml'))
dump(E/'reports/BLOCKERS.json',blocked)
dump(E/'reports/DATASETS.json',datasets)
contract=dict(objective='P1 full-sequence object-specialist overfit followed by empty-target greedy natural-EOS free generation and generated V3 CAD assembly',user_authorization='2026-09-25 delegated explicit instruction supersedes previous no-training restriction',warm_start=str(C),warm_start_chain='P1v2 checkpoint-6000 -> PART000 -> Airplane3 -> Airplane9 V2 -> V3 demo5 frozen step160 -> this experiment',representation='q14 + Compact IR V3 unchanged',input='2048 deterministic surface samples from each original X-Part mesh, shared object center/scale, zero normal channels, no curve registry',input_limitations='Presegmented X-Part parts and object frame are supplied. This is training-object memorization, not unseen-object generalization. V3 decoding/compilation depends on per-part semantic template/source program and quantization metadata.',target_prefix_at_inference=0,curve_tokens_used=False,checkpoint_storage=str(STORE),canonical_results_role='LABELS_AND_CONTROLS_ONLY',full20_expected_objects=20,full20_expected_parts=304,available_mesh_parts=254,missing_mesh_parts=50,training_ready_parts=len(allrows),frozen_part_excluded='tank/PART_029',priority_complete_objects=priority,tank_partial_training=True,tank_full_assembly_blocked_parts=[x['part'] for x in blocked if x['object']=='tank' and x['status'].startswith('BLOCKED')],evaluation=dict(free_exact='Exact entire token sequence including natural EOS; equal lengths required',geometry='Measured mesh vs generated CAD, distinct from canonical equality',full_object='All original parts required; frozen PART029 disclosed separately; no dropped failures'),disk_min_data_gb=15,disk_min_checkpoint_gb=30)
dump(E/'reports/EXPERIMENT_CONTRACT.json',contract)
dump(E/'reports/FROZEN_MANIFEST_HASHES.json',{str(p):sha(p) for p in (O/'manifests').glob('*') if p.is_file()})
dump(E/'reports/FROZEN_PART029_HASHES.json',json.loads((O/'objects/tank/cad_parts/PART_029/FROZEN_SOURCE_HASHES.json').read_text()))
(E/'README.md').write_text('# Active objective: real P1 training and free generation\n\nExisting parent objects/ and paper_demo/ outputs are canonical label/data-preparation controls, not new model successes. New outputs live in model_v1/.\n\nSee reports/EXPERIMENT_CONTRACT.json, DATASETS.json and BLOCKERS.json. Full20 is blocked by 50 missing X-Part inputs and invalid labels; Tank has 12 invalid labels. PART_029 is frozen historical reuse only.\n')
dump(O/'reports/ACTIVE_MODEL_OBJECTIVE.json',contract)
print(json.dumps(dict(datasets=datasets,contract=contract),indent=2))
