from pathlib import Path
import json,time,shutil
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1')
s=json.loads((E/'status.json').read_text());assert s['phase']=='STOPPED_WITH_EVIDENCE' and s['errors']==[{'training_exit_code':1}]
assert not (E/'audits/training_steps.jsonl').exists(),'No optimizer updates must have occurred'
origin=(E/'logs/orchestrate.log').stat().st_mtime-s['elapsed_seconds']
(E/'control/run_clock.json').write_text(json.dumps({'start':origin,'reason':'preserve original evaluation wall budget across pre-update sampler setup correction'}))
for f in ['logs/train.log','logs/orchestrate.log','status.json']:shutil.copy2(E/f,E/'audits'/('sampler_setup_failed_'+Path(f).name))
(E/'audits/sampler_setup_correction.json').write_text(json.dumps({'optimizer_steps_before_failure':0,'cause':'dataset stores conversations; labels are produced lazily by collator','fix':'identify rows using actual collated label hashes, verified against frozen 44-block inventory','old_evaluations_reused':True},indent=2))
lease=(E/'launch/fast_gpu_lease.py').read_text().replace('PIDS={5:4041088}','PIDS={5:1070231}').replace('gpu_reservations_snapshot.json','gpu_reservations_snapshot_2.json').replace('gpu_lease_released.json','gpu_lease_released_2.json').replace('gpu_lease_restored.json','gpu_lease_restored_2.json')
(E/'launch/fast_gpu_lease.py').write_text(lease)
