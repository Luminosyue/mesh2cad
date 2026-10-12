from pathlib import Path
import json,os,collections,concurrent.futures,hashlib
import numpy as np
import trimesh
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
SRC=ROOT/'partsam/PartObjaverse-Tiny_instance_stl'
OUT=ROOT/'partsam/PartObjaverse-Tiny_instance_cad'
OLD=ROOT/'partsam_cad_iou_top1000_v1/candidates'
def check(p):
    m=trimesh.load(p,force='mesh',process=True)
    row={'relative':str(p.relative_to(SRC)),'faces':len(m.faces),'vertices':len(m.vertices),'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),'is_volume':bool(m.is_volume),'volume':float(m.volume),'bounds':m.bounds.tolist(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    old=OLD/(p.parent.name+'_'+p.stem)
    row['existing_code']=(old/'cad.py').is_file()
    if (old/'metrics.json').exists():
        d=json.loads((old/'metrics.json').read_text()); row['previous_iou']=d.get('iou128');row['previous_quality']=d.get('quality_level')
    return row
if __name__=='__main__':
    OUT.mkdir(exist_ok=True)
    files=sorted(SRC.rglob('*.stl'))
    with concurrent.futures.ProcessPoolExecutor(max_workers=8) as pool: rows=list(pool.map(check,files,chunksize=12))
    (OUT/'input_inventory.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps({'files':len(rows),'watertight':sum(r['watertight'] for r in rows),'winding':sum(r['winding'] for r in rows),'positive_solid':sum(r['is_volume'] for r in rows),'total_faces':sum(r['faces'] for r in rows),'existing_code':sum(r['existing_code'] for r in rows),'previous_quality':dict(collections.Counter(r.get('previous_quality') for r in rows))},indent=2))
    for p in files[:3]:
        old=OLD/(p.parent.name+'_'+p.stem)/'source.obj'
        if old.exists():
            a=trimesh.load(p,force='mesh',process=True);b=trimesh.load(old,force='mesh',process=True)
            print('source comparison',p.parent.name,p.name,'faces',len(a.faces),len(b.faces),'bounds delta',np.max(np.abs(a.bounds-b.bounds)))
    print('CPU',os.getloadavg(),'MEM',Path('/proc/meminfo').read_text().splitlines()[:3])
