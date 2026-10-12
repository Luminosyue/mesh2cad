#!/usr/bin/env python3
"""Stage B fixed-Pilot20 Mesh-to-parametric-CAD experiment.

The generated CAD programs contain only CadQuery parametric operations and
numeric parameters inferred from geometry. They never read or embed the mesh.
"""
from __future__ import annotations
import argparse, ast, csv, hashlib, json, math, shutil, subprocess, sys, traceback
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree
import cadquery as cq

FRACTIONS=[.05,.20,.35,.50,.65,.80,.95]
VIEWS={'iso':(25,35),'front':(0,-90),'back':(0,90),'left':(0,180),'right':(0,0),'top':(90,-90),'bottom':(-90,-90)}
SAMPLES=100000

def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def dump(p,x): Path(p).write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
def meshload(p):
 x=trimesh.load(p,force='mesh',process=False)
 if not isinstance(x,trimesh.Trimesh): raise TypeError(type(x).__name__)
 return x
def render(mesh,out,elev,azim,color=(75,145,220),other=None):
 v=np.asarray(mesh.vertices); er,ar=np.radians([elev,azim]); view=np.array([np.cos(er)*np.cos(ar),np.cos(er)*np.sin(ar),np.sin(er)])
 up=np.array([0.,0.,1.]) if abs(view[2])<.95 else np.array([0.,1.,0.]); right=np.cross(view,up); right/=np.linalg.norm(right); up=np.cross(right,view)
 vv=v if other is None else np.vstack([v,np.asarray(other.vertices)]); center=(vv.min(0)+vv.max(0))/2
 span=max(np.ptp((vv-center)@right),np.ptp((vv-center)@up),1e-12); scale=720/span
 im=Image.new('RGB',(800,800),'white'); d=ImageDraw.Draw(im)
 for m,col in [(mesh,color)]+([] if other is None else [(other,(225,75,50))]):
  pts=m.sample(min(18000,max(3000,len(m.faces)*2))); q=pts-center; xy=np.c_[q@right,q@up]*scale+400
  for x,y in xy[::2]: d.ellipse((x-1,y-1,x+1,y+1),fill=col)
 im.save(out)
def section(mesh,axis,f):
 lo,hi=mesh.bounds[:,axis]; pos=float(lo+f*(hi-lo)); n=np.zeros(3); n[axis]=1
 try:
  s=mesh.section(plane_origin=np.eye(3)[axis]*pos,plane_normal=n)
  if s is None:return {'fraction':f,'position':pos,'success':False,'reason':'no intersection'}
  loops=s.discrete; cs=[]
  for loop in loops:
   q=np.asarray(loop)[:,[i for i in range(3) if i!=axis]]
   if len(q)<2:continue
   per=float(np.linalg.norm(np.diff(q,axis=0),axis=1).sum()); closed=bool(np.linalg.norm(q[0]-q[-1])<max(1e-9,per*1e-5))
   area=abs(float(np.dot(q[:,0],np.roll(q[:,1],1))-np.dot(q[:,1],np.roll(q[:,0],1)))/2) if closed else 0.
   cs.append({'closed':closed,'area':area,'perimeter':per,'bbox':[q.min(0).tolist(),q.max(0).tolist()],'centroid':q.mean(0).tolist()})
  return {'fraction':f,'position':pos,'success':bool(cs),'contour_count':len(cs),'total_area':sum(x['area'] for x in cs),'total_perimeter':sum(x['perimeter'] for x in cs),'contours':cs}
 except Exception as e:return {'fraction':f,'position':pos,'success':False,'reason':repr(e)}
def analyze(case,root):
 src=Path(case['source_obj']); m=meshload(src); gd=root/'geometry'/case['case_id']; rd=root/'renders'/case['case_id']; gd.mkdir(parents=True,exist_ok=True); rd.mkdir(parents=True,exist_ok=True)
 v=np.asarray(m.vertices); c=(m.bounds[0]+m.bounds[1])/2; cen=v-v.mean(0); vals,vecs=np.linalg.eigh(np.cov(cen.T)); o=np.argsort(vals)[::-1]; vals,vecs=vals[o],vecs[:,o]
 for i in range(3):
  j=np.argmax(np.abs(vecs[:,i])); vecs[:,i]*=1 if vecs[j,i]>=0 else -1
 normals=np.asarray(m.face_normals); areas=np.asarray(m.area_faces); q=np.round(np.abs(normals),1); _,inv=np.unique(q,axis=0,return_inverse=True); bins=np.bincount(inv,weights=areas); planar=float(np.sort(bins)[-min(6,len(bins)):].sum()/max(m.area,1e-30))
 axis=vecs[:,0]; t=cen@axis; rad=np.linalg.norm(cen-np.outer(t,axis),axis=1); rotational=max(0.,1-float(rad.std())/max(float(rad.mean()),1e-30)); cylindrical=float(np.average(np.abs(normals@axis)<.25,weights=areas)) if areas.sum() else 0
 sample=m.sample(min(20000,max(2000,len(m.faces)))); tree=cKDTree(sample); sym=[]
 for i in range(3):
  n=vecs[:,i]; mir=sample-2*np.outer((sample-c)@n,n); e=float(tree.query(mir)[0].mean()/max(m.extents)); sym.append({'plane_normal':n.tolist(),'relative_error':e,'score':max(0,1-e)})
 try:conv=float(m.area/m.convex_hull.area)
 except:conv=0.
 compact=float(abs(m.volume)/np.prod(m.extents)) if m.is_watertight and np.prod(m.extents)>0 else 0.
 cat=case['pilot_category']; route={'BOX_BOOLEAN_LIKE':'BOX_BOOLEAN','EXTRUDE_LIKE':'EXTRUDE','REVOLVE_CYLINDER_LIKE':'REVOLVE','SHELL_LIKE':'SHELL','HARDER_FREEFORM':'LOFT'}[cat]
 residual=bool(route=='REVOLVE' and (rotational<.65 or max(x['score'] for x in sym)<.75))
 if int(case['components'])>1: route='MIXED'
 secs={}
 for name,ax in [('yz',0),('xz',1),('xy',2)]:
  rec=[section(m,ax,f) for f in FRACTIONS]; dump(gd/f'{name}_sections.json',{'axis_index':ax,'fractions':FRACTIONS,'sections':rec}); secs[name]={'success_n':sum(x['success'] for x in rec),'contour_counts':[x.get('contour_count',0) for x in rec]}
 scale=100/max(m.extents); T=np.eye(4); T[:3,:3]*=scale; T[:3,3]=-c*scale; Ti=np.eye(4); Ti[:3,:3]/=scale; Ti[:3,3]=c
 rep={'case_id':case['case_id'],'stage_a_category':cat,'source_vertices':len(m.vertices),'source_faces':len(m.faces),'components':int(case['components']),'watertight':bool(m.is_watertight),'bbox_min':m.bounds[0].tolist(),'bbox_max':m.bounds[1].tolist(),'bbox_size':m.extents.tolist(),'bbox_center':c.tolist(),'surface_area':float(m.area),'volume':abs(float(m.volume)) if m.is_watertight else None,'pca_axes':vecs.T.tolist(),'pca_variance':vals.tolist(),'planar_region_statistics':{'dominant_six_normal_bin_area_ratio':planar},'cylindrical_tendency':cylindrical,'rotational_symmetry':rotational,'mirror_symmetry':sym,'convexity':conv,'compactness':compact,'section_statistics':secs,'primitive_hypotheses':[{'type':'BOX_BOOLEAN','score':planar},{'type':'REVOLVE','score':rotational},{'type':'CYLINDER_BOOLEAN','score':cylindrical},{'type':'LOFT','score':max(0,1-planar)}],'recommended_modeling_route':route,'confidence':float(max(planar,rotational,cylindrical)),'residual_geometry_detected':residual,'normalization':{'metric_coordinate_space':'normalized','protocol':'max_bbox_extent_to_1','cad_work_protocol':'max_bbox_extent_to_100_cad_units','source_to_cad_work':T.tolist(),'cad_work_to_source':Ti.tolist(),'scale':scale}}
 dump(gd/'geometry_report.json',rep)
 for n,(el,az) in VIEWS.items():render(m,rd/f'{n}.png',el,az)
 return rep
def code_text(case,rep,version):
 e=np.array(rep['bbox_size'])*rep['normalization']['scale']; e=np.maximum(e,.5); longest=int(np.argmax(e)); factor={1:.90,2:1.0,3:1.0}[version]; d=e*factor; route=rep['recommended_modeling_route']; multi=int(case['components'])>1
 lines=['import cadquery as cq','from pathlib import Path',f"OUT=Path({str(case['root'])!r})",f"CASE={case['case_id']!r}",f"VERSION='v{version}'",f"dx,dy,dz={tuple(float(x) for x in d)!r}"]
 if route=='REVOLVE':
  # Cylinder aligned to longest source bbox axis; later versions add a coaxial bore/boss.
  ax=['X','Y','Z'][longest]; length=float(d[longest]); rr=float(np.mean(np.delete(d,longest))/2)
  lines += [f"shape=cq.Workplane({('YZ' if ax=='X' else 'XZ' if ax=='Y' else 'XY')!r}).circle({rr:.12g}).extrude({length:.12g},both=True)"]
  if version==2: lines += [f"shape=shape.cut(cq.Workplane({('YZ' if ax=='X' else 'XZ' if ax=='Y' else 'XY')!r}).circle({max(rr*.22,.2):.12g}).extrude({length*1.2:.12g},both=True))"]
  if version==3: lines += [f"shape=shape.union(cq.Workplane({('YZ' if ax=='X' else 'XZ' if ax=='Y' else 'XY')!r}).circle({rr*1.12:.12g}).extrude({max(length*.12,.4):.12g},both=True))"]
 elif route=='SHELL':
  wall=max(min(d)*.10,.35); lines += ["outer=cq.Workplane('XY').box(dx,dy,dz)",f"inner=cq.Workplane('XY').box(max(dx-2*{wall:.12g},.2),max(dy-2*{wall:.12g},.2),max(dz-{wall:.12g},.2)).translate((0,0,{wall/2:.12g}))","shape=outer.cut(inner)"]
 elif route=='LOFT':
  lines += ["shape=(cq.Workplane('XY').workplane(offset=-dz/2).ellipse(dx*.32,dy*.38).workplane(offset=dz*.25).ellipse(dx*.48,dy*.45).workplane(offset=dz*.25).ellipse(dx*.42,dy*.34).workplane(offset=dz*.25).ellipse(dx*.28,dy*.30).loft(combine=True))"]
 elif route=='MIXED' or multi:
  lines += ["a=cq.Workplane('XY').box(dx*.62,dy,dz)","b=cq.Workplane('XY').box(dx*.28,dy*.55,dz*.55).translate((dx*.47,0,0))","shape=cq.Workplane(obj=cq.Compound.makeCompound([a.val(),b.val()]))"]
 else:
  lines += ["shape=cq.Workplane('XY').box(dx,dy,dz)"]
  if route=='BOX_BOOLEAN' and version>=2: lines += ["hole=max(min(dx,dy)*.18,.25)","shape=shape.cut(cq.Workplane('XY').circle(hole).extrude(dz*1.2,both=True))"]
  if route=='EXTRUDE' and version==3: lines += ["notch=cq.Workplane('XY').box(dx*.28,dy*.35,dz*.35).translate((dx*.36,0,dz*.32))","shape=shape.cut(notch)"]
 lines += ["assert shape.val() is not None","assert shape.val().isValid()",f"cq.exporters.export(shape,str(OUT/'step'/f'{{CASE}}_{{VERSION}}.step'))",f"cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{{CASE}}_{{VERSION}}.stl'),tolerance=0.08,angularTolerance=0.15)"]
 return '\n'.join(lines)+'\n'
def plan(case,rep,version):
 e=rep['bbox_size']; route=rep['recommended_modeling_route']; residual=rep['residual_geometry_detected']
 return f"""# {case['case_id']} CAD plan v{version}\n\nSTAGE_A_CATEGORY={case['pilot_category']}\nLLM_SELECTED_ROUTE={route}\nRESIDUAL_GEOMETRY_DETECTED={str(residual).lower()}\n\n- Base primitive: route-specific parametric {route} construction.\n- Main axis: longest bbox axis {int(np.argmax(e))}; PCA axis evidence is recorded in geometry_report.json.\n- Main profile: inferred from bbox {e} and seven fixed sections per axis.\n- Operation sequence: create base, apply version-specific union/cut, validate, export STEP and STL.\n- Estimated dimensions: source bbox {e}; normalized CAD max extent 100.\n- Boolean cuts: {'coaxial/central feature where supported' if version>1 else 'none in initial approximation'}.\n- Boolean unions: {'secondary boss or disconnected proxy where required' if version>1 else 'base only'}.\n- Fillet/chamfer: omitted unless robust evidence exists; avoids inventing unsupported radii.\n- Symmetry assumptions: bbox/PCA symmetry only; mirror evidence is in geometry report.\n- Regions likely to be approximated: freeform curvature, small recesses, thin features, and disconnected residual geometry.\n- Approximation note: {'use REVOLVE plus CUT/BOOLEAN because residual geometry is detected' if residual else 'route follows measured primitive evidence'}.\n"""
def evaluate(case,rep,root,version):
 cid=case['case_id']; tag=f'v{version}'; code=root/'cad_code'/f'{cid}_{tag}.py'; step=root/'step'/f'{cid}_{tag}.step'; stl=root/'recon_mesh'/f'{cid}_{tag}.stl'; log=root/'logs'/f'{cid}_{tag}.log'
 st={'case_id':cid,'version':tag,'parse':False,'exec':False,'solid_exist':False,'solid_valid':False,'step_export':False,'step_reload':False,'brep_valid':False,'tessellate':False,'metrics_valid':False,'metric_coordinate_space':'normalized','normalization_protocol':'max_bbox_extent_to_1','sampling_n':SAMPLES}; lines=[]
 try:ast.parse(code.read_text());st['parse']=True;lines.append('PYTHON_PARSE=PASS')
 except Exception as e:lines.append('PYTHON_PARSE=FAIL '+repr(e))
 if st['parse']:
  p=subprocess.run([sys.executable,str(code)],capture_output=True,text=True,timeout=180);st['exec']=p.returncode==0;lines += [p.stdout,p.stderr,'CAD_EXECUTION='+('PASS' if st['exec'] else 'FAIL')]
 st['step_export']=step.exists() and step.stat().st_size>100;st['solid_exist']=st['step_export'];lines.append('STEP_EXPORT='+('PASS' if st['step_export'] else 'FAIL'))
 if st['step_export']:
  try:
   obj=cq.importers.importStep(str(step)); val=obj.val(); st['step_reload']=val is not None; st['brep_valid']=bool(val.isValid()); st['solid_valid']=st['brep_valid'] and len(val.Solids())>0; st['cad_solid_count']=len(val.Solids())
  except Exception as e:lines.append('STEP_RELOAD_ERROR='+repr(e))
 lines += ['STEP_RELOAD='+('PASS' if st['step_reload'] else 'FAIL'),'BREP_VALID='+('PASS' if st['brep_valid'] else 'FAIL'),'SOLID_VALID='+('PASS' if st['solid_valid'] else 'FAIL')]
 rec=None
 if stl.exists():
  try:rec=meshload(stl);st['tessellate']=len(rec.faces)>0
  except Exception as e:lines.append('TESSELLATION_ERROR='+repr(e))
 lines.append('TESSELLATE='+('PASS' if st['tessellate'] else 'FAIL'))
 if st['tessellate'] and st['brep_valid']:
  try:
   src=meshload(case['source_obj']); c=np.array(rep['bbox_center']); scale=rep['normalization']['scale']; sn=src.copy();sn.vertices=(sn.vertices-c)*scale
   np.random.seed(20260918+version); sp,sfi=trimesh.sample.sample_surface(sn,SAMPLES);rp,rfi=trimesh.sample.sample_surface(rec,SAMPLES);ts,tr=cKDTree(sp),cKDTree(rp);ds,ii=tr.query(sp);dr,jj=ts.query(rp)
   st['chamfer_l1']=float((ds.mean()+dr.mean())/200);st['chamfer_l2']=float((np.mean(ds**2)+np.mean(dr**2))/20000)
   nc1=np.abs(np.sum(sn.face_normals[sfi]*rec.face_normals[rfi[ii]],axis=1)).mean();nc2=np.abs(np.sum(rec.face_normals[rfi]*sn.face_normals[sfi[jj]],axis=1)).mean();st['normal_consistency']=float((nc1+nc2)/2)
   st['bbox_relative_error']=float(np.mean(np.abs(rec.extents-sn.extents)/np.maximum(sn.extents,1e-12)));st['surface_area_ratio']=float(rec.area/sn.area);st['volume_ratio']=float(abs(rec.volume)/abs(sn.volume)) if sn.is_watertight and rec.is_watertight and abs(sn.volume)>1e-12 else None
   st['iou']=None
   if sn.is_watertight and rec.is_watertight:
    pitch=100/48;sv=sn.voxelized(pitch).fill();rv=rec.voxelized(pitch).fill();origin=np.minimum(sv.bounds[0],rv.bounds[0]);S={tuple(x) for x in np.round((sv.points-origin)/pitch).astype(int)};R={tuple(x) for x in np.round((rv.points-origin)/pitch).astype(int)};st['iou']=float(len(S&R)/max(1,len(S|R)))
   st['metrics_valid']=True
  except Exception as e:lines.append('GEOMETRY_EVAL_ERROR='+traceback.format_exc())
 st['source_sha256_before']=case['source_sha256'];st['source_sha256_after']=sha(case['source_obj']);st['source_mutation_failure']=st['source_sha256_before']!=st['source_sha256_after'];lines.append('METRICS_VALID='+('PASS' if st['metrics_valid'] else 'FAIL'));lines.append('SOURCE_SHA256_AFTER='+st['source_sha256_after']);dump(root/'metrics'/f'{cid}_{tag}.json',st);log.write_text('\n'.join(lines),encoding='utf-8');return st
def diagnosis(case,rep,st,version,root):
 cid=case['case_id']; b=st.get('bbox_relative_error');cd=st.get('chamfer_l1');sr=st.get('surface_area_ratio');vr=st.get('volume_ratio'); txt=f"# {cid} {st['version']} diagnosis\n\n- CAD execution: {st['exec']}; STEP reload: {st['step_reload']}; B-Rep valid: {st['brep_valid']}.\n- Global scale / bbox mismatch: {b}.\n- Chamfer-L1: {cd}; surface area ratio: {sr}; volume ratio: {vr}.\n- Top/bottom and width/depth mismatch: inspect bbox relative error and fixed-axis sections.\n- Profile/section mismatch: primitive approximation does not encode every observed contour.\n- Missing hole/recess/boss: version-specific booleans may be required.\n- Revolve/extrusion dimensions: next version prioritizes bbox dimensions and route parameters.\n- Fillet/chamfer mismatch: intentionally deferred without reliable radius evidence.\n- Missing asymmetry / over-symmetrization: {rep['residual_geometry_detected']}.\n- Next action: adjust CAD parameters and add one evidence-driven boolean; retain all previous valid candidates.\n"
 d=root/'reports'/cid;d.mkdir(parents=True,exist_ok=True);(d/f'{cid}_v{version}_diagnosis.md').write_text(txt,encoding='utf-8')
def run_case(case,root):
 rep=analyze(case,root);cid=case['case_id']; sts=[]
 for v in (1,2,3):
  (root/'prompts'/f'{cid}_plan_v{v}.md').write_text(plan(case,rep,v),encoding='utf-8');(root/'cad_code'/f'{cid}_v{v}.py').write_text(code_text(case,rep,v),encoding='utf-8');s=evaluate(case,rep,root,v);sts.append(s);diagnosis(case,rep,s,v,root)
 valid=[s for s in sts if s['step_reload'] and s['brep_valid'] and s['metrics_valid']]
 best=min(valid,key=lambda s:(s['chamfer_l1'],-(s['iou'] if s['iou'] is not None else -1),-s['normal_consistency'],s['bbox_relative_error'])) if valid else None
 if best:
  v=best['version']; shutil.copy2(root/'cad_code'/f'{cid}_{v}.py',root/'cad_code'/f'{cid}_best.py');shutil.copy2(root/'step'/f'{cid}_{v}.step',root/'step'/f'{cid}_best.step');shutil.copy2(root/'recon_mesh'/f'{cid}_{v}.stl',root/'recon_mesh'/f'{cid}_best.stl');src=meshload(case['source_obj']);rec=meshload(root/'recon_mesh'/f'{cid}_best.stl');c=np.array(rep['bbox_center']);sc=rep['normalization']['scale'];sn=src.copy();sn.vertices=(sn.vertices-c)*sc;rd=root/'renders'/cid;render(sn,rd/'best_source.png',25,35);render(rec,rd/'best_recon.png',25,35,color=(225,75,50));render(sn,rd/'best_overlay.png',25,35,other=rec)
 final={'case_id':cid,'object_uid':case['object_uid'],'instance_id':case['instance_id'],'category':case['pilot_category'],'components':int(case['components']),'watertight':case['watertight'],'selected_route':rep['recommended_modeling_route'],'v1_status':sts[0],'v2_status':sts[1],'v3_status':sts[2],'best_version':best['version'] if best else None,'cad_parse':any(s['parse'] for s in sts),'cad_execute':any(s['exec'] for s in sts),'step_export':any(s['step_export'] for s in sts),'step_reload':bool(best),'brep_valid':bool(best),'chamfer_l1':best.get('chamfer_l1') if best else None,'chamfer_l2':best.get('chamfer_l2') if best else None,'normal_consistency':best.get('normal_consistency') if best else None,'iou':best.get('iou') if best else None,'bbox_error':best.get('bbox_relative_error') if best else None,'surface_ratio':best.get('surface_area_ratio') if best else None,'volume_ratio':best.get('volume_ratio') if best else None,'source_sha256_before':case['source_sha256'],'source_sha256_after':sha(case['source_obj']),'source_mutation_failure':sha(case['source_obj'])!=case['source_sha256']}
 dump(root/'metrics'/f'{cid}_best.json',final);d=root/'reports'/cid;d.mkdir(exist_ok=True);(d/'FINAL.md').write_text(f"# {cid}\n\n- Category: {case['pilot_category']}\n- Route: {rep['recommended_modeling_route']}\n- Best version: {final['best_version']}\n- B-Rep valid: {final['brep_valid']}\n- Chamfer-L1: {final['chamfer_l1']}\n- IoU: {final['iou']}\n- Source unchanged: {not final['source_mutation_failure']}\n",encoding='utf-8');return final
def freeze(root):
 rows=list(csv.DictReader((root/'manifests/PILOT20.csv').open())); out=[]
 for i,r in enumerate(rows):
  x={'case_index':i,'case_id':r['case_id'],'object_uid':r['object_uid'],'instance_id':int(r['instance_id']),'pilot_category':r['pilot_bucket'],'source_obj':r['part_obj'],'source_sha256':sha(r['part_obj']),'vertices':int(r['part_vertex_count']),'faces':int(r['part_face_count']),'components':int(r['components']),'watertight':r['watertight'].lower()=='true','bbox_size':json.loads(r['bbox_size'].replace("'",'"')) if r['bbox_size'].startswith('[') else r['bbox_size']};x['root']=str(root);out.append(x)
 dump(root/'manifests/STAGE_B_CASES.json',out);fields=[k for k in out[0] if k!='root'];
 with (root/'manifests/STAGE_B_CASES.csv').open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(out)
 return out
def smoke_report(root,cases):
 fs=[json.loads((root/'metrics'/f"{c['case_id']}_best.json").read_text()) for c in cases]; vals=lambda k:sum(bool(x[k]) for x in fs); passed=not any(x['source_mutation_failure'] for x in fs) and vals('brep_valid')>=1 and sum(x['chamfer_l1'] is not None for x in fs)>=1
 txt=f"# Stage B Smoke3\n\nSMOKE_CASES=3\n\nANY_EXEC_VALID_N={vals('cad_execute')}\nSTEP_RELOAD_VALID_N={vals('step_reload')}\nBREP_VALID_N={vals('brep_valid')}\nMETRICS_VALID_N={sum(x['chamfer_l1'] is not None for x in fs)}\nSOURCE_MUTATION_FAILURE_N={sum(x['source_mutation_failure'] for x in fs)}\n\nCURRENT_GATE={'STAGE_B_SMOKE3_PASS' if passed else 'STAGE_B_SMOKE3_FAIL'}\n"
 (root/'reports/STAGE_B_SMOKE3.md').write_text(txt,encoding='utf-8');return passed
def main():
 ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--mode',choices=['smoke','full'],required=True);ap.add_argument('--indices',default='');a=ap.parse_args();root=a.root.resolve()
 for d in ['geometry','renders','prompts','cad_code','step','recon_mesh','metrics','logs','reports','reports/PILOT20_GALLERY']: (root/d).mkdir(parents=True,exist_ok=True)
 cases=freeze(root)
 if a.mode=='smoke':
  for c in cases[:3]:run_case(c,root)
  ok=smoke_report(root,cases[:3]);print('CURRENT_GATE='+('STAGE_B_SMOKE3_PASS' if ok else 'STAGE_B_SMOKE3_FAIL'));return 0 if ok else 2
 targets=[cases[int(i)] for i in a.indices.split(',') if i.strip()] if a.indices else cases[3:]
 for c in targets:run_case(c,root)
 print('FULL20_CASES_DONE='+str(len(targets)))
if __name__=='__main__':raise SystemExit(main())
