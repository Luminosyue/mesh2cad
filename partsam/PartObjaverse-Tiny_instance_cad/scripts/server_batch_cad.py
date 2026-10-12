from pathlib import Path
import os,sys,json,base64,zlib,io,time,hashlib,subprocess,concurrent.futures,csv,argparse
import numpy as np
import trimesh
SRC=Path('/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl')
OUT=SRC.with_name('PartObjaverse-Tiny_instance_cad')
HERE=Path(__file__).resolve().parent
TEMPLATE=(HERE/'mesh_cad_runtime_template.py').read_text()

def prepare(p):
    m=trimesh.load(p,force='mesh',process=False)
    v,inverse=np.unique(np.asarray(m.vertices,dtype=np.float64),axis=0,return_inverse=True)
    f=inverse[np.asarray(m.faces)].astype(np.int32)
    merged=trimesh.Trimesh(v,f,process=False)
    info={'source_path':str(p),'relative_path':str(p.relative_to(SRC)),
          'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
          'input_faces':len(f),'input_vertices':len(v),
          'input_watertight':bool(merged.is_watertight),
          'input_winding_consistent':bool(merged.is_winding_consistent),
          'input_bounds':merged.bounds.tolist()}
    buffer=io.BytesIO();np.savez(buffer,vertices=v,faces=f)
    encoded=base64.b85encode(zlib.compress(buffer.getvalue(),6)).decode('ascii')
    code=TEMPLATE.replace('__PART_NAME__',p.stem).replace('__SOURCE_INFO__',repr(info)).replace('__GEOMETRY_BASE85__',encoded)
    folder=OUT/p.relative_to(SRC).parent;folder.mkdir(parents=True,exist_ok=True)
    path=folder/(p.stem+'_cad.py');path.write_text(code,encoding='utf-8')
    return path,info

def one(p):
    relative=str(p.relative_to(SRC));folder=OUT/p.relative_to(SRC).parent
    reportfile=folder/(p.stem+'_report.json')
    if reportfile.exists():
        old=json.loads(reportfile.read_text())
        if old.get('status')=='SUCCESS' and all((folder/(p.stem+s)).is_file() for s in ['.step','.brep','_cad.py']):return old
    started=time.time()
    try:
        code,info=prepare(p)
        log=folder/(p.stem+'_conversion.log')
        env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
        with log.open('w') as stream:
            completed=subprocess.run([sys.executable,str(code)],stdout=stream,stderr=subprocess.STDOUT,env=env,timeout=1200)
        if completed.returncode: raise RuntimeError(f'CAD process exit {completed.returncode}: '+log.read_text()[-1200:])
        return json.loads(reportfile.read_text())
    except Exception as e:
        result={'status':'FAILED','relative_path':relative,'error':str(e),'seconds':time.time()-started}
        folder.mkdir(parents=True,exist_ok=True);reportfile.write_text(json.dumps(result,indent=2))
        return result

def summarize(rows,total,started,complete=False):
    from collections import Counter
    counts=Counter(r['status'] for r in rows);kinds=Counter(r.get('representation','failed') for r in rows)
    summary={'total':total,'processed':len(rows),'status_counts':dict(counts),'representation_counts':dict(kinds),
             'elapsed_seconds':round(time.time()-started,1),'complete':complete,'output_root':str(OUT)}
    tmp=OUT/'progress.tmp.json';tmp.write_text(json.dumps(summary,indent=2));tmp.replace(OUT/'progress.json')
    print(json.dumps(summary),flush=True)
    return summary

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=16);parser.add_argument('--pilot',action='store_true');args=parser.parse_args()
    files=sorted(SRC.rglob('*.stl'))
    if args.pilot:
        inventory=json.loads((OUT/'input_inventory.json').read_text())
        chosen=[inventory[0],min(inventory,key=lambda r:r['faces']),max(inventory,key=lambda r:r['faces'])]
        chosen+=next(([r] for r in inventory if r['watertight']),[])
        chosen+=next(([r] for r in inventory if not r['winding']),[])
        chosen+=inventory[len(inventory)//2:len(inventory)//2+3]
        files=list(dict.fromkeys(SRC/r['relative'] for r in chosen))
    started=time.time();rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures={pool.submit(one,p):p for p in files}
        last=time.time()
        for future in concurrent.futures.as_completed(futures):
            result=future.result();rows.append(result)
            if result['status']=='FAILED':print('FAILED',result['relative_path'],result['error'][-200:],flush=True)
            if len(rows)%25==0 or time.time()-last>25:
                summarize(rows,len(files),started);last=time.time()
    summary=summarize(rows,len(files),started,True)
    if args.pilot:
        (OUT/'pilot_summary.json').write_text(json.dumps({'summary':summary,'files':rows},indent=2));return
    fields=['relative_path','status','representation','input_faces','cad_faces','cad_solids','step_valid','seconds','error']
    with (OUT/'conversion_summary.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader()
        for r in sorted(rows,key=lambda x:x['relative_path']):
            d={k:r.get(k) for k in fields};d.update(cad_faces=r.get('cad',{}).get('faces'),cad_solids=r.get('cad',{}).get('solids'),step_valid=r.get('step_reimport',{}).get('valid'));writer.writerow(d)
    (OUT/'failed_files.json').write_text(json.dumps([r for r in rows if r['status']!='SUCCESS'],indent=2))
    groups={}
    for r in rows:groups.setdefault(str(Path(r['relative_path']).parent),[]).append(r)
    for name,records in groups.items():
        (OUT/name/'folder_summary.json').write_text(json.dumps({'folder':name,'total':len(records),'successful':sum(r['status']=='SUCCESS' for r in records),'files':records},indent=2))

if __name__=='__main__':main()
