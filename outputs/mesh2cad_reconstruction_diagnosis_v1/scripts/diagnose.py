import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json,ast,csv,collections,sys
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');D=O/'mesh2cad_reconstruction_diagnosis_v1';OLD=O/'mesh2cad_data_factory_v1_smoke100'
def write(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False))
def csvout(p,rows):
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows])
def describe(m):
 v=np.asarray(m.vertices);c=v.mean(0);_,sv,vh=np.linalg.svd(v-c,full_matrices=False);local=(v-c)@vh.T;ext=np.ptp(local,axis=0)
 normals=m.face_normals;area=m.area_faces;groups=[]
 for j in np.argsort(-area):
  n=normals[j]
  if not any(abs(np.dot(n,a))>.995 for a in groups):groups.append(n)
 dot=np.abs(normals@vh[2]); parallel_area=float(area[dot>.995].sum()/max(area.sum(),1e-12))
 planar=bool(ext[2]/max(ext[0],1e-12)<1e-5)
 if planar:family='B_EXTRUSION_LIKE';conf=.96;reason='planar contour; solid thickness not observed'
 elif len(m.split(only_watertight=False))>1:family='E_MULTI_PRIMITIVE_ASSEMBLY';conf=.65;reason='multiple disconnected components'
 elif len(groups)<=3 and m.is_watertight:family='A_SINGLE_PRIMITIVE';conf=.75;reason='closed mesh with <=3 unoriented planar normal groups'
 elif len(groups)<=6 or parallel_area>.6:family='B_EXTRUSION_LIKE';conf=.7;reason='few planar normal groups or dominant parallel surfaces'
 else:family='F_CURVED_OR_FREEFORM';conf=.45;reason='many normal groups; rotational/freeform ambiguity, not proof of nonrepresentability'
 return {'vertex_count':len(v),'face_count':len(m.faces),'connected_component_count':len(m.split(only_watertight=False)),
  'watertight':bool(m.is_watertight),'surface_area':float(m.area),'volume_if_valid':float(abs(m.volume)) if m.is_volume else None,
  'bbox_extents':m.extents.tolist(),'centroid':m.centroid.tolist(),'principal_axes':vh.tolist(),'principal_extents':ext.tolist(),
  'aspect_ratios':(ext/max(ext[0],1e-12)).tolist(),'boundary_edges':int(np.sum(np.bincount(m.edges_unique_inverse)==1)),
  'planar':planar,'plane_residual_max':float(np.max(np.abs(local[:,2]))),'normal_group_n':len(groups),
  'cad_family':family,'family_confidence':conf,'family_classification_method':'deterministic PCA + connectivity + area-weighted surface normals; heuristic, not GT','family_evidence':reason}
def complexity(code):
 calls=collections.Counter(n.func.attr for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute))
 mapping={'extrude_count':'extrude','revolve_count':'revolve','boolean_union_count':'union','boolean_cut_count':'cut','boolean_intersect_count':'intersect','fillet_count':'fillet','chamfer_count':'chamfer','circle_count':'circle','polygon_count':'polyline','workplane_count':'Workplane'}
 r={k:calls[v] for k,v in mapping.items()};r.update(primitive_types=[k for k in ['box','sphere','circle','polyline','revolve','loft'] if calls[k]],primitive_count=sum(calls[k] for k in ['box','sphere','extrude','revolve','loft']),sketch_count=calls['circle']+calls['polyline'])
 return r
rows=[];meshmap={};original={}
for line in (OLD/'manifests/cases.jsonl').read_text().splitlines():
 r=json.loads(line);cid=r['case_id'];original[cid]=r;m=trimesh.load(OLD/'cases'/cid/'normalized/normalized_mesh.ply',force='mesh',process=True);meshmap[cid]=m
 d=describe(m);d.update(case_id=cid,status=r['filter_decision'],v1_metrics=r['geometry_metrics'],selected_kind=r['attempts'][r['selected_attempt_index']]['kind'] if 'selected_attempt_index' in r else None)
 if r.get('cad_program_path'):
  d.update(complexity(Path(r['cad_program_path']).read_text()));cad=trimesh.load(r['cad_mesh_path'],force='mesh',process=True)
  bc=float(np.linalg.norm(m.bounds.mean(0)-cad.bounds.mean(0)));be=float(np.max(abs(m.extents-cad.extents)))
  d.update(bbox_center_recomputed=bc,bbox_extent_recomputed=be,bbox_error_recomputed=max(bc,be),bbox_saved_difference=abs(max(bc,be)-r['geometry_metrics']['bbox_error']),cad_area=float(cad.area),cad_centroid=cad.centroid.tolist(),cad_pca_thickness=describe(cad)['principal_extents'][2],cad_component_count=len(cad.split(only_watertight=False)))
 else:d.update(complexity('result = 0'))
 reasons=[];evidence=[]
 if r['filter_decision']=='STRICT_ACCEPT':primary='NONE'
 elif r['filter_decision']=='REJECT':primary='UNSUPPORTED_ZERO_THICKNESS';evidence=['PCA rank 2; V1 forbids zero-thickness solids'];d['unsupported_assessment']='B: CadQuery can model a planar sketch/sheet; V1 solid planner lacks an explicit thin-sheet thickness policy. Thickness is unobserved, not evidence of damage.'
 elif d['planar']:
  primary='WRONG_CAD_FAMILY';reasons=['WRONG_EXTRUSION_DEPTH'];evidence=['Source PCA thickness <1e-5 of major extent','Solid extrusion fills material unsupported by the observed planar surface']
 elif d['connected_component_count']>d.get('cad_component_count',0) and d['connected_component_count']>1:
  primary='MISSING_BOOLEAN_STRUCTURE';reasons=['WRONG_PROFILE'];evidence=['Source has '+str(d['connected_component_count'])+' disconnected surfaces; CAD has '+str(d['cad_component_count']),'Global extrusion bridges source component gaps; actual original Boolean history is unknown']
 elif d['normal_group_n']<=6 and not d['watertight']:
  primary='WRONG_PROFILE';reasons=['MISSING_BOOLEAN_STRUCTURE'];evidence=['Few planar regions with open boundaries','Projected silhouette extrusion discards changing/open section topology; specific missing design operations are unproven']
 elif d['selected_kind'] in ['oriented_box','cylinder']:
  primary='WRONG_PRIMITIVE_TYPE';evidence=['Selected bounding primitive; source has '+str(d['normal_group_n'])+' unoriented normal groups']
 elif d['v1_metrics'].get('bbox_error',0)>.03:
  primary='WRONG_MAJOR_DIMENSIONS';evidence=['Recomputed CAD bbox differs','Profile simplification or axis choice loses an extreme']
 else:primary='WRONG_PROFILE';evidence=['Extrusion restricts section shape to be constant along one axis','Normals/connectivity indicate structure not retained by the selected silhouette']
 d.update(primary_failure=primary,secondary_failures=reasons,diagnostic_evidence=evidence,diagnostic_confidence=.9 if d['planar'] else .6)
 rows.append(d)
write(D/'tables/descriptors_and_diagnosis.json',rows)
flat=[{k:v for k,v in r.items() if k not in ['v1_metrics']} for r in rows];csvout(D/'tables/geometry_and_cad_descriptors.csv',flat)
counts=collections.Counter(r['primary_failure'] for r in rows if r['status']=='RELAXED_ANALYSIS_ONLY')
csvout(D/'tables/failure_mode_breakdown.csv',[{'primary_failure':k,'count':v,'denominator':92} for k,v in counts.items()])
families=collections.Counter(r['cad_family'] for r in rows);csvout(D/'tables/family_breakdown.csv',[{'family':k,'count':v,'method':'heuristic source classification'} for k,v in families.items()])
taxonomy=['WRONG_CAD_FAMILY','WRONG_PRIMITIVE_TYPE','WRONG_MAJOR_DIMENSIONS','WRONG_PROFILE','WRONG_EXTRUSION_DEPTH','WRONG_REVOLVE_AXIS','MISSING_HOLE','MISSING_CUT','MISSING_PROTRUSION','MISSING_BOOLEAN_STRUCTURE','WRONG_PART_ORIENTATION','WRONG_POSITION','PARAMETER_FIT_FAILURE','BOOLEAN_EXECUTION_APPROXIMATION','FREEFORM_NOT_REPRESENTABLE','UNKNOWN_GEOMETRY_MISMATCH']
write(D/'configs/failure_taxonomy.json',{'labels':taxonomy,'policy':'Assign only when supported by geometry; unused labels have zero confirmed cases. Multi-label secondary causes are hypotheses, not original design history.'})
rel=[r for r in rows if r['status']=='RELAXED_ANALYSIS_ONLY'];selected=[];why={}
def add(rs,reason):
 for r in rs:
  if r['case_id'] not in selected and len(selected)<20:selected.append(r['case_id']);why[r['case_id']]=reason
add(sorted(rel,key=lambda r:r['v1_metrics']['iou'])[:3],'worst IoU')
add(sorted(rel,key=lambda r:-r['v1_metrics']['normalized_chamfer'])[:3],'worst NCD')
add(sorted(rel,key=lambda r:-r['v1_metrics']['iou'])[:4],'best relaxed / near threshold')
ordered=sorted(rel,key=lambda r:r['v1_metrics']['iou']);add(ordered[len(ordered)//2-2:len(ordered)//2+2],'median mismatch')
for attr in ['cad_family','primary_failure','selected_kind','primitive_count']:
 for key in sorted({str(r[attr]) for r in rel}):add([next(r for r in rel if str(r[attr])==key)],'coverage '+attr+'='+key)
add(sorted(rel,key=lambda r:r['case_id']),'deterministic coverage fill')
selected=[r['case_id'] for r in rows if r['status']=='STRICT_ACCEPT']+selected+[r['case_id'] for r in rows if r['status']=='REJECT']
write(D/'visualizations/selection.json',{'cases':selected,'relaxed_selection_reasons':why,'camera':{'elevation':22,'azimuth':-55},'same_scale_frame':True})
def draw(ax,m,color,alpha=1):
 poly=Poly3DCollection(m.triangles,facecolor=color,edgecolor='#334155' if len(m.faces)<200 else 'none',linewidth=.2,alpha=alpha);ax.add_collection3d(poly)
for cid in selected:
 r=next(x for x in rows if x['case_id']==cid);src=meshmap[cid];old=original[cid];cad=trimesh.load(old['cad_mesh_path'],force='mesh',process=True) if old.get('cad_mesh_path') else None
 fig=plt.figure(figsize=(15,4));axes=[fig.add_subplot(1,4,i+1,projection='3d') for i in range(4)]
 draw(axes[0],src,'#60a5fa')
 if cad is not None:
  draw(axes[1],cad,'#fb923c');draw(axes[2],src,'#60a5fa',.5);draw(axes[2],cad,'#fb923c',.35)
  a,_=trimesh.sample.sample_surface(src,3000,seed=20261006);b,_=trimesh.sample.sample_surface(cad,3000,seed=20261007);dist=cKDTree(b).query(a)[0];axes[3].scatter(*a.T,c=dist,cmap='magma',vmin=0,vmax=.15,s=1)
 else:
  draw(axes[2],src,'#60a5fa');axes[1].text(0,0,0,'NO CAD');axes[3].text(0,0,0,'Unsupported in V1')
 lo=src.bounds[0] if cad is None else np.minimum(src.bounds[0],cad.bounds[0]);hi=src.bounds[1] if cad is None else np.maximum(src.bounds[1],cad.bounds[1]);c=(lo+hi)/2;rad=max(hi-lo)*.58
 for ax,title in zip(axes,['Source','V1 CAD','Overlay','Source-to-CAD sampled distance']):
  ax.set(xlim=(c[0]-rad,c[0]+rad),ylim=(c[1]-rad,c[1]+rad),zlim=(c[2]-rad,c[2]+rad),title=title);ax.set_box_aspect((1,1,1));ax.view_init(22,-55);ax.set_axis_off()
 fig.suptitle(cid+' | '+r['status']+' | '+r['primary_failure'],fontsize=11);fig.tight_layout();fig.savefig(D/'visualizations'/(cid+'.png'),dpi=130);plt.close(fig)
(D/'visualizations/index.html').write_text('<meta charset="utf-8"><h1>V1 source / CAD / overlay / sampled distance</h1><p>Same camera and scale within each comparison. Distance colors: 0 to 0.15 canonical units. Heuristic causes, not design ground truth.</p>'+''.join(f'<h2>{c}</h2><img style="width:100%" src="{c}.png">' for c in selected))
summary={'source_planar_n':sum(r['planar'] for r in rows),'source_face_counts':dict(collections.Counter(r['face_count'] for r in rows)),
 'bbox_bug_found':any(r.get('bbox_saved_difference',0)>1e-12 for r in rows),'bbox_exact_zero_n':sum(r.get('bbox_error_recomputed')==0 for r in rows),
 'families':dict(families),'failure_modes':dict(counts),'visualized_n':len(selected),'selected_kind_counts':dict(collections.Counter(r['selected_kind'] for r in rows))}
write(D/'reports/diagnosis_summary.json',summary);print(json.dumps(summary),flush=True)
