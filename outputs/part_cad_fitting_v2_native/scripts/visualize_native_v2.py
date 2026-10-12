from v2_common import *
import sys,html
sys.path.insert(0,str(O.parent/'cad_render_v4/scripts'))
from cad_render_utils import *
from report_native_v2 import final_results
import trimesh
from concurrent.futures import ProcessPoolExecutor
def common_span(source,old,new,center,R):
 corners=[source.bounding_box.vertices]
 for path in [old,new]:
  b=cq.importers.importStep(str(path)).val().BoundingBox();corners.append(np.array([[x,y,z] for x in [b.xmin,b.xmax] for y in [b.ymin,b.ymax] for z in [b.zmin,b.zmax]]))
 q=(np.vstack(corners)-center)@R
 return float(2*np.max(np.abs(q[:,:2])))
def run(item):
 group,row=item;d=O/'cases'/row['case_id'];source=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);old=Path(row['v1_dir'])/'cad/cad.step';new=d/'cad/cad.step';R=camera_basis();center=source.bounds.mean(0);span=common_span(source,old,new,center,R);sourceactor=actor(polydata(source.vertices,source.faces,source.vertex_normals),(.27,.55,.80));src=render([sourceactor],center,span,R,title='Source part mesh',subtitle=row['case_id'],size=650);olddata,_,_=step_data(old,np.eye(4),span*.00025,.025);newdata,_,_=step_data(new,np.eye(4),span*.00025,.025);oldactor=actor(olddata);newactor=actor(newdata);v1=read(d/'source/v1_result.json')['metrics'];v2=row['metrics'];oldim=render([oldactor],center,span,R,title='V1 native CAD',subtitle=f"{row['v1_status']} | IoU {v1['iou']:.4f} | NCD {v1['normalized_chamfer']:.4f}",size=650);newim=render([newactor],center,span,R,title='V2 native CAD',subtitle=f"{row['status']} | IoU {v2['iou']:.4f} | NCD {v2['normalized_chamfer']:.4f}",size=650);overlay=render([actor(polydata(source.vertices,source.faces,source.vertex_normals),(.18,.51,.87),.45),actor(newdata,(.93,.44,.23),.55)],center,span,R,title='Source / V2 overlay',subtitle='Blue source | Orange CAD | same coordinates',size=650);im=Image.new('RGB',(2600,710),'#f7f9fc')
 for i,p in enumerate([src,oldim,newim,overlay]):im.paste(p,(i*650,60))
 draw=ImageDraw.Draw(im);draw.text((24,15),f"{group} | {row['case_id']} | {row['fix_type']}",font=font(24),fill='#182536');name=group+'_'+row['case_id'].replace('/','_')+'.png';path=O/'visualizations'/name;path.parent.mkdir(exist_ok=True);im.save(path);return {'group':group,'case_id':row['case_id'],'image':name,'source_sha256':sha(d/'source/part_local.ply'),'v1_step_sha256':sha(old),'v2_step_sha256':sha(new),'same_camera_scale_coordinates':True,'v1_status':row['v1_status'],'v2_status':row['status'],'fitting_performed':row['fitting_performed']}
if __name__=='__main__':
 rows=final_results();rescues=[r for r in rows if r['v1_status']=='NEAR_PASS' and r['status']=='STRICT_ACCEPT'];rescues=sorted(rescues,key=lambda r:(not r['new_strict_vs_baseline'],r['case_id']));failed=sorted([r for r in rows if r['v1_status']=='NEAR_PASS' and r['status']!='STRICT_ACCEPT'],key=lambda r:-r['metrics']['iou']);rejected=sorted([r for r in rows if r['v1_status']=='REJECT'],key=lambda r:(r['status']!='STRICT_ACCEPT',r['metrics']['iou']))
 items=[('near_to_strict',r) for r in rescues[:10]]+[('near_still_failed',r) for r in failed[:10]]+[('reject_representative',r) for r in rejected[:10]]
 with ProcessPoolExecutor(max_workers=3) as pool:manifest=list(pool.map(run,items))
 dump(O/'visualizations/manifest.json',manifest);page='<meta charset="utf-8"><title>Native CAD fitting comparison</title><style>body{max-width:1900px;margin:30px auto;font:17px system-ui}img{width:100%}</style><h1>Native CAD geometry comparison</h1><p>Source / original V1 / new selected V2 / overlay. Same camera, scale and coordinates. Near-to-Strict includes historical baseline rescues; newly rescued cases are prioritized and separately counted in the report. Smooth display does not change metrics.</p>'
 for r in manifest:page+=f'<h2>{r["group"]} — {r["case_id"]}</h2><img src="{r["image"]}">'
 (O/'visualizations/index.html').write_text(page);print('GEOMETRY_VISUALS',len(manifest),flush=True)
