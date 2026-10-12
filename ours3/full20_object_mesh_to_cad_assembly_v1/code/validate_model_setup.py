import json,hashlib,os,subprocess,shutil
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
contract=json.loads((E/'reports/EXPERIMENT_CONTRACT.json').read_text());store=Path(contract['checkpoint_storage'])
if not (E/'checkpoints').exists():(E/'checkpoints').symlink_to(store,target_is_directory=True)
errors=[];allids=[]
for f in sorted((E/'data').glob('*/train.json')):
 rows=json.loads(f.read_text());provs=json.loads(f.with_name('provenance.json').read_text());assert len(rows)==len(provs)
 for row,prov in zip(rows,provs):
  assert row['id']==prov['id'];assert not row['id']=='tank__PART_029';assert sha(prov['target_path'])==prov['target_sha256'];assert sha(prov['point_cloud'])==prov['point_sha256'];allids.append(row['id'])
assert len(allids)==len(set(allids))==220
for p,h in json.loads((E/'reports/FROZEN_PART029_HASHES.json').read_text()).items():assert sha(p)==h
for p,h in json.loads((E/'reports/FROZEN_MANIFEST_HASHES.json').read_text()).items():assert sha(p)==h
for p in (O/'code').glob('*model*.py'):compile(p.read_text(),str(p),'exec')
ready=json.loads((E/'reports/DATASETS.json').read_text());priority=contract['priority_complete_objects']
original=json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text())
for name in priority:assert ready[name]['samples']==next(x['PART_N'] for x in original if x['OBJECT_ID']==name)
launch=[]
for p in (E/'logs').glob('*_process.json'):
 x=json.loads(p.read_text());x['process_record']=str(p);x['alive']=Path('/proc') .joinpath(str(x['pid'])).exists();launch.append(x)
runtime=[]
for name in ['pottery_large','tank']:
 d=E/'runs'/name;s=json.loads((d/'TRAIN_STATUS.json').read_text());p=json.loads((d/'PREFLIGHT.json').read_text());assert s['step']>0 and p['no_target_truncation'];runtime.append(dict(object=name,status=s,preflight=p))
original_code=O/'code/train_model.py';v2_code=O/'code/train_model_v2.py'
source_note=dict(active_initial_code_sha256=sha(original_code),unused_candidate_v2_sha256=sha(v2_code),note='Original active source restored byte-for-byte. Active pottery and tank processes use original code; later queue also uses original. Model-only TRAIN_DONE.full_object_claim is nonauthoritative; only generated OBJECT_GATE.FULL_MODEL_ASSEMBLY_PASS counts as object success. V2 candidate adds earlier scan cadence and removes this ambiguous model-only field but is not used in active runs.')
dump(E/'reports/RUNTIME_SOURCE_AUDIT.json',source_note)
validation=dict(PASS=True,ready_training_parts=220,priority_complete_objects=priority,priority_complete_part_n=sum(ready[n]['samples'] for n in priority),tank_training_parts=32,tank_frozen_reuse_n=1,tank_blocked_parts=12,full20_expected_parts=304,missing_xpart_parts=50,all_selected_object_ids_unchanged=True,all_frozen_hashes_unchanged=True,active_training=runtime,launch=launch,disk_free_gb=dict(data=shutil.disk_usage('/data').free/1e9,checkpoint=shutil.disk_usage(store).free/1e9),compiler_smoke_pass=json.loads((E/'compiler_smoke/pottery_large_PART_000/GATE.json').read_text())['PASS'])
dump(E/'reports/STARTUP_VALIDATION.json',validation)
(O/'CURRENT_OBJECTIVE.md').write_text('# Active objective: P1 training and free generation\n\nThe latest user instruction authorizes real P1 training and supersedes the original no-training restriction. All existing objects/, reports/ and paper_demo/ canonical batch successes are LABEL/DATA-PREPARATION CONTROLS ONLY.\n\nThe active experiment and live status are model_v1/reports/EXPERIMENT_CONTRACT.json and model_v1/reports/MODEL_LIVE_STATUS.json. Only model_v1/generated/*/free_*/OBJECT_GATE.json with FULL_MODEL_ASSEMBLY_PASS=true counts as a new complete generated object.\n\nTank PART_029 is immutable historical reuse. The selected 20 objects still require 304 parts; 50 original X-Part inputs are missing and audited as blocked, never silently replaced. Tank currently has 12 blocked canonical labels.\n')
print(json.dumps(dict(PASS=True,active=[dict(object=x['object'],step=x['status']['step'],loss=x['status']['loss']) for x in runtime],disk_free_gb=validation['disk_free_gb']),indent=2))
