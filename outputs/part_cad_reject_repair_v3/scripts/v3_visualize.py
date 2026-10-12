from v2_common import *
import trimesh
from PIL import Image,ImageDraw
rows=read(O/'tables/part_v2_v3_comparison.json');manifest={r['case_id']:r for r in read(O/'manifests/cases.json')}
recovered=sorted([r for r in rows if not r['preserved'] and r['V3_status']!='REJECT'],key=lambda r:(r['V3_status']!='STRICT_ACCEPT',r['score_delta']))
remaining=sorted([r for r in rows if not r['preserved'] and r['V3_status']=='REJECT'],key=lambda r:r['score_delta'])
groups={'recovered':recovered[:10],'remaining_reject':remaining[:5]+sorted([r for r in remaining if r not in remaining[:5]],key=lambda r:-r['V3_NCD'])[:5]}

def panel(points,colors,title,view,center,span):
 q=(points-center)@view;xy=q[:,:2]*(512*.75/span)+256;xy[:,1]=512-xy[:,1];pixels=np.full((512,512,3),255,dtype=np.uint8)
 for i in np.argsort(q[:,2]):
  x,y=np.rint(xy[i]).astype(int)
  if 2<x<510 and 40<y<510:pixels[y-1:y+2,x-1:x+2]=colors[i]
 im=Image.fromarray(pixels);ImageDraw.Draw(im).text((8,8),title,fill='black');return im

records=[]
for group,items in groups.items():
 for row in items:
  d=O/'cases'/row['case_id'];seed=manifest[row['case_id']]['seed'];meshes=[trimesh.load(d/p,force='mesh',process=True) for p in ['source/part_local.ply','baseline/cad_mesh.ply','cad/cad_mesh.ply']];points=[];normals=[]
  for i,m in enumerate(meshes):
   pts,ids=trimesh.sample.sample_surface(m,20000,seed=seed if i==0 else seed+1);points.append(pts);normals.append(m.face_normals[ids])
  _,_,vh=np.linalg.svd(points[0]-points[0].mean(0),full_matrices=False);a=.35;b=.40;Rz=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]);Rx=np.array([[1,0,0],[0,np.cos(b),-np.sin(b)],[0,np.sin(b),np.cos(b)]]);view=vh.T@Rz@Rx;center=meshes[0].bounds.mean(0);span=float(max(np.ptp((points[0]-center)@view,axis=0)));basecolors=[[60,130,220],[230,130,45],[40,170,95]];light=np.array([.3,.4,.866]);colors=[np.clip(np.asarray(basecolors[i])[None,:]*(.35+.65*np.abs(normals[i]@view@light))[:,None],0,255).astype(np.uint8) for i in range(3)]
  titles=[row['case_id']+' SOURCE',f"V2 {row['V2_status']} IoU={row['V2_IoU']:.3f} NCD={row['V2_NCD']:.4f}",f"V3 {row['V3_status']} IoU={row['V3_IoU']:.3f} NCD={row['V3_NCD']:.4f}"]
  im=Image.new('RGB',(1536,512),'white')
  for i in range(3):im.paste(panel(points[i],colors[i],titles[i],view,center,span),(512*i,0))
  name=row['case_id'].replace('/','__');im.save(O/'visualizations'/(name+'.png'));im.save(d/'visualizations/comparison.png');overlay=Image.new('RGB',(1024,512),'white')
  for i in [1,2]:overlay.paste(panel(np.vstack([points[0],points[i]]),np.vstack([colors[0],colors[i]]),'Source blue / '+('V2 orange' if i==1 else 'V3 green'),view,center,span),((i-1)*512,0))
  overlay.save(O/'visualizations'/(name+'_overlay.png'));dump(d/'visualizations/view.json',{'view':view.tolist(),'center':center.tolist(),'span':span,'same_camera_scale':True,'source_seed':seed,'cad_seed':seed+1});records.append({'group':group,'case_id':row['case_id'],'image':name+'.png','overlay':name+'_overlay.png'})
dump(O/'visualizations/manifest.json',{'counts':{k:len(v) for k,v in groups.items()},'selection':'All strict rescues first, then Near rescues; remaining rejects include score improvements and large residuals. At most ten per group.','records':records})
(O/'visualizations/index.html').write_text('<meta charset="utf-8"><h1>V2 to V3 Reject Repair</h1><p>Shared camera and scale. Blue source, orange V2, green V3. Numerical classification does not certify all topology.</p>'+''.join(f'<h2>{r["group"]}: {r["case_id"]}</h2><img style="width:100%;max-width:1536px" src="{r["image"]}"><br><a href="{r["overlay"]}">Overlay</a>' for r in records));print('VISUALIZED',len(records))
