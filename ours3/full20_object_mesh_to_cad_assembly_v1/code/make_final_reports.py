import csv, json, subprocess, time, shutil
from pathlib import Path

EXP=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1')
MODEL=EXP/'model_v1'
rows=list(csv.DictReader((EXP/'tables/FULL20_OBJECT_RESULTS.csv').open()))
part_path=EXP/'tables/FULL20_ALL_PART_RESULTS.csv'
part_rows=list(csv.DictReader(part_path.open())) if part_path.exists() else []
by_part={(r['OBJECT_ID'],r['PART_ID']):r for r in part_rows}

def gate(obj):
    vals=[]
    for p in sorted((MODEL/'generated'/obj).glob('*/OBJECT_GATE.json')):
        try: vals.append(json.loads(p.read_text()))
        except Exception: pass
    return max(vals,key=lambda x: bool(x.get('FULL_MODEL_ASSEMBLY_PASS',False))) if vals else {}

def active_workers():
    out=subprocess.run(['ps','-eo','pid,args'],capture_output=True,text=True,check=False).stdout.splitlines()
    result=[]
    for line in out:
        if not any(k in line for k in ('train_part_completion.py','train_model.py tank','train_model_v2_snapshot.py')): continue
        p=line.strip().split(None,1)
        if len(p)<2: continue
        gpu=''
        try:
            env=(Path('/proc')/p[0]/'environ').read_bytes().split(b'\0')
            gpu=next((x.decode().split('=',1)[1] for x in env if x.startswith(b'CUDA_VISIBLE_DEVICES=')),'')
        except Exception: pass
        result.append({'pid':p[0],'gpu':gpu,'command':p[1]})
    return result

active=active_workers(); blockers=[]
for objrow in rows:
    obj=objrow['OBJECT_ID']
    if objrow['STATUS']=='DONE': continue
    missing=set((gate(obj).get('missing_parts') or []))
    for pid in sorted(missing):
        pr=by_part.get((obj,pid),{})
        reason=' '.join([pr.get('FAILURE_REASON',''),pr.get('STATUS',''),pr.get('CAD_SOURCE','')]).upper()
        if 'MISSING_XPART' in reason or 'UNAVAILABLE' in reason:
            cls='K. MISSING_INPUT'; recover='PERMANENT_UNLESS_VERIFIED_SOURCE_FOUND'; cost='HIGH'
        elif 'Q14_BREP' in reason or 'BREP_INVALID' in reason:
            cls='G. CAD_BREP_BLOCKER'; recover='BOUNDED_REPAIR_MAX_3'; cost='MEDIUM'
        elif objrow['FREE_PASS_N']=='0' or pr.get('FREE_STATUS','').upper() in ('FAIL','BLOCKED'):
            cls='B. FREE_GENERATION_BLOCKER'; recover='TARGETED_REFINEMENT_MAX_3'; cost='MEDIUM'
        else:
            cls='L. UNKNOWN'; recover='AUDIT_REQUIRED'; cost='UNKNOWN'
        worker=';'.join(w['pid']+':GPU'+(w['gpu'] or '?') for w in active if obj in w['command'] and pid in w['command'])
        blockers.append(dict(OBJECT_ID=obj,PART_ID=pid,CURRENT_STAGE='PARTIAL_OR_ASSEMBLY',FAILURE_CLASS=cls,TF_ERROR_N='',FREE_STATUS=pr.get('FREE_STATUS',''),Q14_STATUS=pr.get('Q14_PASS',''),V3_STATUS=pr.get('V3_PASS',''),CAD_STATUS=pr.get('CAD_EXEC_PASS',''),STEP_STATUS=pr.get('STEP_READBACK_PASS',''),TRANSFORM_STATUS=pr.get('TRANSFORM_PASS',''),GEOMETRY_STATUS=pr.get('PART_GEOMETRY_PASS',''),RECOVERABLE=recover,ESTIMATED_COST=cost,CURRENT_WORKER=worker,ACTION='Preserve current artifacts; targeted repair or completion only'))

fields=['OBJECT_ID','PART_ID','CURRENT_STAGE','FAILURE_CLASS','TF_ERROR_N','FREE_STATUS','Q14_STATUS','V3_STATUS','CAD_STATUS','STEP_STATUS','TRANSFORM_STATUS','GEOMETRY_STATUS','RECOVERABLE','ESTIMATED_COST','CURRENT_WORKER','ACTION']
out=EXP/'tables/FINAL_REMAINING_PART_BLOCKERS.csv'; out.parent.mkdir(parents=True,exist_ok=True)
with out.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(blockers)

counts={}
for r in rows: counts[r['STATUS']]=counts.get(r['STATUS'],0)+1
done=[r['OBJECT_ID'] for r in rows if r['STATUS']=='DONE']
partial=[r for r in rows if r['STATUS']=='PARTIAL_FREE_GENERATED']
disk=round(shutil.disk_usage('/data').free/1e9,1)
gpu=subprocess.run(['nvidia-smi','--query-gpu=index,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,check=False).stdout.strip()
lines=['# FULL20 FINAL COMPLETION STATUS','',f'Updated: {time.strftime("%F %T %z")}','',f"FULL_MODEL_ASSEMBLY_PASS = {counts.get('DONE',0)}/20",f"CURRENT_PARTIAL_N = {counts.get('PARTIAL_FREE_GENERATED',0)}",f"CURRENT_BLOCKED_N = {counts.get('BLOCKED',0)}",f"CURRENT_TRAINING_N = {len(active)}",'', 'DONE:', *[f'- {x}' for x in done], '', 'PARTIAL:']
for r in partial: lines.append(f"- {r['OBJECT_ID']} | {r['FREE_PASS_N']}/{r['PART_N']} free | {r['CAD_STEP_PASS_N']}/{r['PART_N']} CAD/STEP | remaining {int(r['PART_N'])-int(r['CAD_STEP_PASS_N'])}")
lines += ['', 'ACTIVE WORKERS:', *([f"- PID {w['pid']} GPU {w['gpu'] or '?'} | {w['command']}" for w in active] or ['- none']), '', 'BLOCKER CLASS COUNTS:']
classes={}
for b in blockers: classes[b['FAILURE_CLASS']]=classes.get(b['FAILURE_CLASS'],0)+1
lines += [f'- {k}: {v}' for k,v in sorted(classes.items())] or ['- none']
lines += ['',f'DISK_FREE_GB = {disk}','', 'GPU SNAPSHOT:', '```', gpu, '```','', 'Representation: q14 + Compact IR V3; canonical controls are not model success; texture reconstruction is out of scope.']
(EXP/'reports/FULL20_FINAL_COMPLETION_STATUS.md').write_text('\n'.join(lines)+'\n')
(EXP/'reports/FULL20_FINAL_COMPLETION_REPORT.md').write_text('\n'.join(lines)+'\n\nRemaining blocker detail is in tables/FINAL_REMAINING_PART_BLOCKERS.csv.\n')
print('FINAL_REPORTS',counts,'blockers',len(blockers),'active',len(active))
