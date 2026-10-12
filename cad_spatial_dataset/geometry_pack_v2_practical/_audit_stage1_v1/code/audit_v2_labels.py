"""Isolated label audit. Never decodes models or reads prediction metrics."""
import argparse, ast, collections, concurrent.futures, hashlib, json, os
import pathlib, shutil, subprocess, sys, time

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'cad_spatial_dataset/geometry_pack_v2_practical/_audit_stage1_v1'
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'scripts/deepcad')]

def digest(p):
    h = hashlib.sha256()
    with pathlib.Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def write_new(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:
        if isinstance(obj,str): f.write(obj)
        else: json.dump(obj,f,ensure_ascii=False,indent=2,allow_nan=False)

def inventory():
    records=[]; frozen={}
    for split in ('train','val','test'):
        p=ROOT/f'cad_spatial_dataset/joint_deepcad_fusion360_v1/joint_j0j2_v1_{split}.json'
        frozen[str(p)]=digest(p)
        for r in json.loads(p.read_text()):
            pack=ROOT/'cad_spatial_dataset'/r['point_clouds'][0]; pack=pack.parent
            meta=json.loads((pack/'metadata.json').read_text())
            code=(pack/'cad_target.dsl').read_text(); tree=ast.parse(code)
            calls=[n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
            target=[m['value'] for m in r['conversations'] if m['from']=='gpt']
            ast_hash=hashlib.sha256(ast.dump(tree,include_attributes=False).encode()).hexdigest()
            src=pathlib.Path(meta['cad_target']['model_step'])
            paths=[pack/k for k in ('cad_target.dsl','coordinate_transform.json','source.json','surface_points.npy','edge_points_detected.npy','edge_points_gt_sharp.npy')]+[src]
            for fp in paths:
                if fp.is_file(): frozen[str(fp)]=digest(fp)
            records.append(dict(cad_id=r['id'],dataset=r['dataset'],sample_id=r['sample_id'],old_split=split,pack=str(pack),source_step=str(src),source_identity=str(src.resolve()),source_json_hash=digest(pack/'source.json'),dsl_ast_sha256=ast_hash,operation_count=len(calls),operation_names=calls,manifest_matches_pack=bool(target and ast.dump(ast.parse(target[0]),include_attributes=False)==ast.dump(tree,include_attributes=False)),source_exists=src.is_file()))
    for rel in ('scripts/edge_aware_cad_planner_v1/cad_dsl.py','scripts/deepcad/cad_canonical.py','scripts/geometry_pack_v1/occ.py','scripts/geometry_pack_v1/surface.py','ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/surface_idx4096.npz'):
        p=ROOT/rel; frozen[str(p)]=digest(p)
    write_new(OUT/'inventory.json',records); write_new(OUT/'V1_FROZEN_SHA256.json',frozen)
    return records

def mesh_from_step(p):
    from geometry_pack_v1.occ import load_step_shape,tessellate_shape,triangulation_to_arrays
    shape=load_step_shape(pathlib.Path(p)); tessellate_shape(shape)
    v,f=triangulation_to_arrays(shape)
    if len(f)==0: raise ValueError('empty triangulation')
    return v,f

def fingerprint(v,f):
    import numpy as np
    # Translation/positive-uniform-scale invariant, orientation retained.
    mn=v.min(0); diag=float(np.linalg.norm(v.max(0)-mn))
    if diag<=0: raise ValueError('degenerate source bbox')
    q=np.rint((v-mn)/diag/1e-5).astype('<i8')
    # Triangle orientation and vertex ordering invariant; triangulation-dependent.
    ids,inv=np.unique(q,axis=0,return_inverse=True)
    tris=np.sort(inv[f],axis=1); tris=np.unique(tris,axis=0)
    h=hashlib.sha256(ids.astype('<i8').tobytes()+tris.astype('<i8').tobytes()).hexdigest()
    return h,diag

def worker(index):
    import numpy as np
    from scipy.spatial import cKDTree
    from geometry_pack_v1.surface import sample_surface_uniform
    from edge_aware_cad_planner_v1.cad_dsl import parse_dsl,execute_dsl
    from cad_canonical import load_transform_json,transform_dsl
    rec=json.loads((OUT/'inventory.json').read_text())[index]
    dest=OUT/'replay'/rec['cad_id']; dest.mkdir(parents=True,exist_ok=False)
    ans=dict(rec,index=index,parsed=False,execution_ok=False,step_reload=False,label_gate=False)
    start=time.time(); stage='source_step'
    try:
        vg,fg=mesh_from_step(rec['source_step']); fp,diag=fingerprint(vg,fg)
        ans.update(geometry_fingerprint=fp,gt_bbox_diag=diag,source_triangles=len(fg))
        pack=pathlib.Path(rec['pack']); stage='inverse_transform'
        tf=load_transform_json(pack/'coordinate_transform.json')
        code=transform_dsl((pack/'cad_target.dsl').read_text(),tf,inverse=True)
        write_new(dest/'cad_target_source.dsl',code)
        stage='parse'; parse_dsl(code); ans['parsed']=True
        stage='execute'; execute_dsl(code,dest/'reconstructed.step'); ans['execution_ok']=True
        stage='reload'; vp,fpred=mesh_from_step(dest/'reconstructed.step'); ans['step_reload']=True
        stage='geometry'; seed=int(hashlib.sha256(rec['cad_id'].encode()).hexdigest()[:8],16)
        a,_,_=sample_surface_uniform(vg,fg,20000,seed)
        b,_,_=sample_surface_uniform(vp,fpred,20000,seed^0x5A5A5A5A)
        ab=cKDTree(b).query(a,workers=1)[0]/diag
        ba=cKDTree(a).query(b,workers=1)[0]/diag
        chamfer=float((ab.mean()+ba.mean())/2); coverage=float((ab<=.02).mean())
        ans.update(chamfer_rel=chamfer,gt_to_replay=float(ab.mean()),replay_to_gt=float(ba.mean()),coverage_02=coverage,false_positive_surface_fraction_02=float((ba>.02).mean()),distance_p95=float(np.percentile(np.r_[ab,ba],95)),bbox_extent_ratio=((vp.max(0)-vp.min(0))/np.maximum(vg.max(0)-vg.min(0),1e-12)).tolist(),bbox_center_error_rel=float(np.linalg.norm((vp.max(0)+vp.min(0)-vg.max(0)-vg.min(0))/2)/diag))
        surf=np.load(pack/'surface_points.npy',mmap_mode='r'); ans['surface_shape']=list(surf.shape)
        ans['label_gate']=bool(chamfer<=.01 and coverage>=.98 and surf.shape==(8192,6) and rec['manifest_matches_pack'])
    except Exception as exc:
        ans.update(failure_stage=stage,error=repr(exc))
    ans['elapsed_s']=time.time()-start
    write_new(dest/'audit.json',ans)

def launch_one(index):
    dest=OUT/'replay'/json.loads((OUT/'inventory.json').read_text())[index]['cad_id']
    if (dest/'audit.json').exists(): return json.loads((dest/'audit.json').read_text())
    log=OUT/'logs'/f'{index:04d}.log'; log.parent.mkdir(exist_ok=True)
    env=os.environ.copy(); env.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',CUDA_VISIBLE_DEVICES='')
    with log.open('x') as f:
        try: p=subprocess.run([sys.executable,'-B',__file__,'--worker',str(index)],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=150)
        except subprocess.TimeoutExpired: return dict(index=index,failure_stage='timeout',label_gate=False)
    if (dest/'audit.json').exists(): return json.loads((dest/'audit.json').read_text())
    return dict(index=index,failure_stage='worker_exit',returncode=p.returncode,label_gate=False)

def summarize(rows,tag):
    import numpy as np
    inv=json.loads((OUT/'inventory.json').read_text())
    bysource={}
    for ds in ('deepcad','fusion360'):
        rr=[r for r in rows if inv[r['index']]['dataset']==ds]
        metric=[r['chamfer_rel'] for r in rr if 'chamfer_rel'in r]
        bysource[ds]=dict(n=len(rr),parsed=sum(bool(r.get('parsed')) for r in rr),execution_ok=sum(bool(r.get('execution_ok')) for r in rr),reload_ok=sum(bool(r.get('step_reload')) for r in rr),label_pass=sum(bool(r.get('label_gate')) for r in rr),chamfer_quantiles=dict(zip(('min','median','p90','p95','max'),np.percentile(metric,[0,50,90,95,100]).tolist())) if metric else {})
    parent=list(range(len(inv)))
    def find(i):
        while parent[i]!=i: parent[i]=parent[parent[i]]; i=parent[i]
        return i
    matches=[]
    for key in ('source_identity','source_json_hash','dsl_ast_sha256','geometry_fingerprint'):
        groups=collections.defaultdict(list)
        source=rows if key=='geometry_fingerprint' else [dict(x,index=i) for i,x in enumerate(inv)]
        for r in source:
            if r.get(key): groups[r[key]].append(r['index'])
        for h,members in groups.items():
            if len(members)<2:continue
            matches.append(dict(method=key,hash=h,cad_ids=[inv[i]['cad_id'] for i in members],old_splits=[inv[i]['old_split'] for i in members]))
            for i in members[1:]:parent[find(i)]=find(members[0])
    groups=collections.defaultdict(list)
    for i,r in enumerate(inv):groups[find(i)].append(r['cad_id'])
    sizes=collections.Counter('simple' if r['operation_count']<=5 else 'medium' if r['operation_count']<=10 else 'hard' for r in inv)
    summary=dict(status='LABEL_AUDIT_ONLY_NO_TRAINING',audited=len(rows),planned=len(inv),by_source=bysource,identity_groups=len(groups),duplicate_groups=sum(len(v)>1 for v in groups.values()),grouping_complete=len(rows)==len(inv),provisional_thresholds={'chamfer_rel_max':.01,'coverage_02_min':.98,'coverage_distance_rel':.02,'execution_rate_min':.99,'reload_rate_min':.99},metric='symmetric unsquared mean NN distance / GT tessellation bbox diagonal; 20000 area-uniform points per shape, independent deterministic seeds; no alignment',geometry_fingerprint_limit='Quantized normalized triangle hash is invariant to vertex ordering and triangle winding but not retessellation; near duplicate fingerprint completeness NOT certified.',operation_count_definition='all DSL constructor calls, including sketch and boolean calls',operation_strata=dict(sizes),v1_modified_by_this_task=False,test_decode_or_model_metrics_read=False,new_training_started=False,old_split_rewritten=False,full_v2_built=False)
    write_new(OUT/'reports'/f'{tag}_SUMMARY.json',summary)
    write_new(OUT/'reports'/f'{tag}_RESULTS.json',rows)
    write_new(OUT/'reports'/f'{tag}_GROUPING.json',{'groups':list(groups.values()),'matches':matches,'note':'Conservative grouping proposal only; no new split assigned, no records removed.'})
    print(json.dumps(summary,indent=2),flush=True)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--worker',type=int); ap.add_argument('--inventory',action='store_true'); ap.add_argument('--limit',type=int,default=0); ap.add_argument('--workers',type=int,default=6); ap.add_argument('--tag',default='FULL'); args=ap.parse_args()
    if args.worker is not None:return worker(args.worker)
    if args.inventory:return inventory()
    inv=json.loads((OUT/'inventory.json').read_text()); indices=list(range(len(inv)))
    if args.limit: indices=[i for ds in ('deepcad','fusion360') for i,x in enumerate(inv) if x['dataset']==ds][:args.limit] if args.limit>10 else [0,1,2]+[i for i,x in enumerate(inv) if x['dataset']=='fusion360'][:max(0,args.limit-3)]
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        for f in concurrent.futures.as_completed([pool.submit(launch_one,i) for i in indices]):
            rows.append(f.result())
            if len(rows)%50==0 or len(rows)==len(indices):print(json.dumps({'completed':len(rows),'total':len(indices),'label_pass':sum(bool(r.get('label_gate')) for r in rows)}),flush=True)
    summarize(sorted(rows,key=lambda x:x['index']),args.tag)
    frozen=json.loads((OUT/'V1_FROZEN_SHA256.json').read_text())
    changed=[p for p,h in frozen.items() if not pathlib.Path(p).is_file() or digest(p)!=h]
    write_new(OUT/'reports'/f'{args.tag}_V1_VERIFY.json',{'changed':changed,'checked_files':len(frozen),'pass':not changed})
    if changed:raise SystemExit('FROZEN_INPUT_CHANGED')

if __name__=='__main__':main()
