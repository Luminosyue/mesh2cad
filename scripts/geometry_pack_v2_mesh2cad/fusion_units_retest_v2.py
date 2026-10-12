"""V2-only unit correction and frozen-threshold label audit; no model operations."""
import pathlib,json,sys,os,hashlib,time,subprocess,concurrent.futures,argparse
import numpy as np
from fusion_units_probe import R,B,O,save,step,bounds,ratio
O=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v2'
from fusion_unit_contract import transform
sys.path[:0]=[str(R/'scripts'),str(R/'scripts/deepcad')]
INV=[r for r in json.loads((B/'inventory.json').read_text()) if r['dataset']=='fusion360']
TIMEOUT_ID='fusion360__23658_c75a430c_0000'
def digest(p):
 h=hashlib.sha256()
 with pathlib.Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def frozen(tag):
 refs=json.loads((B/'V1_FROZEN_SHA256.json').read_text());changed=[p for p,h in refs.items() if not pathlib.Path(p).is_file() or digest(p)!=h]
 save(O/(tag+'_v1_hashes.json'),dict(checked=len(refs),changed=changed,passed=not changed))
 if changed:raise RuntimeError('V1 frozen input changed')
def textnew(p,s):
 with p.open('x') as f:f.write(s)
def mesh(p):
 from geometry_pack_v1.occ import load_step_shape,tessellate_shape,triangulation_to_arrays
 shape=load_step_shape(p);tessellate_shape(shape);v,f=triangulation_to_arrays(shape)
 if not len(f):raise ValueError('empty triangulation')
 return v,f
def worker(i):
 from cad_canonical import load_transform_json,transform_dsl
 from edge_aware_cad_planner_v1.cad_dsl import parse_dsl,execute_dsl
 from geometry_pack_v1.surface import sample_surface_uniform
 from scipy.spatial import cKDTree
 rec=INV[i];d=O/'samples'/rec['cad_id'];d.mkdir(parents=True,exist_ok=False)
 ans=dict(rec,parsed=False,execution_ok=False,step_reload=False,label_gate=False,index=i);stage='source';t=time.time()
 try:
  src=step(rec['source_step']);ans['source_geometry']=src
  # This mapping is unit metadata, not a fit to geometric errors.
  units=src['file_units']
  if units!=['centimetre'] or src['reader_unit']!='MM':raise ValueError('unexpected unit metadata; manual review required')
  factor=10.;pack=pathlib.Path(rec['pack']);oldtf=load_transform_json(pack/'coordinate_transform.json')
  stage='inverse_old_transform';old=(pack/'cad_target.dsl').read_text();textnew(d/'cad_target_v1_unchanged.dsl',old)
  before=transform_dsl(old,oldtf,inverse=True);textnew(d/'cad_target_before_units.dsl',before)
  stage='unit_conversion';fixed=transform(before,factor);textnew(d/'cad_target_mm.dsl',fixed)
  scale=6./src['diag'];translation=(-np.array(src['min'])*scale).tolist()
  contract=dict(source_step_unit='cm',source_step_reader_unit='mm',legacy_dsl_length_unit='cm',dsl_length_unit='mm',canonical_coordinate_unit='normalized',source_to_canonical_scale=scale,dsl_to_canonical_scale=scale,source_file_numeric_to_canonical_scale=factor*scale,unit_fix_applied=True,unit_fix_factor=factor,unit_evidence='STEP FileUnits=centimetre; OCP target=MM; legacy DSL/official OBJ use native cm numeric coordinates; 20-row audit shows additional non-unit shape errors',source_step_sha256=digest(rec['source_step']),v1_dsl_sha256=digest(pack/'cad_target.dsl'),inverse_transform_precision='same legacy 6-decimal inverse as baseline; no new rounding in unit converter',canonical_translation=translation,axes_rotated=False,directions_scaled=False,augmentation=False,curve_inputs_built=False)
  save(d/'unit_contract.json',contract)
  save(d/'coordinate_transform.json',dict(source_bbox_min=src['min'],source_bbox_max=src['max'],source_diagonal=src['diag'],target_diagonal=6.,scale=scale,translation=translation,source_coordinate_unit='mm'))
  textnew(d/'cad_target.dsl',transform(fixed,scale,translation))
  # Preserve all 8192 source surface samples and row order; rotate/translate no normals.
  xyz=np.load(pack/'surface_points_source.npy');surf=np.load(pack/'surface_points.npy')
  if xyz.shape!=(8192,3) or surf.shape!=(8192,6):raise ValueError('unexpected stored surface schema')
  surface=surf.copy();surface[:,:3]=xyz*scale+np.array(translation)
  norms=np.linalg.norm(surface[:,3:6],axis=1)
  if not np.allclose(norms,1,atol=1e-5):raise ValueError('source normals not unit')
  with (d/'surface_points.npy').open('xb') as f:np.save(f,surface)
  ans['surface_shape']=list(surface.shape);ans['surface_row_order_preserved']=True
  ans['surface_bbox_after']=bounds(surface[:,:3]);ans['surface_bbox_before']=bounds(np.load(pack/'surface_points.npy')[:,:3])
  stage='parse';parse_dsl(fixed);ans['parsed']=True
  stage='execute';execute_dsl(fixed,d/'reconstructed.step');ans['execution_ok']=True
  stage='reload';pred=step(d/'reconstructed.step');ans['replay_geometry']=pred;ans['scale_ratios']=ratio(pred,src)
  vg,fg=mesh(pathlib.Path(rec['source_step']));vp,fp=mesh(d/'reconstructed.step');ans['step_reload']=True
  stage='geometry';diag=float(np.linalg.norm(vg.max(0)-vg.min(0)));seed=int(hashlib.sha256(rec['cad_id'].encode()).hexdigest()[:8],16)
  a,_,_=sample_surface_uniform(vg,fg,20000,seed);b,_,_=sample_surface_uniform(vp,fp,20000,seed^0x5A5A5A5A)
  ab=cKDTree(b).query(a,workers=1)[0]/diag;ba=cKDTree(a).query(b,workers=1)[0]/diag
  ch=float((ab.mean()+ba.mean())/2);cov=float((ab<=.02).mean())
  ans.update(chamfer_rel=ch,coverage_02=cov,chamfer_pass=ch<=.01,coverage_pass=cov>=.98,gt_bbox_diag=diag,bbox_extent_ratio=((vp.max(0)-vp.min(0))/np.maximum(vg.max(0)-vg.min(0),1e-12)).tolist(),bbox_diag_ratio=float(np.linalg.norm(vp.max(0)-vp.min(0))/diag))
  ans['label_gate']=bool(ch<=.01 and cov>=.98 and surf.shape==(8192,6) and rec['manifest_matches_pack'])
  if not ans['label_gate']:ans['failure_stage']='geometry_threshold';ans['error']='Residual shape mismatch after metadata-derived unit correction; no further scale fitting permitted'
 except Exception as e:ans.update(failure_stage=stage,error=repr(e))
 ans['elapsed_s']=time.time()-t;save(d/'audit.json',ans)
def launch(i):
 rec=INV[i];timeout=600 if rec['cad_id']==TIMEOUT_ID else 150
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1')
 log=O/'logs'/(rec['cad_id']+'.log');log.parent.mkdir(exist_ok=True)
 with log.open('x') as f:
  try:p=subprocess.run([sys.executable,'-B',__file__,'--worker',str(i)],env=env,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
  except subprocess.TimeoutExpired:return dict(rec,index=i,failure_stage='timeout',timeout_s=timeout,label_gate=None,execution_ok=None,step_reload=None,error='Timeout: geometric validity unknown; not counted as geometry failure')
 pth=O/'samples'/rec['cad_id']/'audit.json'
 if pth.exists():return dict(json.loads(pth.read_text()),timeout_s=timeout)
 return dict(rec,index=i,failure_stage='worker_exit',returncode=p.returncode,label_gate=None)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--worker',type=int);args=ap.parse_args()
 if args.worker is not None:return worker(args.worker)
 frozen('before');save(O/'fusion_inventory.json',INV);rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=24) as pool:
  for f in concurrent.futures.as_completed([pool.submit(launch,i) for i in range(len(INV))]):
   rows.append(f.result())
   if len(rows)%25==0 or len(rows)==len(INV):print(json.dumps(dict(completed=len(rows),total=len(INV),label_pass=sum(r.get('label_gate') is True for r in rows))),flush=True)
 save(O/'results602.json',sorted(rows,key=lambda r:r['index']));frozen('after')
 print('COMPLETED_NO_TRAINING',flush=True)
if __name__=='__main__':main()
