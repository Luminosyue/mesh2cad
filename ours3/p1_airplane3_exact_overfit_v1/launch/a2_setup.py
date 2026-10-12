from pathlib import Path
import json,shutil,subprocess,hashlib,ast,tempfile,yaml,statistics,os
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');OLD=ROOT/'ours3/p1_quick_overfit_airplane9_v1';DBG=ROOT/'ours3/p1_airplane9_overfit_debug_v1';EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'
assert json.loads((DBG/'single_checks/checkpoint-500/single_case_decode_diagnosis.json').read_text())['SINGLE_PART_EXACT_OVERFIT']=='PASS'
EXP.mkdir(exist_ok=False)
for d in ['data','configs','launch','logs','audits','gt_preflight','evaluations','cache','control']:(EXP/d).mkdir()
storage=Path(tempfile.mkdtemp(prefix='cuiyuehan_p1_airplane3_ckpts_',dir='/var/tmp'));(EXP/'runs').symlink_to(storage,target_is_directory=True)
parts=json.loads((OLD/'data/parts.json').read_text());raw=json.loads((OLD/'data/train.json').read_text());selection=[];chosen=[]
for tag,name,reason in [('A','PART_000','Previously passed single-part checkpoint-500; 6 blocks'),('B','PART_001','13 blocks and 12920 inventory tokens equal the 9-part medians; deterministic ID tie-break'),('C','PART_005','Longest program among the original airplane parts: 25 blocks, 25109 inventory tokens; must pass unmodified GT execution')]:
 row=next(r for r in parts if r['part']==name);target=Path(row['folder']);out=EXP/'gt_preflight'/name;out.mkdir()
 shutil.copy2(target/'target_chunked.py',out/'prediction.py');ast.parse((out/'prediction.py').read_text())
 p=subprocess.run(['/usr/bin/python3',str(OLD/'launch/cq54_evaluate.py'),str(out),str(target)],capture_output=True,text=True,timeout=240)
 (out/'execution.log').write_text(p.stdout+p.stderr)
 rec={'ROLE':tag,'PART_ID':name,'BLOCK_COUNT':row['blocks'],'TOKEN_COUNT':row['full_target_tokens'],'TOKEN_COUNT_DEFINITION':'inventory whole-program token count; supervised per-block token count including EOS will be audited separately','GT_PARSE_PASS':True,'GT_EXECUTION_PASS':p.returncode==0,'GT_STEP_PASS':(out/'prediction.step').exists(),'SELECTION_REASON':reason,'folder':str(target),'gt_sha256':hashlib.sha256((target/'target_chunked.py').read_bytes()).hexdigest()}
 selection.append(rec);(EXP/'selected_3parts.json').write_text(json.dumps(selection,indent=2))
 assert rec['GT_EXECUTION_PASS'] and rec['GT_STEP_PASS'],rec
 chosen.append(row);print('GT_PREFLIGHT',name,'PASS',flush=True)
train=[r for r in raw if r['sample_id'] in {'airplane__'+p['part'] for p in chosen}];assert len(train)==44
for name,data in [('parts.json',chosen),('train.json',train),('eval_memorization.json',train)]: (EXP/'data'/name).write_text(json.dumps(data,indent=2))
shutil.copy2(OLD/'data/dataset_info.json',EXP/'data/dataset_info.json')
registry=[json.loads(line) for line in (OLD/'data/curve_registry.jsonl').read_text().splitlines() if line.strip()];allowed={r['id'] for r in chosen}
(EXP/'data/curve_registry.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in registry if r['cad_id'] in allowed))
for name in ['cq54_protocol.py','cq54_evaluate.py']:shutil.copy2(OLD/'launch'/name,EXP/'launch'/name)
cfg=yaml.safe_load((OLD/'configs/train.yaml').read_text());cfg.update(dataset_dir=str(EXP/'data'),output_dir=str(EXP/'runs/quick'),logging_dir=str(EXP/'logs'),max_steps=3000,eval_steps=250,save_strategy='no',save_total_limit=None,overwrite_output_dir=False)
(EXP/'configs/train.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
original=[OLD,ROOT/'ours3/p1_single_airplane_part_overfit_v1']
inventory=[]
for root in original:
 for f in root.rglob('*'):
  if f.is_file():inventory.append({'path':str(f),'size':f.stat().st_size,'mtime_ns':f.stat().st_mtime_ns})
pipelines=[ROOT/'SpatialLM/spatiallm/tuner/data/collator.py',ROOT/'SpatialLM/spatiallm/tuner/data/template.py',ROOT/'SpatialLM/spatiallm/tuner/data/mm_plugin.py',ROOT/'SpatialLM/spatiallm/model/spatiallm_llama.py',ROOT/'scripts/spatiallm_curve_token_v1/curve_token_injector.py',OLD/'launch/cq54_evaluate.py',OLD/'launch/cq54_protocol.py']
for p in chosen:
 for name in ['target.py','target_chunked.py','target_blocks.json','surface_points.npy','curve_tokens.npy','target.step']:pipelines.append(Path(p['folder'])/name)
frozen=[{'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in pipelines]
(EXP/'audits/frozen_inputs.json').write_text(json.dumps({'original_experiment_files':inventory,'pipeline_and_gt':frozen},indent=2))
metadata={'parts':3,'blocks':44,'seed':42,'initial_checkpoint':cfg['model_name_or_path'],'single_pass_checkpoint_not_used_for_initialization':True,'schedule':[250,500,750,1000,1500,2000,2500,3000],'sampling':'unchanged framework block-level shuffled sampling; not part-balanced','expected_part_probabilities':{'PART_000':6/44,'PART_001':13/44,'PART_005':25/44},'storage':str(storage),'data_unchanged':all(r in raw for r in train)}
(EXP/'audits/setup.json').write_text(json.dumps(metadata,indent=2));print(json.dumps(metadata),flush=True)
