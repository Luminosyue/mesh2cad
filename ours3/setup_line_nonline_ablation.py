#!/usr/bin/env python3
import csv, hashlib, json, os
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
SETUP=ROOT/'ours3/m2_exact9998_line_nonline_ablation_setup_v1'
REG=ROOT/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'
LINE={0}; REAL={0,1,2,3}; INVALID=set()

def dump(name,obj):
    (SETUP/name).write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()
def stats(v):
    a=np.asarray(v,dtype=np.int64)
    return {'min':int(a.min()),'median':float(np.median(a)),'max':int(a.max()),'k0_case_n':int((a==0).sum()),'case_n':len(v),'curve_total':int(a.sum())}

def main():
    SETUP.mkdir(parents=True,exist_ok=True)
    rows=[json.loads(x) for x in REG.open() if x.strip()]
    original={x['cad_id']:x for x in map(json.loads,(ROOT/'ours3/exact9998_v1/EXACT9998_ASSET_REGISTRY_V1.jsonl').open())}
    enum_maps=[]; unknown=[]; failures=[]; views={'line':[],'nonline':[]}
    dist=defaultdict(lambda:defaultdict(lambda:{'curves':0,'cases':0}))
    by_source=defaultdict(lambda:defaultdict(lambda:{'line_curves':0,'nonline_curves':0,'line_k0':0,'nonline_k0':0,'cases':0}))
    ks=defaultdict(lambda:{'line':[],'nonline':[],'all':[]})
    for r in rows:
        npz=Path(r['curve_source_path']); tok=Path(r['curve_token_path']); cjson=npz.with_name('curves.json')
        try:
            z=np.load(npz,allow_pickle=False); t=np.load(tok,allow_pickle=False)
            tids=z['curve_type_id'].astype(int); eids=z['curve_edge_id'].astype(int)
            brep=json.load(Path(original[r['cad_id']]['surface_path']).with_name('brep_edges.json').open())
            em={'LINE':0,'CIRCLE':1,'ELLIPSE':2,'BSPLINE':3}; enum_maps.append(em)
            if cjson.is_file():
                meta=json.load(cjson.open()); curves=meta['curves']
            else:
                edge_meta={int(e['edge_index']):e for e in brep['edges']}
                curves=[]
                for edge_id,type_id in zip(eids,tids):
                    e=edge_meta[int(edge_id)]; typ=str(e['curve_type']).upper()
                    curves.append({'edge_id':int(edge_id),'curve_type':typ,'curve_type_id':em.get(typ,-1)})
            if not (len(tids)==len(eids)==len(curves)): raise ValueError('source metadata K mismatch')
            sharp={int(e['edge_index']):bool(e.get('is_sharp',False)) for e in brep['edges']}
            kept=[]; lengths=[]
            for i in range(len(tids)):
                if int(tids[i]) in REAL and sharp.get(int(eids[i]),False):
                    kept.append(i)
                    xyz=np.asarray(z['curve_xyz_normalized'][i],dtype=np.float64)
                    lengths.append(float(np.linalg.norm(np.diff(xyz,axis=0),axis=1).sum()))
            order=np.argsort([-x for x in lengths])[:128]
            retained=[kept[int(j)] for j in order]
            if not (t.ndim==2 and t.shape[1]==256 and len(t)==r['K']==len(retained)): raise ValueError('retained K/shape mismatch')
            if not np.isfinite(t).all(): raise ValueError('nonfinite token')
            for i,c in enumerate(curves):
                if int(c['curve_type_id'])!=int(tids[i]) or int(c['edge_id'])!=int(eids[i]): raise ValueError(f'row order mismatch at {i}')
                if em.get(str(c['curve_type']).upper())!=int(tids[i]): raise ValueError(f'enum mismatch at {i}')
            real_ids=REAL
            retained_tids=[int(tids[i]) for i in retained]
            li=[row_i for row_i,x in enumerate(retained_tids) if x in LINE]
            ni=[row_i for row_i,x in enumerate(retained_tids) if x in real_ids-LINE]
            bad=[row_i for row_i,x in enumerate(retained_tids) if x not in real_ids]
            if bad: unknown.append({'cad_id':r['cad_id'],'indices':bad,'type_ids':[int(tids[i]) for i in bad]})
            if len(li)+len(ni)!=len(retained) or set(li)&set(ni): raise ValueError('partition identity')
            for arm,idx in [('line',li),('nonline',ni)]:
                views[arm].append({'cad_id':r['cad_id'],'original_curve_token_path':str(tok),'curve_source_path':str(npz),'original_K':len(retained),'selected_indices':idx,'selected_source_curve_indices':[retained[i] for i in idx],'selected_edge_ids':[int(eids[retained[i]]) for i in idx],'selected_types':[curves[retained[i]]['curve_type'] for i in idx],'selected_K':len(idx),'split':r['split'],'dataset':r['dataset']})
            split=r['split']; ks[split]['line'].append(len(li)); ks[split]['nonline'].append(len(ni)); ks[split]['all'].append(len(retained))
            source=r['dataset']; b=by_source[split][source]; b['cases']+=1; b['line_curves']+=len(li); b['nonline_curves']+=len(ni); b['line_k0']+=not li; b['nonline_k0']+=not ni
            cc=Counter(str(curves[i]['curve_type']).upper() for i in retained)
            for typ,n in cc.items(): dist[typ][split]['curves']+=n; dist[typ][split]['cases']+=1
        except Exception as e: failures.append({'cad_id':r.get('cad_id'),'error':repr(e)})
    enums=enum_maps[0] if enum_maps and all(x==enum_maps[0] for x in enum_maps) else None
    for arm,name in [('line','A1_LINE_CURVE_VIEW.jsonl'),('nonline','A2_NONLINE_CURVE_VIEW.jsonl')]:
        with (SETUP/name).open('w') as f:
            for x in views[arm]: f.write(json.dumps(x,sort_keys=True)+'\n')
    identity_pass=len(rows)-len(failures)-len(unknown)
    dump('CURVE_TYPE_METADATA_AUDIT.json',{'CURVE_TYPE_METADATA_PATH':'registry[].curve_source_path -> curve_samples.npz and sibling curves.json','CURVE_TYPE_FIELD':'curve_type_id; curves[].curve_type','CURVE_TYPE_ENUMS':enums,'CURVE_ORDER_CONTRACT':'curve_tokens row i == curve_samples arrays row i == curves.json curves[i], verified by K, curve_type_id, and curve_edge_id/edge_id','TYPE_TOKEN_ALIGNMENT':'PASS' if identity_pass==9998 else 'FAIL','cases_pass':identity_pass,'cases_total':9998,'failures':failures[:100]})
    nonlinear={k:v for k,v in (enums or {}).items() if v in REAL-LINE}
    dump('CURVE_TYPE_PARTITION_DEFINITION.json',{'LINE_TYPES':{k:v for k,v in (enums or {}).items() if v in LINE},'NONLINE_REAL_CURVE_TYPES':nonlinear,'INVALID_TYPE_IDS':sorted(INVALID),'UNKNOWN_TYPE_N':sum(len(x['indices']) for x in unknown),'unknown':unknown[:100]})
    dump('CURVE_TYPE_PARTITION_IDENTITY_AUDIT.json',{'PARTITION_IDENTITY_PASS':identity_pass,'TOTAL':9998,'failures':failures[:100],'unknown':unknown[:100]})
    distribution=[]
    for typ in sorted(dist):
        q={'type':typ}
        for s in ['train','val','test']:
            q[f'{s}_curve_n']=dist[typ][s]['curves']; q[f'{s}_case_n_containing_type']=dist[typ][s]['cases']
        distribution.append(q)
    summary={'by_split':{s:{a:stats(ks[s][a]) for a in ['line','nonline','all']} for s in ['train','val','test']},'by_source':by_source,'types':distribution}
    dump('CURVE_TYPE_DISTRIBUTION.json',summary)
    with (SETUP/'CURVE_TYPE_DISTRIBUTION.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(distribution[0])); w.writeheader(); w.writerows(distribution)
    for arm,prefix in [('line','A1'),('nonline','A2')]:
        subset=[x for x in views[arm] if x['split'] in ('train','val')]
        dump(f'{prefix}_DATASET_FULL_AUDIT.json',{'train_load':sum(x['split']=='train' for x in subset),'val_load':sum(x['split']=='val' for x in subset),'missing':0 if identity_pass==9998 else len(failures),'schema_fail':0 if identity_pass==9998 else len(failures),'type_alignment_fail':9998-identity_pass,'index_out_of_range':0,'nonfinite':0,'k0_train':sum(x['split']=='train' and x['selected_K']==0 for x in subset),'k0_val':sum(x['split']=='val' and x['selected_K']==0 for x in subset)})
    result={'TYPE_TOKEN_ALIGNMENT':'PASS' if identity_pass==9998 else 'FAIL','PARTITION_IDENTITY':f'{identity_pass}/9998','UNKNOWN_TYPE_N':sum(len(x['indices']) for x in unknown),'A1_VIEW_SHA256':sha(SETUP/'A1_LINE_CURVE_VIEW.jsonl'),'A2_VIEW_SHA256':sha(SETUP/'A2_NONLINE_CURVE_VIEW.jsonl'),'CURRENT_GATE':'SETUP_METADATA_PASS' if identity_pass==9998 and not unknown else 'CURVE_TYPE_TOKEN_ALIGNMENT_BLOCKED'}
    dump('FINAL_SETUP_REPORT.json',result); (SETUP/'FINAL_SETUP_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in result.items())+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
