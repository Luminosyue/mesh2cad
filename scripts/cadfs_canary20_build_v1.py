#!/usr/bin/env python3
"""CADFS_OVERFIT100_V1 Canary20 build; data/audit only, never trains or decodes.

The source STEP is the only mesh geometry source.  The existing lossless
FeatureScript converter creates the canonical V3 label; source-vs-label
geometry is checked before a case becomes CLEAN_PASS.
"""
from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch
from scipy.spatial import cKDTree
from transformers import AutoTokenizer

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT/'ours3/cadfs_overfit100_v1'
CANARY = OUT/'canary20'
MANIFEST = CANARY/'CANARY20_MANIFEST.json'
RUN = CANARY/'retry2'  # preserves prior failed implementation evidence
C2 = ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
C2_SHA = '553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
M2_SUMMARY_CKPT = ROOT/'ours3/v3_clean_training_v1/runs/m2_clean_retry1/checkpoint_epoch_20'
DEVICE = torch.device(os.environ.get('CADFS_DEVICE', 'cuda:0'))
LIMIT = 4096
sys.path[:0] = [str(ROOT/'scripts'), str(ROOT/'scripts/spatiallm_geometry_prefix_v3')]
from canonical_cad_data_v4.converters.cadfs_to_dsl import CadfsUnsupported, cadfs_to_dsl
from deepcad.cad_canonical import compute_transform, transform_dsl, write_transform_json
from geometry_pack_v1.occ import tessellate_step
from geometry_pack_v1.surface import sample_surface_uniform
from geometry_pack_v1.pack import apply_canonical
from geometry_pack_v1 import pack
import curve_token_v1.build_dataset as curves
import spatiallm_curve_token_c2_frozen_v2.export_curve_tokens as exporter
import train_v3_smoke as core
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
from spatiallm_curve_token_v1 import heldout_geometry
from spatiallm_curve_token_v1.surface_cache import apply_indices, cad_key, make_indices


def dump(p: Path, x: object) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, sort_keys=True, default=str)+'\n', encoding='utf-8')


def fsha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def placement_exec(dsl: str, work: Path) -> dict:
    r={'dsl_parse':False,'dsl_exec':False,'step_write':False,'step_reload':False,'error_short':None,'canonical_step':None}
    try:
        p=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
        spec=importlib.util.spec_from_file_location('cadfs_v3_executor',p); m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
        code=m.extract_dsl_code(dsl);m.parse_dsl(code);r['dsl_parse']=True
        import cadquery as cq
        st=work/'canonical_from_dsl.step'; sl=work/'canonical_from_dsl.stl'
        m.execute_dsl(code,st,sl);r['dsl_exec']=True;r['step_write']=st.is_file() and sl.is_file();r['canonical_step']=str(st)
        if r['step_write']: cq.importers.importStep(str(st));r['step_reload']=True
    except Exception as e: r['error_short']=(type(e).__name__+': '+str(e))[-600:]
    return r


def mesh_export(v: np.ndarray, f: np.ndarray, out: Path) -> None:
    import trimesh
    trimesh.Trimesh(vertices=v, faces=f, process=False).export(out)


def geom_compare(source_pts: np.ndarray, dsl_pts: np.ndarray) -> dict:
    """Existing V3 geometry-gate policy in a shared canonical coordinate frame."""
    a,b=np.asarray(source_pts,float),np.asarray(dsl_pts,float)
    da=cKDTree(b).query(a,k=1)[0];db=cKDTree(a).query(b,k=1)[0]
    mn,mx=a.min(0),a.max(0);diag=float(np.linalg.norm(mx-mn))
    diag=max(diag,1e-12)
    chamfer=float((da.mean()+db.mean())*0.5/diag)
    thresh=.02*diag
    coverage=float(((da<=thresh).mean()+(db<=thresh).mean())*.5)
    # Existing Fusion/placement geometry threshold: chamfer_rel<=.01 plus coverage>=.98.
    return {'comparison_frame':'canonical_T_from_source_surface','chamfer_rel':chamfer,'coverage_02':coverage,
            'bbox_source_min':mn.tolist(),'bbox_source_max':mx.tolist(),
            'DSL_GEOMETRY_PASS':bool(chamfer<=.01 and coverage>=.98),
            'threshold_provenance':'geometry_pack_v2_mesh2cad frozen geometry gate: chamfer_rel<=0.01, coverage_02>=0.98'}


def build_phase_a(row: dict, c2_model) -> dict:
    sid=row['source_id']; cid=row['cad_id'];base=RUN/'cases'/cid
    if base.exists(): raise RuntimeError(f'refuse overwrite existing canary case: {base}')
    base.mkdir(parents=True); srcdir=base/'source';gp=base/'geometry_pack_v1'/cid; cdir=base/'curves';c2dir=base/'c2';srcdir.mkdir();cdir.mkdir();c2dir.mkdir()
    audit={'cad_id':cid,'source_id':sid,'SOURCE_STEP_PASS':False,'SINGLE_SOLID':bool(row.get('single_solid_candidate')),
           'MESH_PASS':False,'SURFACE_PASS':False,'DSL_PARSE_PASS':False,'DSL_EXEC_PASS':False,'STEP_WRITE_PASS':False,'STEP_RELOAD_PASS':False,
           'DSL_GEOMETRY_PASS':False,'CURVE_PASS':False,'C2_PASS':False,'clean_status':'CLEAN_REJECT','primary_reject_reason':None}
    try:
        fs,step=Path(row['source_fs_path']),Path(row['source_step_path'])
        audit['SOURCE_STEP_PASS']=fs.is_file() and step.is_file() and bool(row.get('single_solid_candidate'))
        if not audit['SOURCE_STEP_PASS']: raise RuntimeError('SOURCE_OR_SINGLE_SOLID')
        shutil.copy2(fs,srcdir/'source.fs');shutil.copy2(step,srcdir/'source.step')
        raw_dsl, conv=cadfs_to_dsl(fs.read_text(encoding='utf-8',errors='replace'))
        # Derive T from the original source STEP, then delegate all mesh/surface
        # and sharp-edge assets to the frozen V3 geometry pack implementation.
        tess=tessellate_step(step);v,f=tess['vertices'],tess['faces']
        if len(v)==0 or len(f)==0 or not np.isfinite(v).all() or not np.isfinite(f).all(): raise RuntimeError('MESH')
        pts,norm,_=sample_surface_uniform(v,f,8192,42); tf=compute_transform(pts)
        stage=base/'_pack_stage'/cid;stage.mkdir(parents=True)
        shutil.copy2(step,stage/'model.step')
        (stage/'program_canonical.dsl').write_text(transform_dsl(raw_dsl,tf),encoding='utf-8')
        write_transform_json(stage/'coordinate_transform.json',tf)
        dump(stage/'source.json',{'cad_id':cid,'source':'CADFS','source_step':str(step),'source_featurescript':str(fs)})
        pack.build_one(stage,gp.parent,overwrite=False)
        shutil.copy2(gp/'cad_target.dsl',base/'cad_target.dsl')
        surf=np.load(gp/'surface_points.npy')
        audit['MESH_PASS']=bool((gp/'mesh.obj').is_file())
        audit['SURFACE_PASS']=bool(surf.shape==(8192,6) and np.isfinite(surf).all() and np.allclose(np.linalg.norm(surf[:,3:],axis=1),1,atol=1e-4))
        if not audit['SURFACE_PASS']:raise RuntimeError('SURFACE')
        dsl=(base/'cad_target.dsl').read_text()
        d=placement_exec(dsl,base);audit['DSL_PARSE_PASS']=d['dsl_parse'];audit['DSL_EXEC_PASS']=d['dsl_exec'];audit['STEP_WRITE_PASS']=d['step_write'];audit['STEP_RELOAD_PASS']=d['step_reload'];audit['dsl_error_short']=d['error_short']
        if not d['step_reload']:raise RuntimeError('DSL_EXECUTION')
        dt=tessellate_step(Path(d['canonical_step'])); dp,dn,_=sample_surface_uniform(dt['vertices'],dt['faces'],8192,43)
        audit.update(geom_compare(apply_canonical(pts,tf.scale,np.asarray(tf.translation)),dp));
        dump(OUT/'audits/CADFS_DSL_GEOMETRY_AUDIT.jsonl.tmp',{}) if False else None
        if not audit['DSL_GEOMETRY_PASS']:raise RuntimeError('DSL_GEOMETRY')
        # Use the frozen existing curve builder, redirecting only its output/config
        # into this isolated CADFS case. The curve source is source.step, not Dora.
        stage=base/'_curve_stage';(stage/cid).mkdir(parents=True);shutil.copy2(step,stage/cid/'model.step')
        old_dir=curves.cad_dir; old_cfg={k:dict(v) for k,v in curves.SPLITS.items()}
        try:
            curves.cad_dir=lambda _split,_sid:cdir
            curves.SPLITS['deepcad_train']['step_root']=stage
            curves.SPLITS['deepcad_train']['track_a_pack']=gp.parent
            cr=curves.build_one('deepcad_train',cid,overwrite=False)
        finally:
            curves.cad_dir=old_dir;curves.SPLITS.clear();curves.SPLITS.update(old_cfg)
        if not cr.get('ok'):raise RuntimeError('CURVE:'+str(cr.get('error')))
        z=np.load(cdir/'curve_samples.npz');n=int(z['num_curves'][0]); xyz=z['curve_xyz_normalized'];tan=z['curve_tangent'];s=z['curve_u'][...,None].astype(np.float32)
        inp=np.concatenate([xyz,tan,s],axis=-1).astype(np.float32);np.save(cdir/'curve_inputs.npy',inp)
        shutil.copy2(cdir/'curves.json',cdir/'gt_brep_curves.json')
        finite=bool(n>0 and inp.shape==(n,32,7) and np.isfinite(inp).all())
        audit.update({'curve_count':n,'curve_input_shape':list(inp.shape),'CURVE_PASS':finite})
        if not finite:raise RuntimeError('CURVE_SANITY')
        old_root=dict(exporter.PACK_ROOT)
        try:
            exporter.PACK_ROOT['deepcad']=gp.parent
            exported=exporter.process_cad('deepcad',cid,cdir,c2_model,DEVICE,True)
        finally: exporter.PACK_ROOT.update(old_root)
        if exported is None:raise RuntimeError('C2_NO_SHARP_CURVE')
        tokens=exported['tokens'];np.save(c2dir/'curve_features.npy',tokens);dump(c2dir/'meta.json',exported['meta'])
        audit.update({'C2_PASS':bool(tokens.ndim==2 and 0 < tokens.shape[0] <= n and tokens.shape[1]==256 and np.isfinite(tokens).all()),'c2_shape':list(tokens.shape),'curve_types':exported['meta'].get('type_counts',{})})
        if not audit['C2_PASS']:raise RuntimeError('C2')
        dump(base/'CONVERTER_PROVENANCE.json',{'converter':'scripts/canonical_cad_data_v4/converters/cadfs_to_dsl.py','converter_report':conv,'target':'cad_target.dsl','raw_featurescript_sha256':fsha(fs),'source_step_sha256':fsha(step),'c2_checkpoint':str(C2),'c2_sha256':C2_SHA,'C2_FROZEN':True})
    except Exception as e: audit['primary_reject_reason']=str(e).split(':',1)[0]
    dump(base/'AUDIT_PHASE_A.json',audit);return audit


def prompt(tok,arm):
    user=core.markers(arm)+'\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
    return tok.encode('<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n'+user+'<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n',add_special_tokens=False)

def load_surface(plugin,path:Path,sid:str):
    raw=np.load(path).astype(np.float64);idx=make_indices(cad_key('cadfs',sid),len(raw));sampled=apply_indices(raw,idx);x,_=heldout_geometry._voxelize_surface_edge(plugin,sampled,None)
    return x,{'index_source':'frozen_deterministic_policy','key':cad_key('cadfs',sid),'input_shape':list(raw.shape),'sampled_shape':list(sampled.shape),'v3_surface_tensor_shape':list(x.shape)}

def raw_c2(x):
    if x.ndim!=2 or x.shape[1]!=256 or len(x)>128 or not np.isfinite(x).all():raise RuntimeError('BAD_C2')
    r=np.zeros((128,256),np.float32);r[:len(x)]=x;m=torch.zeros(128,dtype=torch.bool,device=DEVICE);m[:len(x)]=True
    return torch.tensor(r,device=DEVICE).unsqueeze(0),m

def capture_labels(fn):
    got=[];old=core.module._splice_labels
    def wrap(labels,regions,target_len):
        x=old(labels,regions,target_len);got.append(x.detach().cpu());return x
    core.module._splice_labels=wrap
    try:return fn(),got[-1] if got else None
    finally:core.module._splice_labels=old

def phase_b(rows):
    ok=[r for r in rows if r['C2_PASS']]
    if not ok:return rows
    core.heldout_geometry.install();tok=AutoTokenizer.from_pretrained(core.BASE_MODEL,local_files_only=True,use_fast=False);plugin=get_cad_mm_plugin(point_token='<|point_pad|>',num_bins=1280,use_edge_score=False,separate_edge_tokens=True)
    for arm in ('b0','m2'):
        model=core.make_model(arm,DEVICE,1.9414176940917969)
        if arm=='m2':
            p=M2_SUMMARY_CKPT/'geometry_prefix_adapter.pt'
            if not p.is_file():raise RuntimeError(f'missing M2 summary checkpoint: {p}')
            model.edge_proj.load_state_dict(torch.load(p,map_location=DEVICE))
        model.eval();state={};old_splice=core.install_precomputed_second(model,arm,state)
        try:
            for r in ok:
                cid=r['cad_id'];sid=r['source_id'];base=RUN/'cases'/cid;surf,sm=load_surface(plugin,base/'geometry_pack_v1'/cid/'surface_points.npy',sid);surface=torch.tensor(surf,device=DEVICE)
                target=tok.encode((base/'cad_target.dsl').read_text()+'<|eot_id|>',add_special_tokens=False);pre=prompt(tok,arm);edge=None;summary={}
                if arm=='m2':
                    edge,mask=raw_c2(np.load(base/'c2/curve_features.npy'));state['raw_mask']=mask
                    with torch.no_grad():summ,smask=model.edge_proj(edge.to(dtype=next(model.edge_proj.parameters()).dtype),mask.unsqueeze(0))
                    summary={'SUMMARY_PASS':bool(summ.shape==(1,8,model.config.hidden_size) and int(smask.sum())==8 and torch.isfinite(summ).all()),'summary_token_count':int(summ.shape[1]),'summary_active_count':int(smask.sum())}
                else:state['raw_mask']=torch.empty(0,dtype=torch.bool,device=DEVICE);summary={'SUMMARY_PASS':True,'summary_token_count':0,'summary_active_count':0}
                with torch.no_grad():S=int(model.forward_point_cloud(surface,DEVICE,torch.bfloat16,projector=model.point_proj).shape[1])
                total=len(pre)+(S-1)+(7 if arm=='m2' else 0)+len(target);a={'SONATA_PASS':bool(S>0),'surface_token_count':S,'prompt_tokens':len(pre),'dsl_tokens':len(target)-1,'eos_tokens':1,'REAL_LENGTH':total,'CONTEXT_PASS':total<=LIMIT,**sm,**summary,'V3_SPLICE_PASS':False,'EOS_SUPERVISED':False,'RESULT_SUPERVISED':False}
                if a['CONTEXT_PASS']:
                    ids=torch.tensor([pre+target],device=DEVICE);labels=torch.tensor([[-100]*len(pre)+target],device=DEVICE);capt={}
                    hook=model.model.register_forward_pre_hook(lambda mod,args,kwargs:capt.update({'embed':int(kwargs['inputs_embeds'].shape[1]),'attn':int(kwargs['attention_mask'].shape[1])}),with_kwargs=True)
                    try:
                        with torch.no_grad():out,sp=capture_labels(lambda:model(input_ids=ids,attention_mask=torch.ones_like(ids),labels=labels,point_clouds=surface.unsqueeze(0),edge_clouds=edge))
                    finally:hook.remove()
                    valid=sp[sp!=-100] if sp is not None else torch.empty(0,dtype=torch.long);eos=tok.convert_tokens_to_ids('<|eot_id|>');res=tok.encode('result =',add_special_tokens=False)
                    a.update({'V3_SPLICE_PASS':bool(torch.isfinite(out.loss) and capt.get('embed')==total and capt.get('attn')==total),'EOS_SUPERVISED':bool(len(valid) and int(valid[-1])==eos),'RESULT_SUPERVISED':any(valid[i:i+len(res)].tolist()==res for i in range(max(0,len(valid)-len(res)+1))),'embedding_length':capt.get('embed'),'attention_length':capt.get('attn')})
                r['B0' if arm=='b0' else 'M2']=a
        finally:core.module._splice_geometry=old_splice;del model;gc.collect();torch.cuda.empty_cache()
    for r in ok:
        b,m=r['B0'],r['M2'];allpass=all([r['SOURCE_STEP_PASS'],r['SINGLE_SOLID'],r['MESH_PASS'],r['SURFACE_PASS'],r['DSL_PARSE_PASS'],r['DSL_EXEC_PASS'],r['STEP_RELOAD_PASS'],r['DSL_GEOMETRY_PASS'],r['CURVE_PASS'],r['C2_PASS'],b['SONATA_PASS'],m['SONATA_PASS'],m['SUMMARY_PASS'],b['CONTEXT_PASS'],m['CONTEXT_PASS'],b['V3_SPLICE_PASS'],m['V3_SPLICE_PASS'],b['EOS_SUPERVISED'],m['EOS_SUPERVISED'],b['RESULT_SUPERVISED'],m['RESULT_SUPERVISED']])
        r['clean_status']='CLEAN_PASS' if allpass else 'CLEAN_REJECT'
        if not allpass:
            checks=[('CONTEXT',b['CONTEXT_PASS'] and m['CONTEXT_PASS']),('SUMMARY',m['SUMMARY_PASS']),('SPLICE',b['V3_SPLICE_PASS'] and m['V3_SPLICE_PASS']),('EOS',b['EOS_SUPERVISED'] and m['EOS_SUPERVISED']),('RESULT',b['RESULT_SUPERVISED'] and m['RESULT_SUPERVISED'])]
            r['primary_reject_reason']=next((x for x,p in checks if not p),'OTHER')
        dump(RUN/'cases'/r['cad_id']/'AUDIT.json',r)
    return rows

def main():
    if not MANIFEST.is_file():raise RuntimeError('missing frozen CANARY20_MANIFEST')
    if fsha(C2)!=C2_SHA:raise RuntimeError('C2 hash mismatch')
    cases=RUN/'cases'
    if cases.exists() and any(cases.iterdir()):raise RuntimeError('refuse overwrite existing canary cases')
    cases.mkdir(parents=True, exist_ok=True)
    records=json.loads(MANIFEST.read_text())['records']
    c2,_=exporter.load_backbone(C2,DEVICE)
    try:rows=[build_phase_a(dict(r),c2) for r in records]
    finally:del c2;gc.collect();torch.cuda.empty_cache()
    rows=phase_b(rows)
    (RUN/'CANARY20_PER_CAD.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    clean=[r for r in rows if r.get('clean_status')=='CLEAN_PASS'];rej=[r for r in rows if r.get('clean_status')=='CLEAN_REJECT'];reasons=Counter(r.get('primary_reject_reason') or 'OTHER' for r in rej)
    def count(k):return sum(bool(r.get(k)) for r in rows)
    summary={'CURRENT_GATE':'CADFS_CANARY20_PASS' if len(clean)>=18 else ('CADFS_CANARY20_CONDITIONAL' if len(clean)>=12 else 'CADFS_CANARY20_FAIL'),'ATTEMPTED':len(rows),'CLEAN':len(clean),'REJECTED':len(rej),
      'SOURCE_PASS':count('SOURCE_STEP_PASS'),'MESH_PASS':count('MESH_PASS'),'SURFACE_PASS':count('SURFACE_PASS'),'DSL_PARSE_PASS':count('DSL_PARSE_PASS'),'DSL_EXEC_PASS':count('DSL_EXEC_PASS'),'STEP_RELOAD_PASS':count('STEP_RELOAD_PASS'),'DSL_GEOMETRY_PASS':count('DSL_GEOMETRY_PASS'),'CURVE_PASS':count('CURVE_PASS'),'C2_PASS':count('C2_PASS'),'SUMMARY_PASS':sum(bool(r.get('M2',{}).get('SUMMARY_PASS')) for r in rows),'CONTEXT_PASS':sum(bool(r.get('B0',{}).get('CONTEXT_PASS') and r.get('M2',{}).get('CONTEXT_PASS')) for r in rows),'V3_SPLICE_PASS':sum(bool(r.get('B0',{}).get('V3_SPLICE_PASS') and r.get('M2',{}).get('V3_SPLICE_PASS')) for r in rows),'TOP_REJECTION_REASONS':reasons.most_common(5),'C2_CHECKPOINT':str(C2),'C2_SHA256':C2_SHA,'C2_FROZEN':True,'TRAINING_STARTED':False,'DORA_STARTED':False,'OFFICIAL_STL_MAIN_INPUT':False,'NEXT_STEP':'REPORT_AND_STOP' if len(clean)<18 else 'CADFS100_BUILD_ALLOWED'}
    dump(RUN/'CANARY20_REPORT.json',summary);(RUN/'CANARY20_REPORT.md').write_text('# CADFS Canary20 retry1 report\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n')
    # staged geometry evidence contains one row per attempted CAD.
    (OUT/'audits/CADFS_DSL_GEOMETRY_AUDIT_RETRY1.jsonl').write_text(''.join(json.dumps({'cad_id':r['cad_id'],'source_step_valid':r.get('SOURCE_STEP_PASS'),'dsl_step_valid':r.get('STEP_RELOAD_PASS'),'bbox_error':None,'chamfer_rel':r.get('chamfer_rel'),'coverage_02':r.get('coverage_02'),'DSL_GEOMETRY_PASS':r.get('DSL_GEOMETRY_PASS')})+'\n' for r in rows))
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
