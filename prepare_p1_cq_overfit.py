import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='2'
from pathlib import Path
import sys,json,collections,hashlib
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
EXP=ROOT/'ours3/p1_cadquery_overfit16_v1'
sys.path[:0]=[str(ROOT),str(ROOT/'scripts'),str(ROOT/'p3_xpart_open_cases/_cadquery_batch_code_20260922')]
import numpy as np,trimesh,cadquery as cq,torch,yaml
from transformers import AutoTokenizer
from build_partsam_p1 import export_curves,sample
from spatiallm_curve_token_c2_frozen_v2.export_curve_tokens import load_backbone,curve_inputs
from quality import tessellate,evaluate

def dump(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
def lit(x):return repr(np.round(np.asarray(x),6).tolist())
def code_for(p,s,t):
    b=np.array(p['basis']);unit=s/p['construction_scale'];center=np.array(p['center'])*s+t;lines=['import cadquery as cq']
    for i,f in enumerate(p['features']):
        assert f['type']=='extrude'
        origin=center+b[2]*f['start']*unit
        expr=f'cq.Workplane(cq.Plane(origin={lit(origin)}, xDir={lit(b[0])}, normal={lit(b[2])}))'
        for ring in f['loops']:
            if isinstance(ring,dict):
                # Reset workplane center after constructing each circular wire.
                c=np.array(ring['center'])*unit
                expr+=f'.center({round(float(c[0]),6)}, {round(float(c[1]),6)}).circle({round(ring["radius"]*unit,6)}).center({round(float(-c[0]),6)}, {round(float(-c[1]),6)})'
            else:expr+=f'.polyline({lit(np.array(ring)*unit)}).close()'
        lines.append(f'body_{i} = '+expr+f'.extrude({round(f["length"]*unit,6)})')
    expr='body_0'
    for i in range(1,len(p['features'])):expr+=f'.union(body_{i})'
    lines.append('result = '+expr);return '\n'.join(lines)+'\n'

def main():
    EXP.mkdir(exist_ok=True)
    for n in ['data','assets','audits','launch','configs','logs']:(EXP/n).mkdir(exist_ok=True)
    checkpoint=ROOT/'ours3/p1_operation_aware_structure_loss_v1/runs/p1/checkpoint-8000'
    tok=AutoTokenizer.from_pretrained(checkpoint,use_fast=True)
    candidates=json.loads((ROOT/'p3_xpart_open_cases/_cadquery_batch_20260922/overfit_candidates.json').read_text())['parts']
    proposals=[]
    for r in candidates:
        if r['method']!='extrude':continue
        folder=Path(r['script']).parent;p=json.loads((folder/'parameters.json').read_text());m=trimesh.load(r['source'],force='mesh');s=6/np.linalg.norm(m.extents);t=-m.bounds[0]*s
        code=code_for(p,s,t);n=len(tok.encode(code,add_special_tokens=False));proposals.append((n,r,p,code,s,t))
    proposals.sort(key=lambda x:x[0]);counts=collections.Counter();rows=[];registry=[];audit=[];errors=[]
    backbone,_=load_backbone(ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt',torch.device('cpu'));torch.set_num_threads(2)
    for n,r,p,code,s,t in proposals:
        if len(rows)>=16:break
        if counts[r['case']]>=2 or n>1800:continue
        sid=r['case']+'__'+r['part'];dest=EXP/'assets/XPart/geometry_pack_v1'/sid;dest.mkdir(parents=True,exist_ok=True)
        try:
            namespace={};exec(compile(code,'target.py','exec'),namespace);shape=namespace['result'].val();assert shape.isValid() and len(shape.Solids())==1
            ref=cq.importers.importStep(str(Path(r['script']).with_suffix('.step'))).val().scale(s).translate(tuple(t))
            q=evaluate(tessellate(ref),tessellate(shape));assert q['p95_distance_pct_diagonal']<.01 and q['volume_error_pct']<.1,q
            shape.exportStep(str(dest/'target.step'));(dest/'target.py').write_text(code)
            m=trimesh.load(r['source'],force='mesh');m.vertices=m.vertices*s+t;surface=sample(m,8192,20260922);np.save(dest/'surface_points.npy',surface)
            rec={'cad_id':'xpart__'+sid};export_curves(shape,dest,rec)
            z=np.load(dest/'curve_samples.npz');ids=np.load(dest/'selected_curve_indices.npy');fs=[];ss=[]
            for i in ids:
                f,sc=curve_inputs(z['curve_xyz_normalized'][i].astype(np.float64),z['curve_tangent'][i].astype(np.float32));fs.append(f);ss.append(sc)
            with torch.no_grad():tokens=backbone(torch.from_numpy(np.stack(fs)),torch.from_numpy(np.stack(ss)))['token'].float().numpy()
            assert tokens.shape==(len(ids),256) and np.isfinite(tokens).all();np.save(dest/'curve_tokens.npy',tokens)
            prompt='<point_cloud>\nGenerate CadQuery Python code for this geometry. Output only Python code, beginning with import cadquery as cq and assigning the final solid to result. Do not export files.'
            row={'id':'xpart__'+sid,'dataset':'xpart','sample_id':sid,'conversations':[{'from':'human','value':prompt},{'from':'gpt','value':code}],'point_clouds':[str(dest/'surface_points.npy')]};rows.append(row)
            registry.append({'cad_id':row['id'],'dataset':'xpart','curve_token_path':str(dest/'curve_tokens.npy'),'K':len(ids)})
            record={'id':row['id'],'source':r['source'],'source_sha256':hashlib.sha256(Path(r['source']).read_bytes()).hexdigest(),'target_tokens':n,'curve_tokens':len(ids),'conversion_quality':q,'scale':s,'translation':t.tolist(),'input_provenance':'surface from completed OBJ; oracle sharp curves from reconstructed target CAD','target':str(dest/'target.py')};audit.append(record);dump(dest/'record.json',record);counts[r['case']]+=1
            print('READY',len(rows),sid,n,flush=True)
        except Exception as e:errors.append({'id':sid,'error':str(e)});print('SKIP',sid,str(e)[:200],flush=True)
    assert len(rows)==16,(len(rows),errors)
    dump(EXP/'data/train.json',rows);dump(EXP/'data/eval_memorization.json',rows)
    dump(EXP/'data/dataset_info.json',{name:{'file_name':file,'formatting':'sharegpt','columns':{'messages':'conversations','point_clouds':'point_clouds'}} for name,file in [('cq16_train','train.json'),('cq16_memorization','eval_memorization.json')]})
    (EXP/'data/curve_registry.jsonl').write_text('\n'.join(json.dumps(r) for r in registry)+'\n')
    dump(EXP/'audits/data_audit.json',{'count':len(rows),'samples':audit,'excluded':errors,'evaluation':'Same 16 samples; memorization only, not generalization','source_checkpoint':str(checkpoint),'method':'P1 initialization and geometry architecture; standard CE, no DSL operation auxiliary loss','oracle_input':True})
    cfg=yaml.safe_load((ROOT/'ours3/p1_operation_aware_structure_loss_v1/configs/p1_exact9998_train.yaml').read_text())
    cfg.update(model_name_or_path=str(checkpoint),dataset='cq16_train',eval_dataset='cq16_memorization',dataset_dir=str(EXP/'data'),output_dir=str(EXP/'runs/overfit'),logging_dir=str(EXP/'logs'),cutoff_len=4096,max_steps=400,gradient_accumulation_steps=4,learning_rate=2e-5,lr_scheduler_type='constant',warmup_ratio=0.,logging_steps=5,eval_steps=50,save_steps=100,save_total_limit=1,save_only_model=True,load_best_model_at_end=False,preprocessing_num_workers=1,dataloader_num_workers=0,max_new_tokens=2048)
    (EXP/'configs/train.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
    print('DATA_READY',len(rows),flush=True)
if __name__=='__main__':main()
