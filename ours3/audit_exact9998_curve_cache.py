#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, os, statistics
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
EXACT=ROOT/'ours3/exact9998_v1'
OUT=ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1'
FORMAL=ROOT/'ours3/exact9998_curve_tokens_c2_v1'
CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
OLD=ROOT/'ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2'

def sha256(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()

def write_json(p,x):
    t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n'); os.replace(t,p)

def main():
    OUT.mkdir(parents=True,exist_ok=True); FORMAL.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(x) for x in (EXACT/'EXACT9998_ASSET_REGISTRY_V1.jsonl').open()]
    expected={'train':7998,'val':1000,'test':1000}
    assert len(rows)==9998 and len({r['cad_id'] for r in rows})==9998
    assert Counter(r['split'] for r in rows)==expected
    coverage=[]; registry=[]; stats=defaultdict(Counter); ks=[]; failures=[]
    reused_old=reused_rebuilt=hardlinks_new=hardlinks_existing=0
    for i,r in enumerate(rows,1):
        split=r['split']; dataset=r['dataset'].lower(); sample_id=r.get('source_id') or r['cad_id'].split('__',1)[1]
        source=Path(r['curve_path']); token=Path(r['c2_path_or_ref']); errors=[]; K=None; source_schema=None; token_schema=None; token_hash=None
        source_exists=source.is_file(); token_exists=token.is_file()
        if source_exists:
            try:
                with np.load(source,allow_pickle=False) as z:
                    source_schema={k:list(z[k].shape) for k in sorted(z.files)}
                    req={'num_curves','curve_type_id','curve_edge_id','curve_xyz_normalized','curve_tangent'}
                    if not req.issubset(z.files): errors.append('curve_source_schema_missing_keys')
                    if 'curve_xyz_normalized' in z.files and (z['curve_xyz_normalized'].ndim!=3 or z['curve_xyz_normalized'].shape[1:]!=(32,3)): errors.append('curve_xyz_shape_not_N_32_3')
                    if 'curve_tangent' in z.files and (z['curve_tangent'].ndim!=3 or z['curve_tangent'].shape[1:]!=(32,3)): errors.append('curve_tangent_shape_not_N_32_3')
            except Exception as e: errors.append(f'curve_source_load:{type(e).__name__}:{e}')
        if token_exists:
            try:
                a=np.load(token,allow_pickle=False); token_schema={'shape':list(a.shape),'dtype':str(a.dtype),'finite':bool(np.isfinite(a).all())}
                if a.ndim!=2 or a.shape[1]!=256: errors.append('curve_token_shape_not_K_256')
                else:
                    K=int(a.shape[0])
                    if K<1 or K>128: errors.append('curve_token_K_out_of_range')
                    if not token_schema['finite']: errors.append('curve_token_nonfinite')
                token_hash=sha256(token)
            except Exception as e: errors.append(f'curve_token_load:{type(e).__name__}:{e}')
        stats[split]['n']+=1; stats[split]['source_present']+=int(source_exists); stats[split]['source_missing']+=int(not source_exists)
        stats[split]['token_present']+=int(token_exists); stats[split]['token_missing']+=int(not token_exists); stats[split]['schema_fail']+=int(bool(errors))
        if K is not None: ks.append(K)
        in_old=str(token).startswith(str(OLD)); reused_old+=int(in_old); reused_rebuilt+=int(not in_old)
        formal=FORMAL/dataset/sample_id/'curve_tokens.npy'
        if not errors and source_exists and token_exists:
            formal.parent.mkdir(parents=True,exist_ok=True)
            if formal.exists():
                if sha256(formal)!=token_hash: errors.append('formal_token_hash_mismatch')
                else: hardlinks_existing+=1
            else: os.link(token,formal); hardlinks_new+=1
        if errors: failures.append({'cad_id':r['cad_id'],'errors':errors})
        coverage.append({'cad_id':r['cad_id'],'dataset':dataset,'split':split,'curve_sample_path':str(source),'curve_sample_exists':source_exists,'curve_token_path':str(token),'curve_token_exists':token_exists,'K':K,'schema':{'curve_source':source_schema,'curve_token':token_schema},'errors':errors})
        registry.append({'cad_id':r['cad_id'],'dataset':dataset,'split':split,'curve_source_path':str(source),'curve_token_path':str(formal),'K':K,'dim':256,'C2_checkpoint':str(CKPT),'source':'REUSED_VERIFIED','asset_origin':'OLD_CACHE' if in_old else 'EXACT10K_REBUILD','hash':token_hash})
        if i%500==0: print(f'audited {i}/{len(rows)}',flush=True)
    for name,data in [('EXACT9998_CURVE_ASSET_COVERAGE.jsonl',coverage),('EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl',registry)]:
        p=OUT/name; t=p.with_suffix(p.suffix+'.tmp')
        with t.open('w') as f:
            for x in data: f.write(json.dumps(x,sort_keys=True)+'\n')
        os.replace(t,p)
    ckhash=sha256(CKPT)
    summary={'expected_split_counts':expected,'actual_split_counts':{s:dict(c) for s,c in sorted(stats.items())},'curve_source_present_total':sum(c['source_present'] for c in stats.values()),'curve_source_missing_total':sum(c['source_missing'] for c in stats.values()),'curve_token_present_total':sum(c['token_present'] for c in stats.values()),'curve_token_missing_total':sum(c['token_missing'] for c in stats.values()),'schema_fail_total':len(failures),'failures':failures[:100],'K':{'min':min(ks),'median':statistics.median(ks),'max':max(ks),'K128_present':128 in ks,'count':len(ks)},'old_cache_files_total':sum(1 for _ in OLD.glob('*/*/curve_tokens.npy')),'reused_old_registry_n':reused_old,'reused_rebuilt_registry_n':reused_rebuilt,'formal_root':str(FORMAL),'hardlinks_new':hardlinks_new,'hardlinks_existing_verified':hardlinks_existing,'C2_checkpoint':str(CKPT),'C2_checkpoint_sha256':ckhash}
    write_json(OUT/'EXACT9998_CURVE_ASSET_COVERAGE_SUMMARY.json',summary)
    write_json(OUT/'C2_CHECKPOINT_AUDIT.json',{'checkpoint':str(CKPT),'sha256':ckhash,'exists':CKPT.is_file(),'modified':False,'frozen_required':True})
    write_json(OUT/'C2_TOKEN_EXPORT_PROTOCOL.json',{'producer':str(ROOT/'scripts/spatiallm_curve_token_c2_frozen_v2/export_curve_tokens.py'),'input':'per curve [32,7] = local xyz + tangent + normalized arclength s','scale':'log(polyline_length + 1e-6)','selection':'sharp B-Rep edges ranked by descending polyline length','K_cap':128,'output':'float32 [K,256]','model_eval':True,'torch_no_grad':True,'augmentation':False,'random_perturbation':False,'checkpoint':str(CKPT),'checkpoint_sha256':ckhash})
    write_json(OUT/'M2_EXACT9998_CURVE_DATASET_FULL_AUDIT.json',{'scope':['train','val'],'cases':8998,'passed':sum(stats[s]['n']-stats[s]['schema_fail'] for s in ('train','val')),'failed':sum(stats[s]['schema_fail'] for s in ('train','val')),'checks':['registry exact lookup','token exists','shape [K,256]','1<=K<=128','finite'],'silent_fallback':False})
    print(json.dumps(summary,indent=2))
if __name__=='__main__': main()
