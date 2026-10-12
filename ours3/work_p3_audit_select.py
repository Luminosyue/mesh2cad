import os, json, csv, hashlib, re, math, statistics
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
INP=ROOT/'p3_xpart_open_cases'
OUT=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'
OUT.mkdir(parents=True, exist_ok=True)
for d in ['case_manifest','raw_cad','quantization','semantic_ast','compact_ir','compiled_cadquery','step','token_audit','context_audit','training','eval','renders','reports','logs']:
    (OUT/d).mkdir(parents=True, exist_ok=True)

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def mesh_stats(p, objdir=None, pid=None):
    out={'watertight':False,'vertex_n':0,'face_n':0,'bbox_min':[],'bbox_max':[],'volume':None,'mesh_error':''}
    # X-Part manifests already contain exact topology and watertightness from the
    # validated reconstruction; use them to avoid rereading multi-gigabyte OBJ files.
    if objdir is not None:
        mf=objdir/'xpart_manifest.json'
        if mf.exists():
            try:
                md=json.loads(mf.read_text())
                for x in md.get('parts',[]):
                    if str(x.get('part_id','')).lower()==str(pid).lower():
                        out.update(watertight=bool(x.get('watertight',False)),vertex_n=int(x.get('vertices',0)),face_n=int(x.get('triangles',0)),bbox_min=x.get('bbox_min',[]),bbox_max=x.get('bbox_max',[]),volume=x.get('volume'))
                        return out
            except Exception: pass
    # If no validated manifest is present, retain an explicit unknown entry.
    # Full OBJ parsing is intentionally avoided here because the source tree is
    # multi-gigabyte; selected candidates are validated later by CAD/STEP gates.
    return out
    try:
        import trimesh
        m=trimesh.load_mesh(p, process=False)
        if hasattr(m,'geometry') and not hasattr(m,'vertices'):
            vals=list(m.geometry.values()); m=trimesh.util.concatenate(vals) if vals else None
        if m is None: raise RuntimeError('empty mesh')
        out.update(watertight=bool(getattr(m,'is_watertight',False)), vertex_n=int(len(m.vertices)), face_n=int(len(m.faces)))
        bb=m.bounds; out['bbox_min']=[float(x) for x in bb[0]]; out['bbox_max']=[float(x) for x in bb[1]]
        try: out['volume']=float(abs(m.volume))
        except Exception: pass
    except Exception as e:
        out['mesh_error']=repr(e)
    return out

rows=[]
for objdir in sorted([p for p in INP.iterdir() if p.is_dir()]):
    pm=objdir/'p3_parts/part_metadata.json'
    try: meta=json.loads(pm.read_text()) if pm.exists() else {}
    except Exception: meta={}
    for mesh in sorted((objdir/'p3_parts').glob('part_*.obj')):
        pid=mesh.stem
        upid=pid.replace('part_','PART_')
        cdir=objdir/'xpart_parts_cadquery_features'/upid
        xmesh=objdir/'xpart_parts'/upid/f'complete_{pid}.obj'
        st=mesh_stats(xmesh if xmesh.exists() else mesh, objdir, upid)
        rep={}
        for nm in ['rebuild_validation.json','report.json','job_status.json']:
            q=cdir/nm
            if q.exists():
                try: rep[nm]=json.loads(q.read_text())
                except Exception: pass
        cad=cdir/f'{upid}.py'; step=cdir/f'{upid}.step'
        row={'OBJECT_ID':objdir.name,'PART_ID':pid,'MESH_PATH':str(xmesh if xmesh.exists() else mesh),
             'SOURCE_PART_PATH':str(mesh),'XPART_MESH_EXISTS':xmesh.exists(),'WATERTIGHT':st['watertight'],
             'VERTEX_N':st['vertex_n'],'FACE_N':st['face_n'],'BBOX_MIN':json.dumps(st['bbox_min']),
             'BBOX_MAX':json.dumps(st['bbox_max']),'VOLUME':st['volume'] if st['volume'] is not None else '',
             'HAS_EXISTING_CAD':cad.exists(),'HAS_EXISTING_STEP':step.exists(),'HAS_EXISTING_CADQUERY':cad.exists(),
             'CAD_PATH':str(cad),'STEP_PATH':str(step),'REPORT_JSON':json.dumps(rep,ensure_ascii=False), 'NOTES':st['mesh_error']}
        rows.append(row)

fields=list(rows[0]) if rows else []
with open(OUT/'reports/P3_XPART_OPEN_CASES_AUDIT.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

# Candidate score: validated existing program and STEP, watertight mesh, then geometric complexity.
def score(r):
    s=0
    s += 1000*int(r['WATERTIGHT']) + 500*int(r['HAS_EXISTING_CAD']) + 300*int(r['HAS_EXISTING_STEP'])
    s += min(int(r['FACE_N'])/10,500)
    if r['OBJECT_ID'].lower()=='airplane': s-=100000
    if r['PART_ID'] in {'part_000','part_001','part_005'} and r['OBJECT_ID'].lower()=='airplane': s-=100000
    return s
valid=[r for r in rows if r['WATERTIGHT'] and r['HAS_EXISTING_CAD'] and r['HAS_EXISTING_STEP']]
# Exclude known airplane and any object/part explicitly tagged as old Airplane training.
valid=[r for r in valid if r['OBJECT_ID'].lower()!='airplane']
byobj={}
for r in valid: byobj.setdefault(r['OBJECT_ID'],[]).append(r)
for k in byobj: byobj[k].sort(key=score, reverse=True)
# Pick one from each of 20 different objects, preferring a spread of mesh complexity.
objs=sorted(byobj, key=lambda k:max(score(x) for x in byobj[k]), reverse=True)
chosen=[]
if len(objs)>=20:
    # rank objects by complexity, then sample across quantiles
    ranked=sorted(objs,key=lambda k:int(byobj[k][0]['FACE_N']))
    idxs=sorted(set(round(i*(len(ranked)-1)/19) for i in range(20)))
    chosen=[byobj[ranked[i]][0] for i in idxs]
else:
    for o in objs: chosen.append(byobj[o][0])
    # Fill remaining with next best distinct parts only when necessary.
    for r in sorted(valid,key=score,reverse=True):
        if len(chosen)>=20: break
        if r not in chosen: chosen.append(r)

manifest=[]
for i,r in enumerate(chosen[:20]):
    case=f'case_{i:03d}'
    src=Path(r['MESH_PATH']); cad=Path(r['CAD_PATH']); step=Path(r['STEP_PATH'])
    manifest.append({'CASE_ID':case,'OBJECT_ID':r['OBJECT_ID'],'PART_ID':r['PART_ID'],'MESH_PATH':r['MESH_PATH'],
      'MESH_SHA256':sha256(src) if src.exists() else '','WATERTIGHT':bool(r['WATERTIGHT']),'SOURCE':'existing_validated_xpart_cadquery',
      'CAD_PATH':str(cad),'STEP_PATH':str(step),'FACE_N':int(r['FACE_N']),'VERTEX_N':int(r['VERTEX_N']),
      'VOLUME':r['VOLUME'],'SELECTION_SCORE':score(r)})
    (OUT/'case_manifest'/case).mkdir(exist_ok=True)
    (OUT/'case_manifest'/case/'source.json').write_text(json.dumps(manifest[-1],indent=2))
(OUT/'CASE_MANIFEST.json').write_text(json.dumps({'experiment':'P3_XPART_20CASE_COMPACT_IR_FULLSEQ_OVERFIT_V1','requested_case_n':20,'selected_case_n':len(manifest),'cases':manifest},indent=2))
(OUT/'reports/P3_XPART_OPEN_CASES_AUDIT.json').write_text(json.dumps({'total_parts':len(rows),'valid_candidates':len(valid),'objects':len(byobj),'selected':len(manifest)},indent=2))
print(json.dumps({'total_parts':len(rows),'valid_candidates':len(valid),'objects':len(byobj),'selected':len(manifest),'manifest':manifest},indent=2))
