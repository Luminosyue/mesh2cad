from v2_common import *
import trimesh,sys
from PIL import Image,ImageDraw
rows=read(O/'tables'/('near_pass_rescue.json' if '--near-preview' in sys.argv else 'part_v1_v2_comparison.json'));groups={'near_rescue':[r for r in rows if r['V1_status']=='NEAR_PASS' and r['V2_status']=='STRICT_ACCEPT'],'near_failure':[r for r in rows if r['V1_status']=='NEAR_PASS' and r['V2_status']!='STRICT_ACCEPT'],'reject_examples':[r for r in rows if r['V1_status']=='REJECT']}
def choose(group,limit=10):
 rs=sorted(group,key=lambda r:(r['V2_status']!='STRICT_ACCEPT',-r['delta_IoU']));picked=[];seen=set()
 for r in rs:
  key=(r['object_id'],r['fix_type'],r['V2_status'])
  if key not in seen:picked.append(r);seen.add(key)
  if len(picked)==limit:return picked
 for r in rs:
  if r not in picked:picked.append(r)
  if len(picked)==limit:break
 return picked
def panel(p,color,title,center,view,span):
 im=Image.new('RGB',(512,512),'white');q=(p-center)@view;xy=q[:,:2]*(512*.47/span)+256;xy[:,1]=512-xy[:,1];pix=np.array(im)
 for i in np.argsort(q[:,2]):
  x,y=np.rint(xy[i]).astype(int)
  if 2<x<510 and 45<y<510:pix[y-1:y+2,x-1:x+2]=color[i] if np.ndim(color)==2 else color
 im=Image.fromarray(pix);ImageDraw.Draw(im).text((10,10),title,fill='black');return im
records=[]
for group,rs in groups.items():
 selected=choose(rs)
 if group=='reject_examples':
  selected=choose([r for r in rs if r['V2_status']!='REJECT'],5)+choose([r for r in rs if r['V2_status']=='REJECT'],5)
  selected+=(choose([r for r in rs if r not in selected],10-len(selected)) if len(selected)<10 else [])
 elif group=='near_failure':
  regressions=choose([r for r in rs if r['V2_status']=='REJECT'],2);selected=regressions+choose([r for r in rs if r not in regressions],10-len(regressions))
 for row in selected:
  d=O/'cases'/row['case_id'];r=read(d/'result.json');src=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);v1=trimesh.load(Path(r['v1_dir'])/'cad/cad_mesh_from_reloaded_step.ply',force='mesh',process=True);v2=trimesh.load(d/'cad/cad_mesh.ply',force='mesh',process=True);pts=[]
  for m,seed in [(src,r['seed']),(v1,r['seed']+1),(v2,r['seed']+1)]:pts.append(trimesh.sample.sample_surface(m,20000,seed=seed)[0])
  _,_,vh=np.linalg.svd(pts[0]-pts[0].mean(0),full_matrices=False);ang=.35;R=np.array([[np.cos(ang),-np.sin(ang),0],[np.sin(ang),np.cos(ang),0],[0,0,1]]);view=vh.T@R;center=src.bounds.mean(0);span=max(np.ptp((pts[0]-center)@view,axis=0));colors=[[70,140,220],[230,125,40],[50,175,105]];im=Image.new('RGB',(1536,512),'white')
  titles=[row['case_id']+' | SOURCE',f"V1 {r['v1_status']} IoU={row['V1_IoU']:.3f} NCD={row['V1_NCD']:.4f}",f"V2 {r['v2_status']} IoU={row['V2_IoU']:.3f} NCD={row['V2_NCD']:.4f}"]
  for i in range(3):im.paste(panel(pts[i],colors[i],titles[i],center,view,span),(i*512,0))
  name=row['case_id'].replace('/','__');im.save(d/'visualizations/comparison.png');im.save(O/'visualizations'/(name+'.png'));overlay=Image.new('RGB',(1024,512),'white')
  for i in [1,2]:overlay.paste(panel(np.vstack([pts[0],pts[i]]),np.vstack([np.tile(colors[0],(len(pts[0]),1)),np.tile(colors[i],(len(pts[i]),1))]),'Source blue / '+('V1 orange' if i==1 else 'V2 green'),center,view,span),((i-1)*512,0))
  overlay.save(O/'visualizations'/(name+'_overlay.png'));dump(d/'visualizations/view.json',{'view_matrix':view.tolist(),'center':center.tolist(),'shared_span':float(span),'source_sample_seed':r['seed'],'cad_sample_seed':r['seed']+1});records.append({'group':group,'case_id':row['case_id'],'image':name+'.png','overlay':name+'_overlay.png'})
counts={k:sum(r['group']==k for r in records) for k in groups};dump(O/'visualizations/manifest.json',{'counts':counts,'availability_note':'If fewer than 10 rescues exist, show every actual rescue and explicitly report shortfall; never fabricate examples.','records':records});(O/'visualizations/index.html').write_text('<meta charset="utf-8"><h1>Part CAD V1 vs V2</h1><p>'+json.dumps(counts)+'</p>'+''.join(f'<h2>{r["group"]}: {r["case_id"]}</h2><img style="width:100%;max-width:1536px" src="{r["image"]}"><br><a href="{r["overlay"]}">Source overlays</a>' for r in records));print(json.dumps(counts))
