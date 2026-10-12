import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import json,sys,argparse
from pathlib import Path
import numpy as np,trimesh
from fit_logic import candidate_axes,basis_for_axis
O=Path(__file__).resolve().parents[1]
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False))
def feature(r):
 d=O/'objects'/r['parent_object_id']/'parts'/r['part_id'];d.mkdir(exist_ok=True)
 for s in ['source','features','planner','candidates','cad','metrics','logs']:(d/s).mkdir(exist_ok=True)
 m=trimesh.load(r['part_mesh_path'],force='mesh',process=True);m.apply_transform(np.asarray(r['local_transform']));m.export(d/'source/part_local.ply');m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True)
 axes=candidate_axes(m);evidence=[];v=np.asarray(m.vertices);areas=m.area_faces;normals=m.face_normals
 for a in axes:
  B=basis_for_axis(a);q=v@B;lo=q.min(0);hi=q.max(0);xy=q[:,:2];A=np.column_stack([2*xy,np.ones(len(xy))]);solution=np.linalg.lstsq(A,(xy*xy).sum(1),rcond=None)[0];c=solution[:2];rad=np.linalg.norm(xy-c,axis=1);radius=float(np.median(rad));radres=float(np.median(np.abs(rad-radius))/max(radius,1e-9));cap=float(areas[np.abs(normals@a)>.97].sum()/areas.sum());side=float(areas[np.abs(normals@a)<.15].sum()/areas.sum())
  sections=[]
  for f in [.15,.35,.5,.65,.85]:
   z=float(lo[2]+f*(hi[2]-lo[2]));s=m.section(plane_origin=B[:,2]*z,plane_normal=B[:,2]);closed=0;loops=[]
   if s is not None:
    for pts in s.discrete:
     closed+=int(np.linalg.norm(pts[0]-pts[-1])<1e-5);loops.append(len(pts))
   sections.append({'fraction':f,'loop_n':len(loops),'closed_loop_n':closed})
  evidence.append({'axis':a.tolist(),'basis':B.tolist(),'lo':lo.tolist(),'hi':hi.tolist(),'circle_center':c.tolist(),'radius_median':radius,'radial_relative_mad':radres,'cap_area_fraction':cap,'side_area_fraction':side,'sections':sections})
 bins=np.round(normals/.08).astype(int);_,inv=np.unique(bins,axis=0,return_inverse=True);weights=np.bincount(inv,weights=areas);plane=float(np.sort(weights)[-6:].sum()/areas.sum())
 best=min(evidence,key=lambda x:x['radial_relative_mad']);_,sv,vh=np.linalg.svd(v-v.mean(0),full_matrices=False);ext=np.ptp(v@vh.T,axis=0)
 rec=dict(r,canonical_bbox=m.bounds.tolist(),canonical_centroid=m.centroid.tolist(),principal_axes=vh.tolist(),principal_extents=ext.tolist(),aspect_ratios=(ext/max(ext)).tolist(),dominant_six_normal_bin_area_fraction=plane,
  axis_evidence=evidence,best_radial_axis_index=evidence.index(best),radial_evidence=best['radial_relative_mad'],
  holes_evidence='multiple nested closed sections require contour inspection; no blind hole assertion',protrusions_evidence='local section changes retained in section counts',repeated_features='NOT_INFERRED',
  local_mesh_path=str(d/'source/part_local.ply'))
 dump(d/'features/features.json',rec)
 return {'key':r['parent_object_id']+'/'+r['part_id'],'faces':r['face_count'],'size':r['size_class'],'components':r['connected_components'],'watertight':r['watertight'],
  'plane':round(plane,3),'aspect':[round(float(x),3) for x in ext/max(ext)],'radial':round(best['radial_relative_mad'],3),'best_axis':evidence.index(best),
  'section_loops':[s['closed_loop_n'] for s in best['sections']]}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,required=True);a=ap.parse_args();summ=[]
 for obj in json.loads((O/'manifests/objects_frozen.json').read_text())[:a.limit]:
  p=O/'objects'/obj['object_id']/'p3/parts_manifest.json'
  if not p.exists():continue
  for r in json.loads(p.read_text())['parts']:
   if r['size_class']=='MICRO_PART' or r['part_quality']=='DEGENERATE':continue
   f=O/'objects'/r['parent_object_id']/'parts'/r['part_id']/'features/summary.json'
   if f.exists():s=json.loads(f.read_text())
   else:s=feature(r);dump(f,s)
   summ.append(s);print(json.dumps(s),flush=True)
 dump(O/'manifests'/f'feature_summaries_{a.limit}.json',summ)
