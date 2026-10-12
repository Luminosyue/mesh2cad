import os,time,json,subprocess
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1';run=E/'runs/tank_repair';log=E/'logs/tank_repair_train.log';ck=Path('/var/tmp/cuiyuehan_full20_p1_v3_20260925/tank/checkpoint-320-free_eval')
while not (E/'runs/tank/TRAIN_DONE.json').exists() and not (E/'runs/tank/TRAIN_FAILED.json').exists():time.sleep(30)
if not ck.exists():
 (E/'reports/TANK_REPAIR_DATASET.json').write_text(json.dumps(dict(status='BLOCKED_WAITING_FOR_TANK_BASE_CHECKPOINT',checkpoint=str(ck)),indent=2));raise SystemExit(0)
if (run/'TRAIN_STATUS.json').exists() or (run/'TRAIN_FAILED.json').exists():raise SystemExit(0)
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='2',FULL20_WORKER='1',DISABLE_VERSION_CHECK='1',HF_DATASETS_CACHE='/var/tmp/cuiyuehan_full20_p1_v3_20260925/hf_cache',TRITON_CACHE_DIR='/var/tmp/cuiyuehan_full20_p1_v3_20260925/triton_cache')
with log.open('a') as out:p=subprocess.Popen(['/data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python','-u',str(O/'code/train_model.py'),'tank_repair'],cwd=R,env=env,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
(E/'logs/tank_repair_train_process.json').write_text(json.dumps(dict(pid=p.pid,gpu='2',checkpoint=str(ck)),indent=2));p.wait()
