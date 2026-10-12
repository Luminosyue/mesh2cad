#!/usr/bin/env python3
"""Isolated V3 asset replay for frozen Canary20; never writes legacy roots."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); OUT=ROOT/'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/canary20'; MAN=OUT/'CANARY20_MANIFEST.json'
sys.path.insert(0,str(ROOT/'scripts'))
from geometry_pack_v1 import pack
import curve_token_v1.build_dataset as curves
import spatiallm_curve_token_c2_frozen_v2.export_curve_tokens as exporter

CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'; C2SHA='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
def fsha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def cad_exec(dsl,work):
 r={'parse':False,'exec':False,'step_write':False,'step_reload':False,'error_short':''}
 try:
  spec=importlib.util.spec_from_file_location('canary_cad_dsl',ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
  code=m.extract_dsl_code(dsl);m.parse_dsl(code);r['parse']=True
  import cadquery as cq
  step=work/'gt_replay.step';stl=work/'gt_replay.stl';m.execute_dsl(code,step,stl);r['exec']=True;r['step_write']=step.is_file() and stl.is_file()
  if r['step_write']:cq.importers.importStep(str(step));r['step_reload']=True
 except Exception as e:r['error_short']=(type(e).__name__+': '+str(e))[-500:]
 return r
def main():
 d=json.loads(MAN.read_text()); assert fsha(CKPT)==C2SHA
 # Old curve builder is called directly but only its output-root function is redirected.
 old_cad_dir=curves.cad_dir; old_packs={k:v['track_a_pack'] for k,v in curves.SPLITS.items()}; old_packroot=dict(exporter.PACK_ROOT)
 device='cuda:1'; model,_=exporter.load_backbone(CKPT,__import__('torch').device(device)); rows=[]
 try:
  for rec in d['records']:
   ds=rec['dataset']; sid=rec['source_id']; split='deepcad_train' if ds=='DeepCAD' else 'fusion360_train'; low='deepcad' if ds=='DeepCAD' else 'fusion360'; base=OUT/ds/sid; gp=base/'geometry_pack_v1'/sid; cd=base/'curve_data'; base.mkdir(parents=True,exist_ok=False)
   x={'cad_id':rec['cad_id'],'dataset':ds,'source_pass':False,'mesh_pass':False,'surface_pass':False,'dsl_parse':False,'dsl_exec':False,'step_write':False,'step_reload':False,'curve_count':0,'c2_valid':False,'clean_status':'CLEAN_REJECT','primary_reject_reason':None,'secondary_reject_reasons':[]}
   try:
    src=Path(rec['source_path']); step=src/'model.step'; x['source_pass']=step.is_file() and fsha(step)==rec['source_step_sha256']
    (base/'SOURCE_PROVENANCE.json').write_text(json.dumps({'source_path':str(src),'source_step':str(step),'source_sha256':fsha(step),'build_scripts':['geometry_pack_v1.pack.build_one','curve_token_v1.build_dataset.build_one','spatiallm_curve_token_c2_frozen_v2.export_curve_tokens.process_cad']},indent=2)+'\n')
    if not x['source_pass']:raise RuntimeError('REJECT_SOURCE_LOAD')
    pack.build_one(src,gp.parent,overwrite=False); mesh=np.load(gp/'surface_points.npy'); x['mesh_pass']=(gp/'mesh.obj').is_file(); x['surface_pass']=mesh.shape==(8192,6) and bool(np.isfinite(mesh).all()) and bool(np.allclose(np.linalg.norm(mesh[:,3:],axis=1),1,atol=1e-4)); x['surface_shape']=list(mesh.shape);x['surface_normal_min']=float(np.linalg.norm(mesh[:,3:],axis=1).min());x['surface_normal_max']=float(np.linalg.norm(mesh[:,3:],axis=1).max())
    raw=np.load(gp/'surface_points_source.npy'); tf=json.loads((gp/'coordinate_transform.json').read_text()); x['surface_transform_error']=float(np.abs(raw*float(tf['scale'])+np.asarray(tf['translation'])-mesh[:,:3]).max())
    if not x['mesh_pass']:raise RuntimeError('REJECT_MESH_TESSELLATION')
    if not x['surface_pass']:raise RuntimeError('REJECT_SURFACE')
    dsl=(gp/'cad_target.dsl').read_text(); ce=cad_exec(dsl,base);x.update({'dsl_parse':ce['parse'],'dsl_exec':ce['exec'],'step_write':ce['step_write'],'step_reload':ce['step_reload'],'dsl_error_short':ce['error_short'],'dsl_chars':len(dsl)})
    if not x['step_reload']:raise RuntimeError('REJECT_DSL_OR_STEP')
    curves.cad_dir=lambda _split,_sid:cd; curves.SPLITS[split]['track_a_pack']=gp.parent; cr=curves.build_one(split,sid,overwrite=False); 
    if not cr.get('ok'):raise RuntimeError('REJECT_GT_CURVE:'+str(cr.get('error')))
    z=np.load(cd/'curve_samples.npz');x['curve_count']=int(z['num_curves'][0]);x['curve_sample_shape']=list(z['curve_xyz_normalized'].shape);x['curve_finite']=bool(np.isfinite(z['curve_xyz_normalized']).all() and np.isfinite(z['curve_tangent']).all())
    exporter.PACK_ROOT[low]=gp.parent; res=exporter.process_cad(low,sid,cd,model,__import__('torch').device(device),True)
    if res is None:raise RuntimeError('REJECT_C2_NO_SHARP_CURVE')
    c2=base/'curve_tokens';c2.mkdir();np.save(c2/'curve_tokens.npy',res['tokens']);(c2/'curve_tokens_meta.json').write_text(json.dumps(res['meta'],indent=2)+'\n');x['c2_valid']=bool(np.isfinite(res['tokens']).all() and res['tokens'].ndim==2 and res['tokens'].shape[1]==256);x['curve_type_histogram']=res['meta']['type_counts']
    if not x['c2_valid']:raise RuntimeError('REJECT_C2')
    x['clean_status']='PARTIAL_PASS_REQUIRES_V3_SUMMARY_CONTEXT_AND_SPLICE';x['primary_reject_reason']=None
   except Exception as e:x['primary_reject_reason']=str(e)
   (base/'PER_CAD_AUDIT.json').write_text(json.dumps(x,indent=2)+'\n');rows.append(x);print(rec['cad_id'],x['clean_status'],x['primary_reject_reason'],flush=True)
 finally:
  curves.cad_dir=old_cad_dir
  for k,v in old_packs.items():curves.SPLITS[k]['track_a_pack']=v
  exporter.PACK_ROOT.update(old_packroot)
 (OUT/'CANARY20_PER_CAD_PHASEA.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows));print(json.dumps({'attempted':len(rows),'phaseA_asset_pass':sum(x['clean_status'].startswith('PARTIAL') for x in rows)},indent=2))
if __name__=='__main__':main()
