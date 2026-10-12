"""Scoped automatic continuation; preserves existing jobs and frozen object identities."""
import os, sys, json, time, subprocess, shutil, hashlib, fcntl, traceback
from pathlib import Path

R = Path('/data/home/cuiyuehan/project/mesh2cad')
O = R/'ours3/full20_object_mesh_to_cad_assembly_v1'
E = O/'model_v1'
S = E/'autoqueue_side_20260925'
STORE = Path('/var/tmp/cuiyuehan_full20_p1_v3_20260925')
PY = '/data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python'
TRAIN = S/'train_model_v2_snapshot.py'
ORDER = ['dvd_player', 'speaker_big', 'robot', 'pressure_cooker', 'airplane',
         '2_of_jenga_classic_game', 'toaster', 'birdhouse', 'mini_fire_engine',
         'assorted_vegetable_set', '3d_dollhouse_sofa', 'winerack']
# GPU 2 remains owned by the existing Tank -> repair launcher; GPU 7 is excluded.
GPUS = [4, 5, 1, 3, 6, 0]

def read(p, default=None):
    try: return json.loads(Path(p).read_text())
    except (FileNotFoundError, json.JSONDecodeError): return default

def dump(p, obj):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    q = p.with_name(p.name + '.tmp'); q.write_text(json.dumps(obj, indent=2)+'\n'); q.replace(p)

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def processes():
    result = []
    for p in Path('/proc').iterdir():
        if not p.name.isdigit(): continue
        try:
            args = [x.decode() for x in (p/'cmdline').read_bytes().split(b'\0') if x]
            if not args: continue
            env = dict(x.split(b'=', 1) for x in (p/'environ').read_bytes().split(b'\0') if b'=' in x)
            result.append(dict(pid=int(p.name), args=args,
                               gpu=env.get(b'CUDA_VISIBLE_DEVICES', b'').decode(),
                               own=p.stat().st_uid == os.getuid()))
        except (OSError, ValueError, UnicodeError): pass
    return result

def gpu_info():
    raw = subprocess.check_output(['nvidia-smi', '--query-gpu=index,memory.used,memory.free,utilization.gpu',
                                   '--format=csv,noheader,nounits'], text=True, timeout=20)
    return {int(a): dict(used=int(b), free=int(c), utilization=int(d))
            for a,b,c,d in (line.split(',') for line in raw.strip().splitlines())}

def existing(name, procs):
    return any(name in p['args'] and any('train_model' in a or 'launch_model.py' in a for a in p['args'])
               for p in procs)

def touched(name):
    run = E/'runs'/name
    return (any(run.glob('TRAIN_*.json')) or (run/'PREFLIGHT.json').exists()
            or (run/'events.jsonl').exists() or any((STORE/name).glob('checkpoint-*')))

def inventory():
    manifest = {x['OBJECT_ID']: x for x in read(O/'manifests/FULL20_OBJECT_MANIFEST.json')}
    blockers = read(E/'reports/BLOCKERS.json')
    rows = []
    for name in ORDER:
        d = E/'data'/name; prov = read(d/'provenance.json', [])
        expected = manifest[name]['PART_N']
        rows.append(dict(object=name, ready_parts=len(prov), expected_parts=expected,
                         excluded_parts=expected-len(prov), full_object_claim=False,
                         blockers=[b for b in blockers if b['object']==name],
                         dataset_sha256=sha(d/'train.json'), config_sha256=sha(d/'train.yaml'),
                         provenance_sha256=sha(d/'provenance.json')))
    return rows

def validate(row):
    name=row['object']; d=E/'data'/name
    for file,key in [('train.json','dataset_sha256'),('train.yaml','config_sha256'),('provenance.json','provenance_sha256')]:
        assert sha(d/file)==row[key], 'DATASET_CHANGED_REQUIRES_REVIEW: '+name
    prov=read(d/'provenance.json'); raw=read(d/'train.json')
    assert len(raw)==len(prov)>0
    assert len({p['part'] for p in prov})==len(prov)
    for p in prov:
        assert p['object']==name and not p['curve_tokens_used']
        assert sha(p['target_path'])==p['target_sha256']
        assert sha(p['point_cloud'])==p['point_sha256']
        assert sha(p['input_mesh'])==p['input_mesh_sha256']
    return True

def main():
    if '--plan' in sys.argv:
        rows=inventory()
        for r in rows: validate(r)
        print(json.dumps(rows,indent=2)); return
    S.mkdir(exist_ok=True)
    lock=(S/'scheduler.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
    manifest=read(S/'MANIFEST.json')
    if manifest is None:
        assert not TRAIN.exists()
        shutil.copy2(O/'code/train_model_v2.py', TRAIN)
        rows=inventory()
        for row in rows: validate(row)
        manifest=dict(authorization='用户：跑完这几个case卡空出来继续跑剩下的', created=time.time(),
                      objects=rows, gpus=GPUS, reserved_gpu2='Existing Tank and Tank repair launcher',
                      excluded_gpu7=True, training_script=str(TRAIN), training_sha256=sha(TRAIN),
                      no_automatic_retries=True, no_deletion=True, representation='q14 + Compact IR V3',
                      evaluation='Empty target greedy free generation; complete object requires all original parts and CAD gate',
                      missing_xpart_count=50)
        dump(S/'MANIFEST.json',manifest)
    assert sha(TRAIN)==manifest['training_sha256']
    states=read(S/'STATE.json',{}).get('objects',{})
    children={}; quiet={g:0 for g in GPUS}; gate=None
    def event(**kw):
        record=dict(time=time.time(), **kw)
        with (S/'events.jsonl').open('a') as f: f.write(json.dumps(record)+'\n')
        print(json.dumps(record),flush=True)
    event(event='scheduler_started',pid=os.getpid())
    dump(S/'PROCESS.json',dict(pid=os.getpid(),script=__file__,started=time.time()))
    while True:
        try:
            procs=processes(); gpus=gpu_info()
            for name,p in list(children.items()):
                rc=p.poll()
                if rc is not None:
                    states[name].update(exit_code=rc, exited=time.time())
                    event(event='training_process_exited',object=name,exit_code=rc)
                    del children[name]
            for row in manifest['objects']:
                name=row['object']; run=E/'runs'/name; st=states.setdefault(name,{})
                done=read(run/'TRAIN_DONE.json'); fail=read(run/'TRAIN_FAILED.json')
                if existing(name,procs): st['status']='RUNNING_TRAINING_OR_GENERATION'
                elif fail: st.update(status='FAILED',failure=fail)
                elif done: st.update(status='TRAINING_DONE_CAD_GATE_SEPARATE',done=done)
                elif touched(name) or (S/'claims'/f'{name}.json').exists():
                    st['status']='BLOCKED_EXISTING_ATTEMPT_NO_AUTO_RESTART'
                else: st['status']='QUEUED'
            for gpu in GPUS:
                if str(gpu) in read(S/'GPU_RESERVATIONS.json', {}):
                    quiet[gpu]=0
                    continue
                occupied=any(p['own'] and str(gpu) in p['gpu'].split(',') for p in procs)
                info=gpus[gpu]
                idle=not occupied and info['used']<7000 and info['free']>=36000 and info['utilization']<=5
                quiet[gpu]=quiet[gpu]+1 if idle else 0
            pending=[r for r in manifest['objects'] if states[r['object']]['status']=='QUEUED']
            data_free=shutil.disk_usage('/data').free
            root_free=shutil.disk_usage(STORE).free
            active=sum(any('train_model' in a for a in p['args']) for p in procs)
            # Reserve room for in-flight checkpoints; each training script also gates every save.
            disk_ok=data_free>15e9 and root_free>30e9+25e9*(active+1)
            for gpu in GPUS:
                if not pending or not disk_ok: break
                if quiet[gpu]<2: continue
                row=pending.pop(0);name=row['object']
                validate(row)
                latest=processes()
                if existing(name,latest) or touched(name):continue
                if any(p['own'] and str(gpu) in p['gpu'].split(',') for p in latest):continue
                fresh=gpu_info()[gpu]
                if fresh['used']>=7000 or fresh['free']<36000 or fresh['utilization']>5:continue
                claim=S/'claims'/f'{name}.json';claim.parent.mkdir(exist_ok=True)
                try:
                    with claim.open('x') as f:json.dump(dict(object=name,gpu=gpu,claimed=time.time(),scheduler=os.getpid()),f)
                except FileExistsError:continue
                env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),OMP_NUM_THREADS='4',
                    OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4',TOKENIZERS_PARALLELISM='false',
                    DISABLE_VERSION_CHECK='1',HF_DATASETS_CACHE=str(STORE/'hf_cache'),TRITON_CACHE_DIR=str(STORE/'triton_cache'))
                log=E/'logs'/f'{name}_train.log'
                with log.open('a') as f:
                    p=subprocess.Popen([PY,'-u',str(TRAIN),name],cwd=R,env=env,
                        stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
                st=dict(status='RUNNING_TRAINING_OR_GENERATION',pid=p.pid,gpu=gpu,started=time.time(),
                        ready_parts=row['ready_parts'],expected_parts=row['expected_parts'],full_object_claim=False)
                states[name]=st;children[name]=p;quiet[gpu]=0
                dump(E/'logs'/f'{name}_process.json',dict(st,object=name,launcher=str(Path(__file__))))
                dump(S/'claims'/f'{name}.json',dict(st,object=name))
                event(event='case_launched',object=name,**st)
                active+=1;disk_ok=root_free>30e9+25e9*(active+1)
            # Existing watcher owns the original priority cases. This worker owns
            # only new queued objects and the previously omitted milk-frother gate.
            if gate and gate[0].poll() is not None:
                p,key=gate;dump(S/'cad_attempts'/key,dict(exit_code=p.returncode,finished=time.time()))
                event(event='cad_attempt_exited',attempt=key,exit_code=p.returncode);gate=None
            if gate is None and data_free>15e9:
                gate_names=ORDER+['aroma_stainless_steel_milk_frother_2_cup']
                for name in gate_names:
                    for summary in sorted((E/'runs'/name).glob('free_*/SUMMARY.json')):
                        folder=summary.parent;key=name+'_'+folder.name+'.json'
                        if (E/'generated'/name/folder.name/'OBJECT_GATE.json').exists() or (S/'cad_attempts'/key).exists():continue
                        if any(str(folder) in p['args'] for p in processes()):continue
                        dump(S/'cad_attempts'/key,dict(started=time.time(),status='STARTING'))
                        with (E/'logs'/f'{name}_{folder.name}_side_cad.log').open('a') as f:
                            p=subprocess.Popen(['timeout','--signal=TERM','--kill-after=30','18000',
                                'xvfb-run','-a','/usr/bin/python3',str(O/'code/generated_gate.py'),'attempt',str(folder)],
                                cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
                        dump(S/'cad_attempts'/key,dict(pid=p.pid,started=time.time(),status='RUNNING'))
                        gate=(p,key);event(event='cad_attempt_launched',object=name,pid=p.pid);break
                    if gate:break
            dump(S/'STATE.json',dict(time=time.time(),pid=os.getpid(),objects=states,gpus=gpus,
                data_free_gb=data_free/1e9,checkpoint_free_gb=root_free/1e9,disk_allows_next_launch=disk_ok,
                full_object_claim=False,notice='Partial ready subsets retain frozen full-object missing-part blockers'))
        except Exception:
            event(event='scheduler_error',traceback=traceback.format_exc())
        time.sleep(20)

if __name__=='__main__':main()
