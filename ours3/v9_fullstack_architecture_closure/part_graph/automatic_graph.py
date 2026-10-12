from pathlib import Path
import numpy as np,trimesh
def _gap(a,b):
 amin,amax=a.bounds;bmin,bmax=b.bounds;d=np.maximum(np.maximum(amin-bmax,bmin-amax),0);return float(np.linalg.norm(d))
def pair_score(a,b):
 ea,eb=np.asarray(a.extents),np.asarray(b.extents);ca,cb=np.asarray(a.centroid),np.asarray(b.centroid);area=min(a.area,b.area)/max(a.area,b.area);shape=float(np.exp(-np.linalg.norm(np.sort(ea)/max(np.linalg.norm(ea),1e-9)-np.sort(eb)/max(np.linalg.norm(eb),1e-9))*4));gap=_gap(a,b);scale=max(np.linalg.norm(ea),np.linalg.norm(eb));contact=float(np.exp(-gap/max(scale*.15,1e-9)));small=float(max(a.area,b.area)<.08);score=.35*area+.25*shape+.25*contact+.15*small;return score,{'area_similarity':area,'shape_similarity':shape,'bbox_gap':gap,'contact_score':contact,'small_fragment_pair':bool(small)}
def build_automatic_part_graph(p3_dir,out_dir,threshold=.65):
 p3_dir,out_dir=Path(p3_dir),Path(out_dir);meshes=[trimesh.load(p,force='mesh',process=False) for p in sorted(p3_dir.glob('part_*.obj'))];pairs=[]
 for i in range(len(meshes)):
  for j in range(i+1,len(meshes)):
   s,e=pair_score(meshes[i],meshes[j]);pairs.append({'segments':[i,j],'score':s,**e,'decision':'AUTO_MERGE' if s>=threshold and e['small_fragment_pair'] and e['contact_score']>.9 else 'KEEP_SEPARATE'})
 parent=list(range(len(meshes)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def union(a,b):
  a,b=find(a),find(b)
  if a!=b:parent[b]=a
 for p in sorted(pairs,key=lambda x:-x['score']):
  if p['decision']=='AUTO_MERGE':union(*p['segments'])
 groups={}
 for i in range(len(meshes)):groups.setdefault(find(i),[]).append(i)
 nodes=[];out_dir.mkdir(parents=True,exist_ok=True)
 for k,ids in enumerate(sorted(groups.values(),key=lambda x:min(x))):
  mesh=trimesh.util.concatenate([meshes[i] for i in ids]);path=out_dir/f'AUTO_PART_{k:03d}/source_part.obj';path.parent.mkdir(parents=True,exist_ok=True);mesh.export(path);nodes.append({'part_id':f'AUTO_PART_{k:03d}','segments':ids,'source_mesh':str(path),'triangle_count':len(mesh.faces),'surface_area':float(mesh.area),'bbox_min':mesh.bounds[0].tolist(),'bbox_max':mesh.bounds[1].tolist(),'centroid':mesh.centroid.tolist(),'component_count':len(mesh.split(only_watertight=False)),'coordinate_frame':'SOURCE_GLOBAL','T_part_to_source':np.eye(4).tolist()})
 central=max(nodes,key=lambda n:n['surface_area']);hierarchy={'root':'ROOT_ASSEMBLY','central_part':central['part_id'],'children':[n['part_id'] for n in nodes],'inference':'GEOMETRIC_AREA_CENTRALITY_AND_ATTACHMENT','status':'PARTIAL'}
 return {'schema':'AutomaticCADPartGraphV9','p3_segment_count':len(meshes),'cad_part_count':len(nodes),'automatic_part_merge_used':True,'merge_threshold':threshold,'merge_decisions':pairs,'nodes':nodes,'hierarchy':hierarchy,'localization_used':False,'transform_restore_effective':False,'gt_semantic_labels_used':False,'old_part_specs_used':False}
