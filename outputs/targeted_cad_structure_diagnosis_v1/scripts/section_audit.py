from structure_common import *
import trimesh
from shapely.geometry import Polygon
from concurrent.futures import ProcessPoolExecutor,as_completed
def section_stats(mesh,B):
 q=mesh.vertices@B;low=q.min(0);high=q.max(0);out=[]
 for frac in [.2,.35,.5,.65,.8]:
  z=low[2]+frac*(high[2]-low[2]);section=mesh.section(plane_origin=B@np.array([0,0,z]),plane_normal=B[:,2]);loops=[]
  if section is not None:
   for points in section.discrete:
    if len(points)<4 or np.linalg.norm(points[0]-points[-1])>1e-5:continue
    uv=np.asarray(points)@B[:,:2];poly=Polygon(uv)
    if not poly.is_valid:poly=poly.buffer(0)
    if poly.is_empty or poly.geom_type!='Polygon' or poly.area<1e-7:continue
    center=np.array(poly.centroid.coords[0]);rad=np.linalg.norm(uv-center,axis=1);circle_res=float(np.std(rad)/max(np.mean(rad),1e-10));rect=poly.minimum_rotated_rectangle;compact=float(poly.area/max(rect.area,1e-10));loops.append({'polygon':poly,'area':poly.area,'center':center.tolist(),'circle_relative_residual':circle_res,'rectangle_fill':compact})
  loops.sort(key=lambda p:-p['area']);inside=[]
  for i,p in enumerate(loops):
   depth=sum(x['polygon'].contains(p['polygon'].representative_point()) for x in loops[:i]);p['hole']=bool(depth%2);inside.append(p)
  outer=[p for p in inside if not p['hole']];holes=[p for p in inside if p['hole']];out.append({'fraction':frac,'outer_n':len(outer),'hole_n':len(holes),'area':sum(p['area'] for p in outer)-sum(p['area'] for p in holes),'outer_circle_residual':max((p['circle_relative_residual'] for p in outer),default=None),'outer_rectangle_fill':min((p['rectangle_fill'] for p in outer),default=None),'hole_circle_residuals':[p['circle_relative_residual'] for p in holes],'hole_areas':[p['area'] for p in holes]})
 return out
def run(row):
 dest=O/'audits'/row['case_id'];p=dest/'section_audit.json'
 if p.exists():return read(p)
 old=V/'cases'/row['case_id'];source=trimesh.load(old/'source/part_local.ply',force='mesh',process=True);cad=trimesh.load(old/'cad/cad_mesh.ply',force='mesh',process=True);code=(old/'cad/cad.py').read_text();B=np.eye(3)
 for n in ast.walk(ast.parse(code)):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Plane':
   kw={k.arg:ast.literal_eval(k.value) for k in n.keywords};x=np.array(kw['xDir']);z=np.array(kw['normal']);x/=np.linalg.norm(x);z/=np.linalg.norm(z);B=np.column_stack([x,np.cross(z,x),z]);break
 s=section_stats(source,B);c=section_stats(cad,B);valid=[x for x in s if x['outer_n']];areas=[x['area'] for x in valid];stable=bool(len(valid)>=4 and np.std(areas)/max(np.mean(areas),1e-12)<.08);extra_hole=sum(max(0,x['hole_n']-y['hole_n']) for x,y in zip(s,c));circleholes=sum(v<.12 for x in s for v in x['hole_circle_residuals']);rounds=sum(x['outer_circle_residual'] is not None and x['outer_circle_residual']<.08 for x in s);boxes=sum(x['outer_rectangle_fill'] is not None and x['outer_rectangle_fill']>.94 for x in s)
 r={'case_id':row['case_id'],'basis':B.tolist(),'source_sections':s,'cad_sections':c,'closed_source_section_n':len(valid),'stable_section_area':stable,'source_extra_hole_section_count':extra_hole,'circle_hole_section_count':circleholes,'circular_outer_section_n':rounds,'rectangular_outer_section_n':boxes,'section_comparison_note':'Each mesh sliced at own matching fractional axial positions; topology evidence only, no refit or changed transform. Open contours are not silently closed.'};dump(p,r);return r
if __name__=='__main__':
 rows=[r for r in read(O/'manifests/all_parts.json') if r['family'] in ['A_SIMPLE_PRIMITIVE','D_EXTRUDE_WITH_CUTS']];errors=[]
 with ProcessPoolExecutor(max_workers=6) as pool:
  fs={pool.submit(run,r):r['case_id'] for r in rows}
  for f in as_completed(fs):
   try:f.result()
   except Exception as e:errors.append({'case_id':fs[f],'error':str(e)})
 dump(O/'logs/section_errors.json',errors);print('SECTION_AUDIT',len(rows),'ERRORS',errors,flush=True)
